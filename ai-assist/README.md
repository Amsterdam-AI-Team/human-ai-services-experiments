# AI‑Assist Service

This repository implements a conversational assistant for municipality legal workflows, such as filing objections to parking fines or updating municipal records. The core components include:

* **FastAPI backend** (`main.py`) exposing two endpoints:

  * `/analyze` for voice file transcription and intent classification via Whisper & RobBERT.
  * `/chat` for guided, checklist‑driven conversations powered by Azure OpenAI.
* **Dynamic Pydantic model** (`models.py`) that builds an intent‑specific schema with:

  * A running `draft` of the output document.
  * Boolean checklist fields for each step.
  * A `vragen` array for follow‑up questions.
* **LangChain integration** (`templates.py`) that:

  * Uses `with_structured_output` to enforce JSON responses.
  * Persists conversation state (`history`, `checklist`, `draft`) in memory.
* **Intent definitions** (`intents.py`) capturing the questions and metadata per use case.
* **Requirements** in `requirements.txt`.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Service](#running-the-service)
5. [Endpoints & Usage Examples](#endpoints--usage-examples)

   * [`/ping`](#ping)
   * [`/analyze`](#analyze)
   * [`/chat`](#chat)
6. [Session Flow Example](#session-flow-example)
7. [Extending with New Intents](#extending-with-new-intents)

---

## Prerequisites

* Python 3.10+
* A valid Azure OpenAI resource (deployment name, API key, API version)
* Poppler (for OCR fallback) if you plan to use `analyze` on scanned PDFs
* `ffmpeg` (for Whisper transcription)

---

## Installation

```bash
git clone https://github.com/your-org/ai-assist.git
cd ai-assist
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Configuration

Copy your Azure credentials into a `.env` file at the project root:

```ini
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your_api_key_here
OPENAI_API_VERSION=2025-01-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
WHISPER_MODEL_NAME=base
# Optionally, SSH SOCKS proxy for WSL networking
SSH_SOCKS_PROXY=socks5h://localhost:1080
```

---

## Running the Service

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The service will listen on **0.0.0.0:8000**. In examples below, replace `localhost` with `128.251.225.11` (your deployment IP).

---

## Endpoints & Usage Examples

### `GET /ping`

Health check:

```bash
curl http://128.251.225.11:8000/ping
# -> {"status":"ok"}
```

### `POST /analyze`

Transcribe an audio file, detect the user intent, and return similarity score.

```bash
curl -X POST http://128.251.225.11:8000/analyze \
  -F file=@/path/to/audio.wav
```

**Response**:

```json
{
  "transcript": "Ik wil bezwaar maken op mijn parkeerboete",
  "match": { "intent": "Ik wil bezwaar maken...", "intentcode": "create_objection_parking_fine", ...},
  "similarity": 0.92
}
```

### `POST /chat`

Drive a structured conversation. Provide `session_id` to maintain state, `intentcode` to select the workflow, and the user `message`.

```bash
curl -X POST http://128.251.225.11:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
        "session_id": null,
        "intentcode": "create_objection_parking_fine",
        "message": "Goedemorgen, ik wil bezwaar maken op mijn parkeerboete."
      }'
```

**Partial Response**:

```json
{
  "session_id": "<generated-uuid>",
  "reply": "Wat is de datum van de parkeerboete?",
  "checklist": {
    "draft": "",
    "de-datum-van-de-bon": false,
    "het-kenteken-van-de-auto": false,
    "de-reden-van-je-bezwaar": false
  },
  "finished": false
}
```

---

## Session Flow Example

Below is a complete 4‑turn example. All requests use `session_id="abcd-1234-uuid"` and the IP `128.251.225.11`.

1. **Start** (ask date)

```bash
curl -X POST http://128.251.225.11:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
        "session_id": "abcd-1234-uuid",
        "intentcode": "create_objection_parking_fine",
        "message": "Goedemorgen, ik wil bezwaar maken."
      }'
```

2. **Supply date**

```bash
curl -X POST http://128.251.225.11:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
        "session_id": "abcd-1234-uuid",
        "intentcode": "create_objection_parking_fine",
        "message": "De boete is op 2025-06-15 uitgeschreven."
      }'
```

3. **Provide plate**

```bash
curl -X POST http://128.251.225.11:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
        "session_id": "abcd-1234-uuid",
        "intentcode": "create_objection_parking_fine",
        "message": "Het kenteken is AB-123-CD."
      }'
```

4. **Give reason**

```bash
curl -X POST http://128.251.225.11:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
        "session_id": "abcd-1234-uuid",
        "intentcode": "create_objection_parking_fine",
        "message": "Ik maak bezwaar omdat de boete onterecht is."
      }'
```

*Final response includes*:

```json
"checklist": {
  "de-datum-van-de-bon": true,
  "het-kenteken-van-de-auto": true,
  "de-reden-van-je-bezwaar": true
},
"finished": true
```

---

## Extending with New Intents

1. **Add** a new entry to `intents.py`:

   ```python
   INTENTS.append({
     "intent": "Tekst voor nieuw intent",
     "intentcode": "nieuw_intent_code",
     "steps": [ ... ]
   })
   ```
2. **Restart** the server. The next `/chat` call with `intentcode = "nieuw_intent_code"` will dynamically build its own checklist and draft schema.


