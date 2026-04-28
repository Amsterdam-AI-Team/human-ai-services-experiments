import {
	TRANSCRIPTION_AZ_ENDPOINT,
	TRANSCRIPTION_AZ_MODEL,
	TRANSCRIPTION_API_KEY,
} from "$env/static/private";
import { SUPPORTED_LANGUAGES, type LanguageCode } from "./i18n";

export interface TranscribeResult {
	text: string;
}

export async function transcribe(
	audio: Blob,
	filename: string,
	language?: string,
): Promise<TranscribeResult> {
	if (!TRANSCRIPTION_AZ_ENDPOINT) {
		throw new Error("TRANSCRIPTION_AZ_ENDPOINT not set");
	}
	if (!TRANSCRIPTION_API_KEY) {
		throw new Error("TRANSCRIPTION_API_KEY not set");
	}

	const form = new FormData();
	form.append("file", audio, filename);
	form.append("model", TRANSCRIPTION_AZ_MODEL || "whisper");
	if (language && (SUPPORTED_LANGUAGES as readonly string[]).includes(language)) {
		form.append("language", language as LanguageCode);
	}

	const r = await fetch(TRANSCRIPTION_AZ_ENDPOINT, {
		method: "POST",
		headers: { Authorization: `Bearer ${TRANSCRIPTION_API_KEY}` },
		body: form,
	});

	if (!r.ok) {
		const body = await r.text();
		throw new Error(`Azure transcribe failed: ${r.status} ${body.slice(0, 500)}`);
	}

	const data = (await r.json()) as { text?: string };
	return { text: (data.text ?? "").trim() };
}
