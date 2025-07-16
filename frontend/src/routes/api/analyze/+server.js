import { AI_API_ENDPOINT } from '$env/static/private';

export async function POST({ request }) {
	try {
		const formData = await request.formData();

		const response = await fetch(`${AI_API_ENDPOINT}/analyze?top_k=6`, {
			method: 'POST',
			body: formData
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