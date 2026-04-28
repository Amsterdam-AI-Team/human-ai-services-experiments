import {
	TRANSCRIPTION_AZ_ENDPOINT,
	TRANSCRIPTION_AZ_MODEL,
	TRANSCRIPTION_API_KEY,
} from "$env/static/private";
import { SUPPORTED_LANGUAGES, type LanguageCode } from "./i18n";

export interface TranscribeResult {
	text: string;
}

interface DetectedFormat {
	mime: string;
	ext: string;
}

// Detect actual audio format from magic bytes. The browser MediaRecorder
// produces webm/opus by default but the frontend wraps it in a Blob with
// type "audio/wav" — gpt-4o-transcribe rejects the mismatch where whisper
// silently tolerates it.
function detectFormat(bytes: Uint8Array): DetectedFormat {
	const head = bytes.slice(0, 16);
	const hex = Array.from(head)
		.map((b) => b.toString(16).padStart(2, "0"))
		.join("");
	// EBML / Matroska / WebM
	if (hex.startsWith("1a45dfa3")) return { mime: "audio/webm", ext: "webm" };
	// OggS
	if (hex.startsWith("4f676753")) return { mime: "audio/ogg", ext: "ogg" };
	// RIFF .... WAVE
	if (hex.startsWith("52494646") && hex.slice(16, 24) === "57415645")
		return { mime: "audio/wav", ext: "wav" };
	// ID3 / MPEG audio frame sync
	if (hex.startsWith("494433") || /^fff[ab]/.test(hex)) return { mime: "audio/mpeg", ext: "mp3" };
	// ftyp (mp4/m4a) — bytes 4..8
	if (hex.slice(8, 16) === "66747970") return { mime: "audio/mp4", ext: "m4a" };
	// FLAC
	if (hex.startsWith("664c6143")) return { mime: "audio/flac", ext: "flac" };
	// Fallback: trust the blob's own type if it looks audio-like.
	return { mime: "application/octet-stream", ext: "bin" };
}

function basenameWithoutExt(filename: string): string {
	const dot = filename.lastIndexOf(".");
	return dot > 0 ? filename.slice(0, dot) : filename;
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

	const buf = new Uint8Array(await audio.arrayBuffer());
	const fmt = detectFormat(buf);
	const fixedBlob = new Blob([buf], { type: fmt.mime });
	const fixedName = `${basenameWithoutExt(filename) || "audio"}.${fmt.ext}`;

	const form = new FormData();
	form.append("file", fixedBlob, fixedName);
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
		throw new Error(
			`Azure transcribe failed: ${r.status} (sent as ${fmt.mime}) ${body.slice(0, 500)}`,
		);
	}

	const data = (await r.json()) as { text?: string };
	return { text: (data.text ?? "").trim() };
}
