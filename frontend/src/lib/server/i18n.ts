import nl from "./translations/nl.json" with { type: "json" };
import en from "./translations/en.json" with { type: "json" };
import fr from "./translations/fr.json" with { type: "json" };

export const SUPPORTED_LANGUAGES = ["nl", "en", "fr"] as const;
export type LanguageCode = (typeof SUPPORTED_LANGUAGES)[number];
export const DEFAULT_LANGUAGE: LanguageCode = "nl";

type Translations = Record<string, unknown>;

const TRANSLATIONS: Record<LanguageCode, Translations> = {
	nl: nl as Translations,
	en: en as Translations,
	fr: fr as Translations,
};

export function isSupportedLanguage(lang: string): lang is LanguageCode {
	return (SUPPORTED_LANGUAGES as readonly string[]).includes(lang);
}

export function normalizeLanguageCode(lang: string | null | undefined): LanguageCode {
	if (!lang) return DEFAULT_LANGUAGE;
	const code = lang.toLowerCase().trim();
	if (isSupportedLanguage(code)) return code;
	const base = code.split("-")[0];
	if (isSupportedLanguage(base)) return base;
	return DEFAULT_LANGUAGE;
}

export function getTranslation(lang: string, keyPath: string, fallback?: string): string {
	const code = normalizeLanguageCode(lang);
	const tree = TRANSLATIONS[code];
	let cur: unknown = tree;
	for (const key of keyPath.split(".")) {
		if (cur && typeof cur === "object" && key in (cur as Record<string, unknown>)) {
			cur = (cur as Record<string, unknown>)[key];
		} else {
			cur = undefined;
			break;
		}
	}
	if (typeof cur === "string") return cur;
	if (fallback !== undefined) return fallback;
	if (code !== DEFAULT_LANGUAGE) return getTranslation(DEFAULT_LANGUAGE, keyPath, fallback);
	throw new Error(`Translation key not found: ${keyPath} for ${code}`);
}

export interface SystemPromptData {
	role?: string;
	context?: string;
	objective?: string;
	style?: string;
	tone?: string;
	audience?: string;
	response?: string;
	instructions?: string;
	workflow?: string;
	important?: string;
}

export type SystemPromptType = "juridisch_medewerker" | "burger_system" | "gemeente_system";

export function getSystemPrompt(lang: string, type: SystemPromptType): SystemPromptData {
	const code = normalizeLanguageCode(lang);
	const prompts = (TRANSLATIONS[code] as { system_prompts?: Record<string, SystemPromptData> })
		.system_prompts;
	const data = prompts?.[type];
	if (data) return data;
	if (code !== DEFAULT_LANGUAGE) return getSystemPrompt(DEFAULT_LANGUAGE, type);
	throw new Error(`System prompt not found: ${type} for ${code}`);
}

export interface IntentStep {
	title: string;
	description: string;
}

export interface Intent {
	intent: string;
	intentcode: string;
	steps: IntentStep[];
}

export function getIntents(lang: string): Intent[] {
	const code = normalizeLanguageCode(lang);
	const intents = (TRANSLATIONS[code] as { intents?: Intent[] }).intents;
	if (intents && intents.length > 0) return intents;
	if (code !== DEFAULT_LANGUAGE) return getIntents(DEFAULT_LANGUAGE);
	return [];
}

export function getLanguageSuffix(lang: string): string {
	return getTranslation(lang, "language_suffix", "Answer strictly in Dutch");
}

export function getLanguageName(lang: string): string {
	const map: Record<LanguageCode, string> = { nl: "Dutch", en: "English", fr: "French" };
	return map[normalizeLanguageCode(lang)];
}
