# AI‑Assist Service

This repository implements a conversational assistant for municipality legal workflows, such as filing objections to parking fines or updating municipal records. The core components include:

*  **FastAPI backend** (`main.py`) exposing two endpoints:

*  `/analyze` for voice file transcription and intent classification via Whisper & RobBERT.

*  `/chat` for guided, checklist‑driven conversations powered by Azure OpenAI.

*  **Dynamic Pydantic model** (`models.py`) that builds an intent‑specific schema with:

* A running `draft` of the output document.

* Boolean checklist fields for each step.

* A `vragen` array for follow‑up questions.

*  **LangChain integration** (`templates.py`) that:

* Uses `with_structured_output` to enforce JSON responses.

* Persists conversation state (`history`, `checklist`, `draft`) in memory.

*  **Intent definitions** (`intents.py`) capturing the questions and metadata per use case.

*  **Requirements** in `requirements.txt`.

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

* [`/yap`](#yap) – **NEW**

* [`/yap/start`](#yapstart) – **NEW**

* [`/yap/next`](#yapnext) – **NEW**

6. [Session Flow Example](#session-flow-example)

7. [Extending with New Intents](#extending-with-new-intents)

---

## Prerequisites

* Python 3.10+

* A valid Azure OpenAI resource (deployment name, API key, API version)

* Poppler (for OCR fallback) if you plan to use `analyze` on scanned PDFs

*  `ffmpeg` (for Whisper transcription)

---

## Installation 

```bash

git  clone  https://github.com/your-org/ai-assist.git

cd  ai-assist

python3  -m  venv  venv

source  venv/bin/activate

pip  install  -r  requirements.txt

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

DATABASE_URL=url

# Optionally, SSH SOCKS proxy for WSL networking

SSH_SOCKS_PROXY=socks5h://localhost:1080

``` 

---

## Running the Service

```bash

uvicorn  main:app  --host  0.0.0.0  --port  8000

```

The service will listen on **0.0.0.0:8000**. In examples below, replace `localhost` with `128.251.225.11` (your deployment IP).

---

## Endpoints & Usage Examples

### `GET /ping`

Health check:

```bash

curl  http://128.251.225.11/ping

# -> {"status":"ok"}

```

### `POST /analyze`


>  **Purpose** – Upload a Dutch audio clip.

> Whisper transcribes it locally, we embed the text with RobBERT and

> return the *N* most similar intents (cosine‑similarity).


| Parameter | Location | Type | Default | Description |

| --------- | --------- | --------- | ------- | -------------------------------------------------------------------------------------------------- |

| `file` | form‑data | `audio/*` | — | Audio recording (WAV, MP3, …); **must** have a MIME‑type that starts with `audio/` |

| `top_k` | query | `int` | `1` | Number of best matches to return.<br>Values above the total number of intents are silently capped. |


#### Example – return **three** best intents

```bash

curl  -X  POST  "http://128.251.225.11/analyze?top_k=3"  \

-F "file=@/path/to/boete_recording.mp3;type=audio/mpeg"

```

**Response**

```json

{

"transcript": "Ik wil bezwaar maken op mijn parkeerboete.",

"matches": [

{

"intent": {

"intentcode": "create_objection_parking_fine",

"...": "…"  // full intent object

},

"similarity": 0.92

},

{

"intent": {

"intentcode": "update_address_municipal_records",

"...": "…"

},

"similarity": 0.41

},

{

"intent": {

"intentcode": "another_intent_code",

"...": "…"

},

"similarity": 0.33

}

]

}

```

### `POST /chat`

Starts or continues a guided conversation. **Two request modes are supported:**

| Mode | Content‑Type | Required fields | Optional | Notes |

| ----------- | --------------------- | ----------------------- | --------------------------- | ---------------------------------------------------------- |

| *JSON* | `application/json` | `intentcode`, `message` | `session_id` | For plain text messages – easiest for front‑ends |

| *Multipart* | `multipart/form‑data` | `intentcode` | `session_id`, `message`, `` | Use when sending an audio clip – Whisper will be run first |

---

#### 1. JSON (text‑only)

```bash

curl  -X  POST  http://localhost:8000/chat  \

-H "Content-Type: application/json" \

-d  '{

"intentcode": "create_objection_parking_fine",

"message": "Goedemorgen, ik wil bezwaar maken."

}'

```

#### 2. Multipart with audio

```bash

# note the file=@… part name **must** be audio

curl  -X  POST  http://localhost:8000/chat  \

-F intentcode=create_objection_parking_fine \

-F  audio=@/path/to/boete_recording.mp3;type=audio/mpeg  \

-F message="" # optional fall‑back / caption \

-F  session_id=$(uuidgen) # optional; server generates one

```

```json

{

"session_id": "<uuid>",

"reply": "Wat is de datum van de parkeerboete?",

"checklist": {

"draft": "", // running document draft

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

1.  **Start** (ask date)

```bash

curl  -X  POST  http://128.251.225.11/chat  \

-H "Content-Type: application/json" \

-d  '{

"session_id": "abcd-1234-uuid",

"intentcode": "create_objection_parking_fine",

"message": "Goedemorgen, ik wil bezwaar maken."

}'

```

2.  **Supply date**

```bash

curl  -X  POST  http://128.251.225.11/chat  \

-H "Content-Type: application/json" \

-d  '{

"session_id": "abcd-1234-uuid",

"intentcode": "create_objection_parking_fine",

"message": "De boete is op 2025-06-15 uitgeschreven."

}'

```

3.  **Provide plate**

```bash

curl  -X  POST  http://128.251.225.11/chat  \

-H "Content-Type: application/json" \

-d  '{

"session_id": "abcd-1234-uuid",

"intentcode": "create_objection_parking_fine",

"message": "Het kenteken is AB-123-CD."

}'

```

4.  **Give reason**

```bash

curl  -X  POST  http://128.251.225.11/chat  \

-H "Content-Type: application/json" \

-d  '{

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

### `POST /yap`  <a id="yap"></a>

>  **Purpose** – **incremental voice capture**.

> Upload een nieuw audio‑fragment. De server ⤵︎

>  1. transcribeert het met Whisper;

>  2. voegt de tekst toe aan de reeds opgebouwde **transcriptie**;

>  3. retourneert de volledige, geaccumuleerde transcript.

| Parameter | Location | Type | Description |

| -------------- | ---------- | ------------ | -------------------------------------------------------------------------------- |

| `audio` | form‑data | `audio/*` | Geluidsfragment (WAV/MP3/…) |

| `transcript` | form‑data | `string` | (optioneel) bestaande tekst om aan te vullen |

```bash

curl  -X  POST  http://localhost:8000/yap  \

-F "audio=@blokfeest_part1.mp3;type=audio/mpeg"

#  ⇨  {  "transcript":  "We willen op 14 september..."  }

curl  -X  POST  http://localhost:8000/yap  \

-F "audio=@blokfeest_part2.mp3;type=audio/mpeg" \

-F  "transcript=We willen op 14 september..."

# ⇨ { "transcript": "We willen op 14 september... én we vragen €750 subsidie." }

````

---

### `POST /yap/start` <a id="yapstart"></a>

Start  een  **gesimuleerde  dialoog**  tussen  twee  agenten:

* **burger‑agent** – spreekt namens de inwoner

(krijgt  de  volledige  transcript  mee  in  zijn  system‑prompt)

* **gemeente‑agent** – reageert namens de gemeente

| Parameter | Location | Type | Description |

| ------------ | -------- | ------ | ---------------------------------------------- |

| `transcript` | JSON | string | De  samengevoegde  tekst  van  de  micro‑opnames |

| `intentcode` | JSON | string | Welk  procestype  hierbij  hoort (bijv. subsidie) |

```bash

curl  -X POST http://localhost:8000/yap/start \

-H "Content-Type: application/json" \

-d '{

"transcript": "We willen op 14 september een buurt‑bbq ...",

"intentcode": "block_party_subsidy"

}'

```

**Response** 

```jsonc

{

"yap_session_id": "27a79bcf‑7cb6‑4010‑a7f7‑b76c5b479fc0",

"messages": [

{ "speaker": "burger",

"message": "Ik wil graag subsidie ... Details:\nWe willen ..." },

{ "speaker": "gemeente",

"message": "Dank voor uw aanvraag! Ik heb nog enkele vragen ..." }

],

"finished": false,

"draft": null

}

```

---

### `POST /yap/next`  <a id="yapnext"></a>

Haalt **één** volgende beurt op. De server roept intern GPT aan voor

de juiste agent, voegt het antwoord toe aan de geschiedenis en controleert

of er een akkoord & concept‑document (`draft`) is.

| Parameter | Location | Type | Description |

| ---------------- | -------- | ---- | --------------------------------- |

| `yap_session_id` | query | UUID | Verwijzing naar de lopende sessie |

```bash

curl  -X  POST  "http://localhost:8000/yap/next?yap_session_id=<uuid>"

```

**Response (tussentijd)**

```json

{

"yap_session_id": "<uuid>",

"messages": [ ... ], // volledige dialoog tot nu toe

"speaker": "burger",

"message": "Het event is gratis voor alle bewoners.",

"finished": false,

"draft": null

}

```

**Response (afgerond)**

```json

{

"yap_session_id": "<uuid>",

"messages": [ ... ],

"speaker": "gemeente",

"message": "Prima, alles is duidelijk. We keuren de subsidie goed.",

"finished": true,

"draft": "Goedgekeurde subsidie: Buurtfeest “Samen aan Tafel” – €750\n\nEen duurzaam..."

}

```

> 🔄 Blijf `/yap/next` aanroepen tot `"finished": true`.

> Daarna toont iedere oproep eenvoudig het eindresultaat.

---

## Session Flow Example (Yap)

1.  **Opnemen & opsparen**

*Drie audiocalls naar `/yap` leveren één transcript op.*

2.  **Start de dialoog**

```bash

curl  -X  POST  http://localhost:8000/yap/start  \

-H "Content-Type: application/json" \

-d  '{ "transcript": "<samengevoegde tekst>", "intentcode": "block_party_subsidy" }'

# ⇨ ontvang yap_session_id

```

3.  **Onderhandel tot akkoord**

```bash

while  true; do

curl  "http://localhost:8000/yap/next?yap_session_id=$SID"

sleep  1

done

```

4.  **Gebruik de `draft`**

Wanneer `finished=true` kun je het gegenereerde concept rechtstreeks

in een PDF, e‑mail of formulier plakken.

---

## Extending with New Intents

1.  **Add** a new entry to `intents.py`:

```python

INTENTS.append({

"intent": "Tekst voor nieuw intent",

"intentcode": "nieuw_intent_code",

"steps": [ ... ]

})

```

2.  **Restart** the server. The next `/chat` call with `intentcode = "nieuw_intent_code"` will dynamically build its own checklist and draft schema.