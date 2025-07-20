import { register, init, waitLocale, getLocaleFromNavigator } from 'svelte-i18n';

// Register translation files
register('nl', () => import('./nl.json'));
register('en', () => import('./en.json'));
register('fr', () => import('./fr.json'));

let isInitialized = false;

// Initialize i18n - always default to Dutch
export async function initI18n() {
  if (isInitialized) return;
  
  try {
    init({
      fallbackLocale: 'nl',
      initialLocale: 'nl', // Always start with Dutch
    });
    
    // Wait for the locale to be loaded
    await waitLocale('nl');
    isInitialized = true;
    console.log('i18n initialized successfully');
  } catch (error) {
    console.error('Failed to initialize i18n:', error);
    throw error;
  }
}

// Available languages
export const languages = [
  { code: 'nl', name: 'Nederlands' },
  { code: 'en', name: 'English' },
  { code: 'fr', name: 'Français' }
] as const;

export type LanguageCode = typeof languages[number]['code'];