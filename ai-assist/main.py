from __future__ import annotations
from dotenv import load_dotenv
load_dotenv()

import whisper                                 
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Body
from uuid import uuid4

import numpy as np
from models import (build_step_model, ChatRequest,
                    ChatResponse, AnalyzeResponse)
from intents import INTENTS
from templates import make_chain

import os

import tempfile
import asyncio



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

# ---------------------------------------------------------------------------
# Pydantic response model
# ---------------------------------------------------------------------------




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

# ---------------------------------------------------------------------------
# Chatbot
# ---------------------------------------------------------------------------

@app.post("/chat", response_model=ChatResponse)
async def chat(data: ChatRequest = Body(...)):
    # 1. resolve / create session
    sid = data.session_id or str(uuid4())
    session = SESSIONS.setdefault(
        sid, {"history": [], "checklist": {}, "intentcode": data.intentcode}
    )

    # 2. get intent + dynamic step model
    intent = next(i for i in INTENTS if i["intentcode"] == session["intentcode"])
    StepModel = build_step_model(intent)

    # 3. build chain once per session
    if "chain" not in session:
        session["chain"] = make_chain(StepModel)

    # 4. run chain (async)
    chain_input = {"message": data.message, "history": session["history"]}
    step_obj: StepModel = await session["chain"].ainvoke(chain_input)

    # 5. update session state
    session["history"].append({"role": "user", "content": data.message})
    session["history"].append({"role": "assistant", "content": step_obj.vragen or ""})
    session["checklist"] = step_obj.model_dump(exclude={"vragen"})
    finished = all(session["checklist"].values())

    return ChatResponse(
        session_id=sid,
        reply=step_obj.vragen[0] if step_obj.vragen else "Alle stappen zijn afgerond!",
        checklist=session["checklist"],
        finished=finished,
    )
