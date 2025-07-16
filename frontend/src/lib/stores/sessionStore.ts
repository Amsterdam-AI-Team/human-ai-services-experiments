import { writable } from 'svelte/store';
import { browser } from '$app/environment';

interface SessionData {
	sessionId: string | null;
	timestamp: number;
}

const STORAGE_KEY = 'sessionData';

// Load from localStorage on initialization
const loadFromStorage = (): SessionData => {
	if (!browser) return { sessionId: null, timestamp: 0 };
	try {
		const stored = localStorage.getItem(STORAGE_KEY);
		return stored ? JSON.parse(stored) : { sessionId: null, timestamp: 0 };
	} catch {
		return { sessionId: null, timestamp: 0 };
	}
};

export const sessionData = writable<SessionData>(loadFromStorage());

// Save to localStorage whenever store updates
sessionData.subscribe(data => {
	if (browser) {
		localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
	}
});

export const setSessionId = (sessionId: string) => {
	sessionData.set({
		sessionId,
		timestamp: Date.now()
	});
};

export const getSessionId = (): string | null => {
	let currentSessionId: string | null = null;
	
	sessionData.subscribe(data => {
		currentSessionId = data.sessionId;
	})();
	
	return currentSessionId;
};

export const clearSession = () => {
	sessionData.set({ sessionId: null, timestamp: 0 });
};