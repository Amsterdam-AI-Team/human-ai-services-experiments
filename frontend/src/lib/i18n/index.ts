import { register, init, getLocaleFromNavigator } from 'svelte-i18n';

// Register translation files
register('nl', () => import('./nl.json'));
register('en', () => import('./en.json'));
register('fr', () => import('./fr.json'));

// Initialize i18n
export function initI18n() {
  init({
    fallbackLocale: 'nl', // Default to Dutch
    initialLocale: getLocaleFromNavigator() || 'nl',
  });
}

// Available languages
export const languages = [
  { code: 'nl', name: 'Nederlands' },
  { code: 'en', name: 'English' },
  { code: 'fr', name: 'Français' }
] as const;

export type LanguageCode = typeof languages[number]['code'];