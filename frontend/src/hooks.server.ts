import { register, init } from 'svelte-i18n';
import type { Handle } from '@sveltejs/kit';

// Register translations for SSR
register('nl', () => import('./lib/i18n/nl.json'));
register('en', () => import('./lib/i18n/en.json'));
register('fr', () => import('./lib/i18n/fr.json'));

// Initialize with Dutch for SSR
init({
  fallbackLocale: 'nl',
  initialLocale: 'nl',
});

export const handle: Handle = async ({ event, resolve }) => {
  return resolve(event);
};