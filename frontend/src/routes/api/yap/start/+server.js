import { json } from "@sveltejs/kit";
import { yapGenerate } from "$lib/server/chains";
import { newSessionId, setYapSession } from "$lib/server/sessions";
import { getTranslation, normalizeLanguageCode } from "$lib/server/i18n";

/** @type {import("./$types").RequestHandler} */
export async function POST({ request }) {
	try {
		const body = await request.json();
		/** @type {string} */ const text = (body.text ?? "").toString();
		const language = normalizeLanguageCode(body.language ?? null);

		const openingTemplate = getTranslation(
			language,
			"responses.yap_opening",
			"Ik wil graag subsidie aanvragen voor een buurtfeest. Details:",
		);
		const opening = `${openingTemplate}\n${text}`;

		/** @type {{speaker: "burger"|"gemeente", message: string}[]} */
		const msgs = [{ speaker: "burger", message: opening }];

		const gemeenteReply = await yapGenerate("gemeente", text, msgs, language);
		msgs.push({ speaker: "gemeente", message: gemeenteReply.message });

		const sid = newSessionId();
		setYapSession(sid, {
			transcript: text,
			messages: msgs,
			turn: 2,
			finished: false,
			draft: null,
			language,
		});

		return json({ yap_session_id: sid, messages: msgs });
	} catch (e) {
		const msg = e instanceof Error ? e.message : "Unknown error";
		return new Response(JSON.stringify({ error: msg }), {
			status: 500,
			headers: { "Content-Type": "application/json" },
		});
	}
}
