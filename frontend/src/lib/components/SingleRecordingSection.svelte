<!-- SingleRecordingSection.svelte -->
<script lang="ts">
	import { sendToEndpoint, type EndpointType } from '$lib/utils/apiHelpers';

	let { endpoint = 'analyze' as EndpointType } = $props();

	let apiResponse = $state('');
	let isAnalyzing = $state(false);
	let isRecording = $state(false);
	let mediaRecorder = $state<MediaRecorder | null>(null);
	let audioChunks = $state<Blob[]>([]);

	async function handleRecordingStop(audioBlob: Blob) {
		// Send audio to the specified endpoint
		isAnalyzing = true;
		const formData = new FormData();
		formData.append('file', audioBlob, 'recording.wav');

		try {
			const result = await sendToEndpoint(endpoint, formData);
			console.log('API response:', result);
			apiResponse = JSON.stringify(result, null, 2);
		} catch (error) {
			console.error('API error:', error);
			apiResponse = `Error: ${error instanceof Error ? error.message : 'Unknown error'}`;
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
	
	{#if apiResponse}
		<div class="api-response">
			<h3>API Response:</h3>
			<pre>{apiResponse}</pre>
		</div>
	{/if}
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

	.api-response {
		margin-top: 2rem;
		padding: 1rem;
		background: #f8f9fa;
		border: 1px solid #dee2e6;
		border-radius: 8px;
		max-width: 600px;
		width: 100%;
	}

	.api-response h3 {
		margin: 0 0 1rem 0;
		color: #333;
	}

	.api-response pre {
		background: #ffffff;
		padding: 1rem;
		border-radius: 4px;
		overflow-x: auto;
		font-size: 0.9rem;
		margin: 0;
		white-space: pre-wrap;
		word-wrap: break-word;
	}
</style>