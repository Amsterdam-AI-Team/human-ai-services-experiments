import { json, error } from "@sveltejs/kit";
import { transcribe } from "$lib/server/transcribe";
import { normalizeLanguageCode, getTranslation } from "$lib/server/i18n";

/** @type {import("./$types").RequestHandler} */
export async function POST({ request }) {
	try {
		const ct = request.headers.get("content-type") || "";

		/** @type {string} */ let baseText = "";
		/** @type {string} */ let appendStr = "";
		/** @type {Blob|null} */ let audio = null;
		/** @type {string} */ let audioFilename = "audio.webm";
		/** @type {string|null} */ let languageRaw = null;

		if (ct.includes("multipart/form-data")) {
			const fd = await request.formData();
			baseText = (fd.get("text") ?? "").toString();
			appendStr = (fd.get("append") ?? "").toString();
			languageRaw = (fd.get("language") ?? null)?.toString() ?? null;
			const a = fd.get("audio");
			if (a instanceof Blob) {
				audio = a;
				if (a instanceof File && a.name) audioFilename = a.name;
			}
		} else {
			const body = await request.json();
			baseText = body.text ?? "";
			appendStr = body.append ?? "";
			languageRaw = body.language ?? null;
		}

		const language = normalizeLanguageCode(languageRaw);

		if (audio) {
			const ctype = audio.type.toLowerCase();
			if (!(ctype.startsWith("audio") || ctype === "application/octet-stream" || ctype === "")) {
				throw error(
					400,
					getTranslation(
						language,
						"responses.error_audio_required",
						"Uploaded file must be audio/*",
					),
				);
			}
			const { text: newText } = await transcribe(audio, audioFilename, language);
			baseText = baseText ? baseText.replace(/\s+$/, "") + "\n" + newText.trim() : newText.trim();
		} else if (appendStr) {
			baseText = baseText
				? baseText.replace(/\s+$/, "") + "\n" + appendStr.trim()
				: appendStr.trim();
		} else {
			baseText = baseText.trim();
		}

		return json({ text: baseText, language });
	} catch (e) {
		if (e && typeof e === "object" && "status" in e) throw e;
		const msg = e instanceof Error ? e.message : "Unknown error";
		return new Response(JSON.stringify({ error: msg }), {
			status: 500,
			headers: { "Content-Type": "application/json" },
		});
	}
}
