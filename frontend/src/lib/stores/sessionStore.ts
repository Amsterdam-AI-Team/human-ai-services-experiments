import { writable, get } from "svelte/store";
import { browser } from "$app/environment";

interface SessionData {
  sessionId: string | null;
  timestamp: number;
}

const STORAGE_KEY = "sessionData";
const SESSION_TTL = 30 * 60 * 1000; // 30 minutes

// Load from localStorage on initialization with TTL check
const loadFromStorage = (): SessionData => {
  if (!browser) return { sessionId: null, timestamp: 0 };
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return { sessionId: null, timestamp: 0 };

    const data = JSON.parse(stored);
    const now = Date.now();

    // Check if session has expired
    if (data.timestamp && (now - data.timestamp) > SESSION_TTL) {
      // Session expired, clear it
      localStorage.removeItem(STORAGE_KEY);
      return { sessionId: null, timestamp: 0 };
    }

    return data;
  } catch {
    return { sessionId: null, timestamp: 0 };
  }
};

export const sessionData = writable<SessionData>(loadFromStorage());

// Save to localStorage whenever store updates
sessionData.subscribe((data) => {
  if (browser) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  }
});

export const setSessionId = (sessionId: string) => {
  sessionData.set({
    sessionId,
    timestamp: Date.now(),
  });
};

export const getSessionId = (): string | null => {
  return get(sessionData).sessionId;
};

export const clearSession = () => {
  sessionData.set({ sessionId: null, timestamp: 0 });
};
