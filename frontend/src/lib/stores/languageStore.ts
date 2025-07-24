import { writable } from "svelte/store";
import { locale } from "svelte-i18n";
import type { LanguageCode } from "$lib/i18n";

// Current language state
export const currentLanguage = writable<LanguageCode>("nl");

// Language switching functions
export function setLanguage(languageCode: LanguageCode) {
  currentLanguage.set(languageCode);
  locale.set(languageCode);

  // Persist language preference
  if (typeof localStorage !== "undefined") {
    localStorage.setItem("preferred-language", languageCode);
  }
}

// Load saved language preference (only for manual overrides)
export function loadSavedLanguage(): LanguageCode {
  if (typeof localStorage !== "undefined") {
    const saved = localStorage.getItem("preferred-language") as LanguageCode;
    if (saved && ["nl", "en", "fr"].includes(saved)) {
      return saved;
    }
  }
  return "nl"; // Always default to Dutch
}

// Initialize language on app start - always Dutch unless manually changed
export function initLanguage() {
  const savedLang = loadSavedLanguage();
  setLanguage(savedLang);
}

// Function for API-driven language switching (future use with Whisper)
export function setLanguageFromAPI(
  languageCode: LanguageCode,
  confidence?: number,
) {
  console.log(
    `API detected language: ${languageCode} (confidence: ${confidence})`,
  );

  // You can add confidence threshold logic here
  // if (confidence && confidence < 0.8) {
  //   console.log('Low confidence, not switching language');
  //   return;
  // }

  setLanguage(languageCode);
  // Note: This won't persist to localStorage - only manual switches persist
}

// Helper function to check if detected language differs from current
export function shouldSwitchLanguage(detectedLang: LanguageCode): boolean {
  let current: LanguageCode = "nl";
  currentLanguage.subscribe((lang) => (current = lang))();
  return detectedLang !== current && ["nl", "en", "fr"].includes(detectedLang);
}
