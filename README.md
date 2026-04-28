# Experiments for human AI services

Demo applications exploring how Amsterdam residents interact with the
municipality using voice and AI. The current demo covers two flows:

* **Concept 1** – guided form-filling chat for handling municipal requests
  (parking-fine objection, public-space report, …).
* **Concept 2** – two-agent dialog (resident agent ↔ municipality agent)
  for negotiating a neighbourhood-event subsidy.

## Background

De groeiende mogelijkheden van AI maken nieuwe vormen van interactie mogelijk.
Hoe zien inwoners de interactie met de gemeente voor zich in de toekomst?
Blijft er behoefte aan menselijk contact, waarbij technologie een
faciliterende rol kan spelen? Of is het mogelijk om met vergaande
automatisering toch rekening te houden met de menselijke maat?

## Architecture

Single SvelteKit application — no separate backend, no database. All
server-side logic (audio transcription, embedding-based intent matching,
LLM chat with structured output, in-memory session state) lives in
`frontend/src/lib/server/` and is exposed via SvelteKit `+server.js`
endpoints under `frontend/src/routes/api/*`.

External dependencies: Azure OpenAI (chat + embeddings) and an Azure
Whisper / gpt-4o-transcribe deployment for speech-to-text. No user data
is persisted — sessions live in process memory and disappear on restart.

## Repository layout

* [`frontend`](./frontend) — the SvelteKit app (the actual deployable).
* [`README.md`](./README.md) — this file.

## Quick start

```bash
git clone https://github.com/Amsterdam-AI-Team/human-ai-services-experiments.git
cd human-ai-services-experiments/frontend
pnpm install
# Fill in Azure credentials in .env (see frontend/.env for required keys)
pnpm dev
```

See [`frontend/README.md`](./frontend/README.md) for full setup, env-var
reference, and feature documentation.

## Contributing

Feel free to help out! [Open an issue](https://github.com/Amsterdam-AI-Team/human-ai-services-experiments/issues),
submit a [PR](https://github.com/Amsterdam-AI-Team/human-ai-services-experiments/pulls)
or [contact us](https://amsterdamintelligence.com/contact/).

## Acknowledgements

This repository was created by
[Amsterdam Intelligence](https://amsterdamintelligence.com/) for the City of
Amsterdam.

## License

This project is licensed under the terms of the European Union Public
License 1.2 (EUPL-1.2).
