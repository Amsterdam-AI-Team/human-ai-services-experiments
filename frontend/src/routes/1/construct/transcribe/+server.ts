import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request }) => {
	const formData = await request.formData();
	const audioData = formData.get('audio');
	
	// Simulate API delay
	await new Promise(resolve => setTimeout(resolve, 1500));
	
	// Mock transcription result for parking ticket objection
	const mockTranscription = 'Ik heb een parkeerboete gekregen op 15 maart om 14:30 bij de Nieuwmarkt. Ik had wel betaald via de app maar het kenteken was verkeerd ingevoerd.';
	
	return json({
		success: true,
		transcription: mockTranscription
	});
};