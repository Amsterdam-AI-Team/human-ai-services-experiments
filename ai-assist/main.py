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
                    YapNextResponse)

from intents import INTENTS
from templates import (make_chain, _yap_check_finished,
                       _yap_generate)

import os

import tempfile
import asyncio
import asyncpg
import re
import logging

if "AZURE_OPENAI_API_KEY" not in os.environ:
    print("❌  Missing Azure OpenAI API key")

for var in [
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_KEY",
    "OPENAI_API_VERSION",
    "AZURE_OPENAI_DEPLOYMENT_NAME",
    "WHISPER_MODEL_NAME",
    "DATABASE_URL",
]:
    print(f"{var}={os.getenv(var)}")


# ---------------------------------------------------------------------------
# Initialise local Whisper model (loaded once at startup)
# ---------------------------------------------------------------------------

# base / small / medium / large / etc.
_WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL_NAME", "base")
_whisper_model = whisper.load_model(_WHISPER_MODEL_NAME)


def _transcribe(path: str) -> str:
    """Blocking helper executed in a thread (keeps event loop responsive)."""
    result = _whisper_model.transcribe(path, language="nl")
    return result["text"].strip()


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

_EMBED_MODEL_NAME = "NetherlandsForensicInstitute/robbert-2022-dutch-sentence-transformers"
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
) -> AnalyzeResponse:
    """
    • Accepts a single *audio/* upload.
    • Optional query/form field **top_k** (default = 1) returns the K best‑scoring intents.
    """
    if not file.content_type.startswith("audio/"):
        raise HTTPException(400, detail="Uploaded file must be audio/*")

    # 1️⃣ save upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # 2️⃣ transcribe in background thread
        loop = asyncio.get_running_loop()
        text = await loop.run_in_executor(None, _transcribe, tmp_path)

        # 3️⃣ similarity search
        q_vec = _embedder.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        sims = np.dot(_INTENT_EMBS, q_vec)     # shape = (n_intents,)

        # -- FIX ---------------------------------------------------------------
        k = max(1, min(top_k, len(sims))) 
        top_idx = sims.argsort()[-k:][::-1]    # laatste k indices, hoog → laag
        # ---------------------------------------------------------------------

        matches = [
            {"intent": INTENTS[i], "similarity": float(sims[i])}
            for i in top_idx
        ]

        return AnalyzeResponse(transcript=text, matches=matches)

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

    if not intentcode:
        raise HTTPException(422, detail="'intentcode' is required")

    # ── 2. Derive user_text ────────────────────────────────────────────────
    if audio is not None:
        ct = (audio.content_type or "").lower()
        if not (ct.startswith("audio") or ct == "application/octet-stream"):
            raise HTTPException(400, detail="Uploaded file must be audio/*")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
            tmp.write(await audio.read())
            tmp_path = tmp.name

        try:
            loop = asyncio.get_running_loop()
            user_text = await loop.run_in_executor(None, _transcribe, tmp_path)
        finally:
            os.remove(tmp_path)
    else:
        user_text = message or ""
        if not user_text:
            raise HTTPException(
                400, detail="Either 'message' field or audio file required"
            )

    # ── 3. Session bookkeeping ────────────────────────────────────────────
    sid = session_id or str(uuid4())
    session = SESSIONS.setdefault(
        sid,
        {
            "history": [],
            "checklist": {},
            "intentcode": intentcode,
            "draft": "",
        },
    )

    # ── 4. Build / reuse LangChain runnable ───────────────────────────────
    intent = next(i for i in INTENTS if i["intentcode"] == session["intentcode"])
    StepModel = build_step_model(intent)

    if "chain" not in session:
        session["chain"] = make_chain(StepModel, session)  # async fn

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
        step_obj.vragen[0] if step_obj.vragen else "Alle stappen zijn afgerond!",
    )

    # 5️⃣ checklist ---------------------------------------------------------
    session["checklist"] = step_obj.model_dump(exclude={"vragen"})
    finished = all(v for k, v in session["checklist"].items() if k != "draft")

    return ChatResponse(
        session_id=sid,
        reply=step_obj.vragen[0] if step_obj.vragen else "Alle stappen zijn afgerond!",
        checklist=session["checklist"],
        finished=finished,
    )


@app.post("/yap", response_model=YapAccumResponse)
async def yap_accumulate(
    request: Request,
    text: str | None = Form(None),
    audio: UploadFile | None = File(None),
    append: str | None = Form(None),
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

    base_text = text or ""

    if audio is not None:
        ct = (audio.content_type or "").lower()
        if not (ct.startswith("audio") or ct == "application/octet-stream"):
            raise HTTPException(400, detail="Uploaded file must be audio/*")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
            tmp.write(await audio.read())
            tmp_path = tmp.name

        try:
            loop = asyncio.get_running_loop()
            new_text = await loop.run_in_executor(None, _transcribe, tmp_path)
            print(new_text)
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

    return YapAccumResponse(text=base_text)


# ---------------------------------------------------------------------------
#  /yap/start  – bewaar sessie direct in Postgres
# ---------------------------------------------------------------------------
@app.post("/yap/start", response_model=YapStartResponse)
async def yap_start(req: YapStartRequest):
    sid = str(uuid4())

    # 1. burger opent gesprek
    opening = (
        "Ik wil graag subsidie aanvragen voor een buurtfeest. Details:\n"
        f"{req.text}"
    )
    msgs = [{"speaker": "burger", "message": opening}]

    # 2. gemeente‑reactie
    gemeente_reply = await _yap_generate("gemeente", req.text, msgs)
    msgs.append({"speaker": "gemeente", "message": gemeente_reply})

    # 3. cache in RAM  ✅ transcript back
    YAP_SESSIONS[sid] = {
        "transcript": req.text,      # <── added line
        "messages": msgs,
        "turn": 3,                   # volgende = burger
        "finished": False,
        "draft": None,
    }

    # 4. persist two rows + the transcript once
    await _store_yap(sid, "system", f"TRANSCRIPT::{req.text}")   # optional
    await _store_yap(sid, "burger", opening)
    await _store_yap(sid, "gemeente", gemeente_reply)

    finished, draft = _yap_check_finished(msgs)
    if finished:
        YAP_SESSIONS[sid]["finished"] = True
        YAP_SESSIONS[sid]["draft"] = draft

    return YapStartResponse(
        yap_session_id=sid,
        messages=msgs,
        finished=finished,
        draft=draft,
    )


@app.post("/yap/next", response_model=YapNextResponse)
async def yap_next(
    yap_session_id: str = Query(..., description="ID from /yap/start"),
):
    if yap_session_id not in YAP_SESSIONS:
        raise HTTPException(404, detail="Unknown yap_session_id")

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
    role = "burger" if sess["turn"] % 2 == 0 else "gemeente"
    # NB: we started turn=1 after burger opening + gemeente reply, adjust if changed.
    # Safer: infer from last speaker:
    if sess["messages"]:
        last_speaker = sess["messages"][-1]["speaker"]
        role = "burger" if last_speaker == "gemeente" else "gemeente"

    new_msg = await _yap_generate(role, sess["transcript"], sess["messages"])
    sess["messages"].append({"speaker": role, "message": new_msg})
    sess["turn"] += 1

    finished, draft = _yap_check_finished(sess["messages"])
    if finished:
        sess["finished"] = True
        sess["draft"] = draft

    return YapNextResponse(
        yap_session_id=yap_session_id,
        messages=sess["messages"],
        speaker=role,
        message=new_msg,
        finished=sess["finished"],
        draft=sess["draft"],
    )
