import { json, error } from "@sveltejs/kit";
import { transcribe } from "$lib/server/transcribe";
import { runChat } from "$lib/server/chains";
import { getOrCreateChatSession, newSessionId } from "$lib/server/sessions";
import { getTranslation, normalizeLanguageCode } from "$lib/server/i18n";
import { INTENTS } from "$lib/server/intents";

/** @type {import("./$types").RequestHandler} */
export async function POST({ request }) {
	try {
		const ct = request.headers.get("content-type") || "";

		/** @type {string|null} */ let intentcode = null;
		/** @type {string|null} */ let message = null;
		/** @type {string|null} */ let sessionIdInput = null;
		/** @type {string|null} */ let languageRaw = null;
		/** @type {Blob|null} */ let audio = null;
		/** @type {string} */ let audioFilename = "audio.webm";

		if (ct.includes("multipart/form-data")) {
			const fd = await request.formData();
			intentcode = (fd.get("intentcode") ?? null)?.toString() ?? null;
			message = (fd.get("message") ?? null)?.toString() ?? null;
			sessionIdInput = (fd.get("session_id") ?? null)?.toString() ?? null;
			languageRaw = (fd.get("language") ?? null)?.toString() ?? null;
			const a = fd.get("audio");
			if (a instanceof Blob) {
				audio = a;
				if (a instanceof File && a.name) audioFilename = a.name;
			}
		} else {
			const body = await request.json();
			intentcode = body.intentcode ?? null;
			message = body.message ?? null;
			sessionIdInput = body.session_id ?? null;
			languageRaw = body.language ?? null;
		}

		const language = normalizeLanguageCode(languageRaw);
		if (!intentcode) {
			throw error(
				422,
				getTranslation(language, "responses.error_intentcode_required", "'intentcode' is required"),
			);
		}

		// Resolve user text: transcribe audio if present, otherwise use message.
		/** @type {string} */ let userText;
		if (audio) {
			const r = await transcribe(audio, audioFilename, language);
			userText = r.text;
		} else if (message) {
			userText = message;
		} else {
			throw error(
				400,
				getTranslation(
					language,
					"responses.error_message_or_audio",
					"Either 'message' field or audio file required",
				),
			);
		}

		const sid = sessionIdInput || newSessionId();
		const session = getOrCreateChatSession(sid, intentcode);

		const intent = INTENTS.find((i) => i.intentcode === session.intentcode);
		if (!intent) {
			throw error(404, `Unknown intentcode: ${session.intentcode}`);
		}

		const result = await runChat(intent, session, userText, language);

		// Persist conversation turn into session history.
		session.history.push({ role: "user", content: userText });
		session.history.push({ role: "assistant", content: result.reply });
		session.checklist = result.checklist;
		session.language = language;

		return json({
			session_id: sid,
			reply: result.reply,
			checklist: result.checklist,
			finished: result.finished,
			user_text: userText,
			draft: result.draft,
		});
	} catch (e) {
		if (e && typeof e === "object" && "status" in e) throw e;
		const msg = e instanceof Error ? e.message : "Unknown error";
		return new Response(JSON.stringify({ error: msg }), {
			status: 500,
			headers: { "Content-Type": "application/json" },
		});
	}
}
