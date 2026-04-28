import { json, error } from "@sveltejs/kit";
import { yapGenerate } from "$lib/server/chains";
import { getYapSession } from "$lib/server/sessions";
import { normalizeLanguageCode, getTranslation } from "$lib/server/i18n";

/** @type {import("./$types").RequestHandler} */
export async function POST({ url }) {
	try {
		const yap_session_id = url.searchParams.get("yap_session_id");
		const language = normalizeLanguageCode(url.searchParams.get("language"));

		if (!yap_session_id) {
			throw error(400, "yap_session_id query parameter is required");
		}

		const sess = getYapSession(yap_session_id);
		if (!sess) {
			throw error(
				404,
				getTranslation(language, "responses.error_unknown_session", "Unknown yap_session_id"),
			);
		}

		if (sess.finished) {
			const last = sess.messages[sess.messages.length - 1];
			return json({
				yap_session_id,
				messages: sess.messages,
				speaker: last.speaker,
				message: last.message,
				finished: true,
				draft: sess.draft,
			});
		}

		const lastSpeaker = sess.messages[sess.messages.length - 1].speaker;
		/** @type {"burger"|"gemeente"} */
		const role = lastSpeaker === "gemeente" ? "burger" : "gemeente";

		const sessionLang = normalizeLanguageCode(sess.language || language);
		const turn = await yapGenerate(role, sess.transcript, sess.messages, sessionLang);

		sess.messages.push({ speaker: role, message: turn.message });

		if (role === "gemeente" && "finished" in turn) {
			sess.finished = Boolean(turn.finished);
			sess.draft = turn.draft ?? null;
		}

		return json({
			yap_session_id,
			messages: sess.messages,
			speaker: role,
			message: turn.message,
			finished: sess.finished,
			draft: sess.draft,
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
