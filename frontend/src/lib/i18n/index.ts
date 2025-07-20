import { register, init } from 'svelte-i18n';

// Register translation files
register('nl', () => import('./nl.json'));
register('en', () => import('./en.json'));
register('fr', () => import('./fr.json'));

// Initialize i18n - always default to Dutch
export function initI18n() {
  init({
    fallbackLocale: 'nl',
    initialLocale: 'nl', // Always start with Dutch
  });
}

// Available languages
export const languages = [
  { code: 'nl', name: 'Nederlands' },
  { code: 'en', name: 'English' },
  { code: 'fr', name: 'Français' }
] as const;

export type LanguageCode = typeof languages[number]['code'];