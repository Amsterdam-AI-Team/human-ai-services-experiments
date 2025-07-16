import { writable } from 'svelte/store';

export interface ApiResponse {
	endpoint: string;
	data: any;
	timestamp: number;
}

export const apiResponses = writable<ApiResponse[]>([]);

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