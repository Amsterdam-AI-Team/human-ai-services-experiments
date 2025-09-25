from __future__ import annotations
from dotenv import load_dotenv
load_dotenv()

import whisper
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware
from fastapi import (FastAPI, File,
                     UploadFile, Form,
                     HTTPException, Request, Query)
from uuid import uuid4

import numpy as np
from models import (build_step_model, ChatResponse,
                    AnalyzeResponse, YapAccumResponse,
                    YapStartRequest, YapStartResponse,
                    YapNextResponse, FeedbackRequest)

from intents import INTENTS
from templates import (make_chain, _yap_generate)
from i18n import (get_intents, get_translation, normalize_language_code, 
                  extract_language_from_request)

import os

import tempfile
import asyncio
import asyncpg
import re
import logging
import requests
from langdetect import detect

import mimetypes
import subprocess
import uuid
from pathlib import Path

if "AZURE_OPENAI_API_KEY" not in os.environ:
    print("❌  Missing Azure OpenAI API key")

logging.basicConfig(level=logging.INFO)
logging.info("Environment variables loaded:")
for var in [
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_KEY",
    "OPENAI_API_VERSION",
    "AZURE_OPENAI_DEPLOYMENT_NAME",
    "WHISPER_MODEL_NAME",
    "DATABASE_URL",
    "TRANSCRIPTION_AZ_ENDPOINT",
    "TRANSCRIPTION_AZ_MODEL",
    "TRANSCRIPTION_API_KEY"
]:
    logging.info(f"{var}={os.getenv(var)}")


# ---------------------------------------------------------------------------
# Initialise local Whisper model (loaded once at startup)
# ---------------------------------------------------------------------------

# base / small / medium / large / etc.
_WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL_NAME", "base")
_whisper_model = whisper.load_model(_WHISPER_MODEL_NAME)

# cloud transcribe endpoint
_AZ_ENDPOINT = os.getenv("TRANSCRIPTION_AZ_ENDPOINT")
_AZ_MODEL = os.getenv("TRANSCRIPTION_AZ_MODEL")
_AZ_KEY = os.getenv("TRANSCRIPTION_API_KEY")


def _detect_language(text: str) -> str:
    """Lightweight n‑gram language ID (ISO‑639‑1)."""
    try:
        return detect(text)          # e.g. 'nl', 'en'
    except Exception:
        return "und"                 # undefined

def _transcribe(path: str, filename: str | None = None, content_type: str | None = None) -> str:
    # Attention: for demo purposes we return a predefined string
    return 'The neighborhood is 20 years old and we want to celebrate that. I was thinking of long tables with large bowls of food on them, bottles of wine, bottles of water. A little campfire next to it to warm up and maybe something fun for the children too.'
    return 'The neighborhood is 20 years old and we want to celebrate with a modest gathering. I was thinking of long tables with large bowls of food, premium champagne and artisanal spirits, craft beer tasting stations. A bonfire large enough to see from the highway, plus a petting zoo with exotic animals, a mechanical bull, and maybe a small fireworks display for the children.'
    """
    Always transcodes the incoming audio to MP3 (mono, 16 kHz) with ffmpeg,
    then sends that MP3 to the Azure endpoint using your existing headers/model.
    Falls back to local Whisper on any failure.
    """
    api_key = os.getenv("TRANSCRIPTION_API_KEY")
    if not api_key:
        raise RuntimeError("TRANSCRIPTION_API_KEY not set")

    # Prepare an MP3 temp file
    mp3_path = Path(tempfile.gettempdir()) / f"cast-{uuid.uuid4().hex}.mp3"
    ffmpeg_cmd = [
        "/usr/bin/ffmpeg", "-y",         # absolute path avoids PATH issues under systemd
        "-i", path,                      # source file (any format)
        "-ac", "1",                      # mono
        "-ar", "16000",                  # 16 kHz
        "-codec:a", "libmp3lame",
        "-b:a", "128k",
        str(mp3_path)
    ]

    try:
        # 1) ALWAYS transcode to MP3
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        send_path = str(mp3_path)
        send_name = "audio.mp3"
        send_ct = "audio/mpeg"

        logging.info(
            "Transcribe → sending to Azure (forced MP3): name=%s ct=%s size=%d bytes",
            send_name, send_ct, os.path.getsize(send_path)
        )

        # 2) Send MP3 to Azure with your existing headers/model
        with open(send_path, "rb") as f:
            files = {
                "file": (send_name, f, send_ct),
                "model": (None, "gpt-4o-transcribe"),  # keep your current behavior
            }
            headers = {"Authorization": f"Bearer {api_key}"}

            r = requests.post(_AZ_ENDPOINT, files=files, headers=headers, timeout=120)

        try:
            r.raise_for_status()
        except requests.HTTPError:
            logging.error("Azure transcription HTTP %s: %s", r.status_code, r.text)
            raise

        text = r.json().get("text", "").strip()
        logging.info("Azure transcription succeeded – text length: %d", len(text))
        return text

    except Exception as e:
        logging.warning("Azure transcription failed (%s) – falling back to local Whisper", e)
        # If casting failed (e.g., ffmpeg missing), or Azure rejected, use original file locally
        res = _whisper_model.transcribe(path)
        return res["text"].strip()

    finally:
        # Clean up the temp MP3 if it exists
        try:
            if mp3_path.exists():
                mp3_path.unlink()
        except Exception:
            pass

# ---------------------------------------------------------------------------
# FastAPI app config
# ---------------------------------------------------------------------------
app = FastAPI(title="Whisper‑Intent Matcher (local Whisper + local embeddings)", version="4.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# naive in-memory store; swap with redis client.get/set
SESSIONS: dict[str, dict] = {}
YAP_SESSIONS: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# Local embedding model (DL ~430 MB, loads once)
# ---------------------------------------------------------------------------

_EMBED_MODEL_NAME = 'sentence-transformers/distiluse-base-multilingual-cased-v1'
_embedder = SentenceTransformer(_EMBED_MODEL_NAME)


def _embed(text: str) -> np.ndarray:
    """Return L2‑normalised embedding for *text* using RobBERT sentence transformers."""
    vec = _embedder.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return vec  # unit‑norm thanks to normalise=True


# Pre‑compute intent embeddings once at startup
_INTENT_EMBS = np.vstack([_embed(obj["intent"]) for obj in INTENTS])

raw_dsn = os.getenv("DATABASE_URL", "postgresql://myuser:secret@localhost:5432/mydb")
# strip any dialect (e.g. '+asyncpg', '+psycopg')
DATABASE_URL = re.sub(r"\+[^:]+://", "://", raw_dsn, count=1)


# ensure DB tables exist
@app.on_event("startup")
async def _init_db():
    app.state.pool = await asyncpg.create_pool(DATABASE_URL)
    async with app.state.pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_log (
                id SERIAL PRIMARY KEY,
                session_id UUID NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                ts TIMESTAMPTZ DEFAULT now()
            );
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS yap_log (
                id SERIAL PRIMARY KEY,
                session_id UUID NOT NULL,
                speaker TEXT NOT NULL,
                content TEXT NOT NULL,
                ts TIMESTAMPTZ DEFAULT now()
            );
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback_log (
                id SERIAL PRIMARY KEY,
                session_id UUID,
                text TEXT NOT NULL,
                ts TIMESTAMPTZ DEFAULT now()
            );
            """
        )


# --------------------------------------------------------------
# helper ─ persist a single message
# --------------------------------------------------------------
async def _store_message(session_id: str, role: str, content: str):
    async with app.state.pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO chat_log (session_id, role, content) VALUES ($1,$2,$3)",
            session_id, role, content,
        )


async def _store_yap(session_id: str, speaker: str, content: str) -> None:
    async with app.state.pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO yap_log (session_id, speaker, content) VALUES ($1,$2,$3)",
            session_id, speaker, content,
        )
# ---------------------------------------------------------------------------
# /analyze route – core pipeline
# ---------------------------------------------------------------------------


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    file: UploadFile = File(...),
    top_k: int = Query(1, ge=1, description="Return the K best matches"),
    language: str = Query(None, description="Language code (nl, en, fr)"),
) -> AnalyzeResponse:
    """
    • Accepts a single *audio/* upload.
    • Optional query/form field **top_k** (default = 1) returns the K best‑scoring intents.
    """

    # Normalize language code
    lang_code = normalize_language_code(language)

    if not file.content_type.startswith("audio/"):
        error_msg = get_translation(lang_code, "responses.error_audio_required", 
                                  "Uploaded file must be audio/*")
        raise HTTPException(400, detail=error_msg)

    # 1️⃣ save upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:

        # 2️⃣ transcribe in background thread
        loop = asyncio.get_running_loop()
        #text = await loop.run_in_executor(None, _transcribe, tmp_path)
        
        text = await loop.run_in_executor(
        None,
        _transcribe,
        tmp_path,
        file.filename or "audio",      # <-- pass through
        (file.content_type or "").lower() or None  # <-- pass through
         )

        detected_language = _detect_language(text)

        # 3️⃣ similarity search
        q_vec = _embedder.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        sims = np.dot(_INTENT_EMBS, q_vec)     # shape = (n_intents,)

        # -- FIX ---------------------------------------------------------------
        k = max(1, min(top_k, len(sims))) 
        top_idx = sims.argsort()[-k:][::-1]    # laatste k indices, hoog → laag
        # ---------------------------------------------------------------------

        # Get localized intents using detected language instead of query parameter
        localized_intents = get_intents(detected_language)
        
        # Create a mapping from intentcode to localized intent
        intent_map = {intent["intentcode"]: intent for intent in localized_intents}
        
        matches = []
        for i in top_idx:
            original_intent = INTENTS[i]
            intentcode = original_intent["intentcode"]
            
            # Use localized version if available, otherwise fall back to original
            localized_intent = intent_map.get(intentcode, original_intent)
            
            matches.append({
                "intent": localized_intent, 
                "similarity": float(sims[i])
            })
        

        return AnalyzeResponse(transcript=text, matches=matches, language=detected_language)

    finally:
        os.remove(tmp_path)

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/ping")
async def ping():
    return {"status": "ok"}


# --------------------------------------------------------------
# /chat
# --------------------------------------------------------------

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: Request,               # ← now correctly typed
    intentcode: str | None = Form(None),
    message: str | None = Form(None),
    session_id: str | None = Form(None),
    language: str | None = Form(None),
    audio: UploadFile | None = File(None),
):
    if (
        request.headers.get("content-type", "").startswith("application/json")
        and audio is None
    ):
        body = await request.json()
        intentcode = body.get("intentcode")
        message = body.get("message")
        session_id = body.get("session_id")
        language = body.get("language")

    # Normalize language code
    lang_code = normalize_language_code(language)
    logging.info(f"Chat endpoint - original language: {language}, normalized: {lang_code}")
    
    if not intentcode:
        error_msg = get_translation(lang_code, "responses.error_intentcode_required", 
                                  "'intentcode' is required")
        raise HTTPException(422, detail=error_msg)

    # ── 2. Derive user_text ────────────────────────────────────────────────
    if audio is not None:
        ct = (audio.content_type or "").lower()
        if not (ct.startswith("audio") or ct == "application/octet-stream"):
            error_msg = get_translation(lang_code, "responses.error_audio_required", 
                                      "Uploaded file must be audio/*")
            raise HTTPException(400, detail=error_msg)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
            tmp.write(await audio.read())
            tmp_path = tmp.name

        try:
            loop = asyncio.get_running_loop()
            #user_text = await loop.run_in_executor(None, _transcribe, tmp_path)
            user_text = await loop.run_in_executor(
                None,
                _transcribe,
                tmp_path,
                audio.filename or "audio",
                (audio.content_type or "").lower() or None
            )
        finally:
            os.remove(tmp_path)
    else:
        user_text = message or ""
        if not user_text:
            error_msg = get_translation(lang_code, "responses.error_message_or_audio", 
                                      "Either 'message' field or audio file required")
            raise HTTPException(400, detail=error_msg)

    # ── 3. Session bookkeeping ────────────────────────────────────────────
    sid = session_id or str(uuid4())
    session = SESSIONS.setdefault(
        sid,
        {
            "history": [],
            "checklist": {},
            "intentcode": intentcode,
            "draft": "",
            "language": None,  # Track current language
        },
    )

    # ── 4. Build / reuse LangChain runnable ───────────────────────────────
    intent = next(i for i in INTENTS if i["intentcode"] == session["intentcode"])
    StepModel = build_step_model(intent, lang_code)

    # Recreate chain if language changed or doesn't exist
    if "chain" not in session or session.get("language") != lang_code:
        logging.info(f"Creating new chain for language: {lang_code} (previous: {session.get('language')})")
        session["chain"] = make_chain(StepModel, session, lang_code)  # async fn
        session["language"] = lang_code
    else:
        logging.info(f"Reusing existing chain for language: {lang_code}")

    step_obj: StepModel = await session["chain"](
        {"message": user_text, "history": session["history"]}
    )

    # ── 5. Persist & update session ───────────────────────────────────────
    session["history"].extend(
        [
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": step_obj.vragen or ""},
        ]
    )

    await _store_message(sid, "user", user_text)
    await _store_message(
        sid,
        "assistant",
        step_obj.vragen[0] if step_obj.vragen else get_translation(lang_code, "responses.all_steps_completed", "Alle stappen zijn afgerond!"),
    )

    # 5️⃣ checklist ---------------------------------------------------------
    session["checklist"] = step_obj.model_dump(exclude={"vragen"})
    finished = all(v for k, v in session["checklist"].items() if k != "draft")

    return ChatResponse(
        session_id=sid,
        reply=step_obj.vragen[0] if step_obj.vragen else get_translation(lang_code, "responses.all_steps_completed", "Alle stappen zijn afgerond!"),
        checklist=session["checklist"],
        finished=finished,
        user_text=user_text
    )


@app.post("/yap", response_model=YapAccumResponse)
async def yap_accumulate(
    request: Request,
    text: str | None = Form(None),
    audio: UploadFile | None = File(None),
    append: str | None = Form(None),
    language: str | None = Form(None),
):
    """
    Accumuleer audio naar tekst. Opties:
      • multipart met `audio` en optioneel bestaand `text`
      • multipart zonder audio maar met `append`
      • JSON: {"text": "...", "append": "..."}
    """
    # JSON fallback ----------------------------------------------------------
    if request.headers.get("content-type", "").startswith("application/json") and audio is None:
        body = await request.json()
        text = body.get("text", "")
        append = body.get("append", "")
        language = body.get("language")
    
    # Normalize language code
    lang_code = normalize_language_code(language)

    base_text = text or ""

    if audio is not None:
        ct = (audio.content_type or "").lower()
        if not (ct.startswith("audio") or ct == "application/octet-stream"):
            error_msg = get_translation(lang_code, "responses.error_audio_required", 
                                      "Uploaded file must be audio/*")
            raise HTTPException(400, detail=error_msg)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
            tmp.write(await audio.read())
            tmp_path = tmp.name

        try:
            loop = asyncio.get_running_loop()
            #new_text = await loop.run_in_executor(None, _transcribe, tmp_path)
            new_text = await loop.run_in_executor(
                None,
                _transcribe,
                tmp_path,
                audio.filename or "audio",
                (audio.content_type or "").lower() or None
            )
        finally:
            os.remove(tmp_path)

        if base_text:
            base_text = base_text.rstrip() + "\n" + new_text.strip()
        else:
            base_text = new_text.strip()

    elif append:
        if base_text:
            base_text = base_text.rstrip() + "\n" + append.strip()
        else:
            base_text = append.strip()
    else:
        # no audio, no append: just echo provided text
        base_text = base_text.strip()

    return YapAccumResponse(text=base_text, language=_detect_language(base_text))


# ---------------------------------------------------------------------------
#  /yap/start  – bewaar sessie direct in Postgres
# ---------------------------------------------------------------------------
@app.post("/yap/start", response_model=YapStartResponse)
async def yap_start(req: YapStartRequest):
    sid = str(uuid4())
    
    # Normalize language code
    lang_code = normalize_language_code(req.language)

    # 1. burger opent gesprek
    opening_template = get_translation(lang_code, "responses.yap_opening", 
                                     "Ik wil graag subsidie aanvragen voor een buurtfeest. Details:")
    opening = f"{opening_template}\n{req.text}"
    msgs = [{"speaker": "burger", "message": opening}]

    # 2. gemeente‑reactie
    gemeente_reply = await _yap_generate("gemeente", req.text, msgs, lang_code)
    msgs.append({"speaker": "gemeente", "message": gemeente_reply.message})

    # 3. cache in RAM  ✅ transcript back
    YAP_SESSIONS[sid] = {
        "transcript": req.text,      # <── added line
        "messages": msgs,
        "turn": 2,                   # volgende = burger
        "finished": False,
        "draft": None,
        "language": lang_code,        # <── added language
    }

    # 4. persist two rows + the transcript once
    await _store_yap(sid, "system", f"TRANSCRIPT::{req.text}")   # optional
    await _store_yap(sid, "burger", opening)
    await _store_yap(sid, "gemeente", gemeente_reply.message)

    # finished, draft = _yap_check_finished(msgs)
    # if finished:
    #     YAP_SESSIONS[sid]["finished"] = True
    #     YAP_SESSIONS[sid]["draft"] = draft

    return YapStartResponse(
        yap_session_id=sid,
        messages=msgs
    )


@app.post("/yap/next", response_model=YapNextResponse)
async def yap_next(
    yap_session_id: str = Query(..., description="ID from /yap/start"),
    language: str = Query(None, description="Language code (nl, en, fr)"),
):
    lang_code = normalize_language_code(language)
    
    if yap_session_id not in YAP_SESSIONS:
        error_msg = get_translation(lang_code, "responses.error_unknown_session", 
                                  "Unknown yap_session_id")
        raise HTTPException(404, detail=error_msg)

    sess = YAP_SESSIONS[yap_session_id]

    if sess["finished"]:
        # Nothing more to say; just echo final state
        last = sess["messages"][-1]
        return YapNextResponse(
            yap_session_id=yap_session_id,
            messages=sess["messages"],
            speaker=last["speaker"],
            message=last["message"],
            finished=True,
            draft=sess["draft"],
        )

    # Whose turn?
    last_speaker = sess["messages"][-1]["speaker"]
    role = "burger" if last_speaker == "gemeente" else "gemeente"

    # structured output (BurgerTurn of GemeenteTurn)
    # Use stored language or fallback to query parameter
    session_lang = sess.get("language", lang_code)
    step_obj = await _yap_generate(role, sess["transcript"], sess["messages"], session_lang)

    # 1.  sla de boodschap op
    sess["messages"].append({"speaker": role, "message": step_obj.message})

    # 2.  update status – alleen de gemeente mag finished/draft zetten
    if role == "gemeente":
        sess["finished"] = bool(step_obj.finished)
        sess["draft"] = step_obj.draft

    return YapNextResponse(
        yap_session_id=yap_session_id,
        messages=sess["messages"],
        speaker=role,
        message=step_obj.message,
        finished=sess["finished"],
        draft=sess["draft"],
    )


@app.post("/feedback")
async def submit_feedback(
    payload: FeedbackRequest
):
    """
    Store feedback from UI with optional session_id.
    """
    async with app.state.pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO feedback_log (session_id, text)
            VALUES ($1, $2)
            """,
            payload.session_id, payload.feedback
        )
    return {"status": "ok"}
