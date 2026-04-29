# Environment variables for deployment

This app reads its configuration from environment variables. Two SvelteKit
mechanisms are used:

- **`$env/static/private`** — the value is **inlined at build time**. The
  zip we ship to Azure already contains the value baked into the bundled
  output. `npm run build` reads it from `frontend/.env`.
- **`$env/dynamic/private`** — the value is **read at runtime** via
  `process.env`. Must be present in App Service → Settings →
  Environment variables.

Some keys are referenced in both ways (e.g. `AZURE_OPENAI_ENDPOINT` is
static in `chains.ts`/`transcribe.ts` and dynamic in `embeddings.ts`).
Easiest rule: **set every key in both places** (local `frontend/.env`
before build, and App Service env vars at runtime). Duplicate is safe.

## Build-time prerequisite (zip-deploy)

Before running `npm run build` for a deploy zip, ensure
`frontend/.env` contains all keys below with valid values. Anything
missing or wrong will be silently baked into the output and you only
discover it in production.

## Required variables

| Var | Used in | Mechanism | Secret? | Purpose |
|---|---|---|---|---|
| `AZURE_OPENAI_ENDPOINT` | chains.ts, transcribe.ts (static); embeddings.ts (dynamic) | both | no (URL) | Base URL of the Azure OpenAI resource, e.g. `https://<name>.cognitiveservices.azure.com/` |
| `AZURE_OPENAI_API_KEY` | chains.ts (static); embeddings.ts (dynamic) | both | **YES** | API key for the chat + embeddings deployments |
| `OPENAI_API_VERSION` | chains.ts (static); embeddings.ts (dynamic) | both | no | Azure OpenAI API version, e.g. `2025-01-01-preview` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | chains.ts | static | no | Chat-completions deployment name, e.g. `gpt-4.1` |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | embeddings.ts | dynamic | no | Either a deployment name (URL is built from `AZURE_OPENAI_ENDPOINT`) or a full embeddings URL incl. `?api-version=...` |
| `TRANSCRIPTION_AZ_ENDPOINT` | transcribe.ts | static | no (URL) | Full URL of the transcription endpoint, **must end in `/audio/transcriptions`** (NOT `/audio/translations`) |
| `TRANSCRIPTION_AZ_MODEL` | transcribe.ts | static | no | Multipart `model` field sent with the transcribe request, e.g. `whisper` or `gpt-4o-transcribe` |
| `TRANSCRIPTION_API_KEY` | transcribe.ts | static | **YES** | API key for the transcription endpoint |

## Optional variables

| Var | Mechanism | Purpose |
|---|---|---|
| `AZURE_OPENAI_EMBEDDING_API_KEY` | dynamic | Separate API key if embeddings live on a different Azure resource than the chat deployment. Falls back to `AZURE_OPENAI_API_KEY` if unset. |
| `PORT` | runtime (adapter-node default) | Port the adapter-node server listens on. Azure App Service sets this automatically; leave unset in local `.env`. |

## Configuring App Service

In Azure Portal → App Service → **Settings → Environment variables → App settings**:

1. Add every required variable above (and any optional ones you use).
2. Mark the secret ones (`*_API_KEY`) appropriately (Key Vault reference if you want).
3. After saving, the app restarts automatically.

You **can** skip the static-only variables in App Settings if the local
build already baked them in — but keeping App Settings as the source of
truth is less error-prone when you rebuild later.

## Sanity check

After setting up `frontend/.env`, verify the build picks them up:

```bash
cd frontend
npm run build
node build
# Curl http://localhost:3000/ping (or another endpoint) and check logs
```

If a static variable was missing at build time, the bundled output will
have `undefined` for it and the corresponding endpoint will throw at
the first request.
