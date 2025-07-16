<!-- SingleRecordingSection.svelte -->
<script lang="ts">
	import { sendToEndpoint, type EndpointType } from '$lib/utils/apiHelpers';
	import { addApiResponse } from '$lib/stores/apiStore';
	import { getSessionId } from '$lib/stores/sessionStore';

	let { endpoint = 'analyze' as EndpointType, intentcode = null } = $props();

	let isAnalyzing = $state(false);
	let isRecording = $state(false);
	let mediaRecorder = $state<MediaRecorder | null>(null);
	let audioChunks = $state<Blob[]>([]);

	async function handleRecordingStop(audioBlob: Blob) {
		// Send audio to the specified endpoint
		isAnalyzing = true;
		const formData = new FormData();
		
		// TODO: API inconsistency - different endpoints expect different field names
		// analyze endpoint expects 'file', chat/chatAudio endpoints expect 'audio'
		// When API becomes consistent, this can be simplified to always use the same field name
		const audioFieldName = endpoint === 'analyze' ? 'file' : 'audio';
		formData.append(audioFieldName, audioBlob, 'recording.wav');
		
		// Add intentcode to FormData if provided
		if (intentcode) {
			formData.append('intentcode', intentcode);
		}
		
		// Add session_id to FormData if it exists and endpoint is chatAudio
		if (endpoint === 'chatAudio') {
			const currentSessionId = getSessionId();
			if (currentSessionId) {
				formData.append('session_id', currentSessionId);
			}
		}

		try {
			const result = await sendToEndpoint(endpoint, formData);
			console.log('API response:', result);
			
			// Store the response in the store
			addApiResponse(endpoint, result);
		} catch (error) {
			console.error('API error:', error);
			// Store error in the store as well
			addApiResponse(endpoint, { error: error instanceof Error ? error.message : 'Unknown error' });
		} finally {
			isAnalyzing = false;
		}
	}

	async function toggleRecording() {
		if (isRecording) {
			// Stop recording
			if (mediaRecorder && mediaRecorder.state !== 'inactive') {
				mediaRecorder.stop();
				mediaRecorder.stream.getTracks().forEach((track) => track.stop());
			}
		} else {
			// Start recording
			if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
				try {
					const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
					mediaRecorder = new MediaRecorder(stream);
					mediaRecorder.start();
					isRecording = true;
					audioChunks = [];

					mediaRecorder.addEventListener('dataavailable', (event) => {
						audioChunks.push(event.data);
					});

					mediaRecorder.addEventListener('stop', async () => {
						const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
						console.log('Recording stopped', audioBlob);
						audioChunks = [];
						isRecording = false;
						
						// Handle the stopped recording
						await handleRecordingStop(audioBlob);
					});
				} catch (error) {
					console.error('Error accessing microphone:', error);
				}
			}
		}
	}

</script>

<div class="recording-section">
	<!-- <p>{displayText}</p> -->
	<div class="button-container">
		<button
			class="record-button"
			onclick={toggleRecording}
			class:recording={isRecording}
			disabled={isAnalyzing}
		>
			<img
				src={isRecording ? '/images/record-button-stop.svg' : '/images/record-button.svg'}
				alt="Record button"
			/>
		</button>
	</div>
	
</div>

<style>
	.recording-section {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
		width: 100%;
		justify-content: center;
	}


	.button-container {
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.record-button {
		background: none;
		border: none;
		cursor: pointer;
		transition: transform 0.2s;
		padding: 0;
	}

	.record-button:hover {
		transform: scale(1.05);
	}

	.record-button.recording {
		animation: pulse 1s infinite;
	}

	.record-button img {
		width: 100px;
		height: 100px;
	}

	@keyframes pulse {
		0% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.1);
		}
		100% {
			transform: scale(1);
		}
	}

</style>