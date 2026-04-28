import { json, error } from "@sveltejs/kit";
import { transcribe } from "$lib/server/transcribe";
import { topKIntents } from "$lib/server/embeddings";
import { getIntents, normalizeLanguageCode } from "$lib/server/i18n";

/** @type {import("./$types").RequestHandler} */
export async function POST({ request, url }) {
	try {
		const formData = await request.formData();
		const file = formData.get("file");
		if (!(file instanceof Blob)) {
			throw error(400, "form field 'file' must be an audio Blob");
		}

		const language = normalizeLanguageCode(
			(formData.get("language") || url.searchParams.get("language") || "").toString(),
		);
		const topKParam = parseInt(url.searchParams.get("top_k") || "1", 10);
		const topK = Number.isFinite(topKParam) ? topKParam : 1;

		const filename = file instanceof File ? file.name : "audio.webm";
		const { text: transcript } = await transcribe(file, filename, language);

		const matches = await topKIntents(transcript, topK);

		// Re-localize matched intents using the request language.
		const localized = getIntents(language);
		const map = new Map(localized.map((i) => [i.intentcode, i]));
		const out = matches.map(({ intent, similarity }) => ({
			intent: map.get(intent.intentcode) ?? intent,
			similarity,
		}));

		return json({ transcript, language, matches: out });
	} catch (e) {
		const msg = e instanceof Error ? e.message : "Unknown error";
		return new Response(JSON.stringify({ error: msg }), {
			status: 500,
			headers: { "Content-Type": "application/json" },
		});
	}
}
