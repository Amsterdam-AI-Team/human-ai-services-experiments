from __future__ import annotations
from dotenv import load_dotenv
load_dotenv()

import whisper                                 
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from uuid import uuid4

import numpy as np
from models import (build_step_model, ChatRequest,
                    ChatResponse, AnalyzeResponse)
from intents import INTENTS
from templates import make_chain

import os

import tempfile
import asyncio
import asyncpg
import re          # add at the top

if "AZURE_OPENAI_API_KEY" not in os.environ:
    print("❌  Missing Azure OpenAI API key")

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
# ---------------------------------------------------------------------------
# /analyze route – core pipeline
# ---------------------------------------------------------------------------


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(file: UploadFile = File(...)):
    """Upload an audio file ➜ local Whisper transcript ➜ embed & cosine-match ➜ best intent."""

    if not file.content_type.startswith("audio/"):
        raise HTTPException(400, detail="Uploaded file must be audio/*.")

    # 1️⃣ Persist upload to a temp file so Whisper can read it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # 2️⃣ Run Whisper in a thread so the event loop stays responsive
        loop = asyncio.get_running_loop()
        text: str = await loop.run_in_executor(None, _transcribe, tmp_path)
        if not text:
            raise RuntimeError("Whisper returned empty transcription")

        # 3️⃣ Embed & cosine‑match
        q_vec = _embed(text)
        sims = np.dot(_INTENT_EMBS, q_vec)  # dot = cosine (unit‑norm vectors)
        best_idx = int(np.argmax(sims))
        best_sim = float(sims[best_idx])
        best_intent = INTENTS[best_idx]

        return AnalyzeResponse(transcript=text, match=best_intent, similarity=best_sim)

    except Exception as exc:
        raise HTTPException(500, detail=str(exc))
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

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