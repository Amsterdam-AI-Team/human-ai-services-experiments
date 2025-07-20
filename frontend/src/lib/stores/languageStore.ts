import { writable } from 'svelte/store';
import { locale } from 'svelte-i18n';
import type { LanguageCode } from '$lib/i18n';

// Current language state
export const currentLanguage = writable<LanguageCode>('nl');

// Language switching functions
export function setLanguage(languageCode: LanguageCode) {
  currentLanguage.set(languageCode);
  locale.set(languageCode);
  
  // Persist language preference
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem('preferred-language', languageCode);
  }
}

// Load saved language preference
export function loadSavedLanguage(): LanguageCode {
  if (typeof localStorage !== 'undefined') {
    const saved = localStorage.getItem('preferred-language') as LanguageCode;
    if (saved && ['nl', 'en', 'fr'].includes(saved)) {
      return saved;
    }
  }
  return 'nl'; // Default to Dutch
}

// Initialize language on app start
export function initLanguage() {
  const savedLang = loadSavedLanguage();
  setLanguage(savedLang);
}