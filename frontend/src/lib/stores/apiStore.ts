import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export interface ApiResponse {
	endpoint: string;
	data: any;
	timestamp: number;
}

const STORAGE_KEY = 'apiResponses';

// Load from localStorage on initialization
const loadFromStorage = (): ApiResponse[] => {
	if (!browser) return [];
	try {
		const stored = localStorage.getItem(STORAGE_KEY);
		return stored ? JSON.parse(stored) : [];
	} catch {
		return [];
	}
};

export const apiResponses = writable<ApiResponse[]>(loadFromStorage());

// Save to localStorage whenever store updates
apiResponses.subscribe(responses => {
	if (browser) {
		localStorage.setItem(STORAGE_KEY, JSON.stringify(responses));
	}
});

export const addApiResponse = (endpoint: string, data: any) => {
	apiResponses.update(responses => [
		...responses,
		{
			endpoint,
			data,
			timestamp: Date.now()
		}
	]);
};

export const getLatestResponse = (endpoint: string) => {
	let latestResponse: ApiResponse | null = null;
	
	apiResponses.subscribe(responses => {
		const filtered = responses.filter(r => r.endpoint === endpoint);
		latestResponse = filtered.length > 0 ? filtered[filtered.length - 1] : null;
	})();
	
	return latestResponse;
};

export const clearApiResponses = () => {
	apiResponses.set([]);
};

export const clearApiResponsesForEndpoint = (endpoint: string) => {
	apiResponses.update(responses => 
		responses.filter(r => r.endpoint !== endpoint)
	);
};