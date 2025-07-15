import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request }) => {
	const formData = await request.formData();
	const audioData = formData.get('audio');
	
	// Simulate API delay
	await new Promise(resolve => setTimeout(resolve, 1500));
	
	// Mock transcription result
	const mockTranscription = 'Ik wil een groot feest met 50 mensen, blauwe vlaggen en een sparerib BBQ';
	
	return json({
		success: true,
		transcription: mockTranscription
	});
};