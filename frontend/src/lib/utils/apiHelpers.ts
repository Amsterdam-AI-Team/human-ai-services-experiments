// API helper functions for different endpoints
export type EndpointType = 'analyze' | 'chat' | 'chatAudio';

export interface ApiResponse {
	data: any;
	error: string | null;
	isLoading: boolean;
}

export async function sendToEndpoint(endpoint: EndpointType, data: any): Promise<any> {
	const endpointMap = {
		analyze: '/api/analyze',
		chat: '/api/chat', 
		chatAudio: '/api/chatAudio'
	};

	const url = endpointMap[endpoint];
	
	const requestInit: RequestInit = {
		method: 'POST'
	};

	// Handle different data types based on endpoint
	if (endpoint === 'chat') {
		// JSON for text chat
		requestInit.headers = { 'Content-Type': 'application/json' };
		requestInit.body = JSON.stringify(data);
	} else {
		// FormData for audio endpoints (analyze, chatAudio)
		requestInit.body = data;
	}

	const response = await fetch(url, requestInit);
	const result = await response.json();

	if (!response.ok) {
		throw new Error(result.error || 'Request failed');
	}

	return result;
}