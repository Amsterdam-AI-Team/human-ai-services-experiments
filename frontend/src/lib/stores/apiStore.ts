import { writable, get } from "svelte/store";
import { browser } from "$app/environment";

export interface ApiResponse {
  endpoint: string;
  data: any;
  timestamp: number;
}

const STORAGE_KEY = "apiResponses";
const API_RESPONSE_TTL = 30 * 60 * 1000; // 30 minutes

// Load from localStorage on initialization with TTL check
const loadFromStorage = (): ApiResponse[] => {
  if (!browser) return [];
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];

    const responses = JSON.parse(stored) as ApiResponse[];
    const now = Date.now();

    // Filter out expired responses
    const validResponses = responses.filter(
      (response) => (now - response.timestamp) <= API_RESPONSE_TTL
    );

    // If we filtered any out, update localStorage
    if (validResponses.length !== responses.length && validResponses.length === 0) {
      localStorage.removeItem(STORAGE_KEY);
      return [];
    } else if (validResponses.length !== responses.length) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(validResponses));
    }

    return validResponses;
  } catch {
    return [];
  }
};

export const apiResponses = writable<ApiResponse[]>(loadFromStorage());

// Save to localStorage whenever store updates
apiResponses.subscribe((responses) => {
  if (browser) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(responses));
  }
});

export const addApiResponse = (endpoint: string, data: any) => {
  apiResponses.update((responses) => [
    ...responses,
    {
      endpoint,
      data,
      timestamp: Date.now(),
    },
  ]);
};

export const getLatestResponse = (endpoint: string) => {
  const responses = get(apiResponses);
  const filtered = responses.filter((r) => r.endpoint === endpoint);
  return filtered.length > 0 ? filtered[filtered.length - 1] : null;
};

export const clearApiResponses = () => {
  apiResponses.set([]);
};

export const clearApiResponsesForEndpoint = (endpoint: string) => {
  apiResponses.update((responses) =>
    responses.filter((r) => r.endpoint !== endpoint),
  );
};
