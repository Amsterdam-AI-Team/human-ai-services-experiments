import { getIntents, DEFAULT_LANGUAGE, type Intent } from "./i18n";

// Default-language intent list — used as the canonical set for embedding
// pre-computation. Localized variants live in src/lib/server/translations/*.
export const INTENTS: Intent[] = getIntents(DEFAULT_LANGUAGE);

export function getIntentByCode(intentcode: string, lang?: string): Intent | undefined {
	const list = lang ? getIntents(lang) : INTENTS;
	return list.find((i) => i.intentcode === intentcode);
}
