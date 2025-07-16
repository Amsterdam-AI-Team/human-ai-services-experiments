import { AI_API_ENDPOINT } from '$env/static/private';

export async function POST({ request }) {
	try {
		const { message, intentcode } = await request.json();
		
		const requestBody = { message, ...(intentcode && { intentcode }) };
		
		const response = await fetch(`${AI_API_ENDPOINT}/chat`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(requestBody)
		});
		
		const result = await response.json();
		return new Response(JSON.stringify(result), {
			headers: { 'Content-Type': 'application/json' }
		});
	} catch (error) {
		return new Response(JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }), {
			status: 500,
			headers: { 'Content-Type': 'application/json' }
		});
	}
}