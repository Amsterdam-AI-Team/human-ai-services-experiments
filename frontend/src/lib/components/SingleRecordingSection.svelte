<!-- SingleRecordingSection.svelte -->
<script lang="ts">
	import { sendToEndpoint, type EndpointType } from '$lib/utils/apiHelpers';
	import { addApiResponse } from '$lib/stores/apiStore';
	import { getSessionId } from '$lib/stores/sessionStore';

	let { endpoint = 'analyze' as EndpointType, intentcode = null, recordKey = 'e' } = $props();

	let isAnalyzing = $state(false);
	let isRecording = $state(false);
	let mediaRecorder = $state<MediaRecorder | null>(null);
	let audioChunks = $state<Blob[]>([]);
	let keyPressed = $state(false);
	let keyPressTimer = $state<number | null>(null);
	let isHoldToTalk = $state(false);

	async function handleRecordingStop(audioBlob: Blob) {
		// Send audio to the specified endpoint
		isAnalyzing = true;
		const formData = new FormData();
		
		// TODO: API inconsistency - different endpoints expect different field names
		// analyze endpoint expects 'file', chat/yap endpoints expect 'audio'
		// When API becomes consistent, this can be simplified to always use the same field name
		const audioFieldName = endpoint === 'analyze' ? 'file' : 'audio';
		formData.append(audioFieldName, audioBlob, 'recording.wav');
		
		// Add intentcode to FormData if provided
		if (intentcode) {
			formData.append('intentcode', intentcode);
		}
		
		// Add session_id to FormData if it exists and endpoint is chat (using FormData mode)
		if (endpoint === 'chat') {
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

	async function startRecording() {
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

	async function stopRecording() {
		if (mediaRecorder && mediaRecorder.state !== 'inactive') {
			mediaRecorder.stop();
			mediaRecorder.stream.getTracks().forEach((track) => track.stop());
		}
	}

	async function toggleRecording() {
		if (isRecording) {
			await stopRecording();
		} else {
			await startRecording();
		}
	}

	function handleKeyDown(event: KeyboardEvent) {
		if (event.key.toLowerCase() === recordKey.toLowerCase() && !keyPressed && !isAnalyzing) {
			keyPressed = true;
			
			// Start timer for distinguishing between short press and hold
			keyPressTimer = window.setTimeout(() => {
				// Long press detected - start hold-to-talk
				isHoldToTalk = true;
				if (!isRecording) {
					startRecording();
				}
			}, 200); // 200ms threshold
		}
	}

	function handleKeyUp(event: KeyboardEvent) {
		if (event.key.toLowerCase() === recordKey.toLowerCase() && keyPressed) {
			keyPressed = false;
			
			if (keyPressTimer) {
				clearTimeout(keyPressTimer);
				keyPressTimer = null;
			}

			if (isHoldToTalk) {
				// End hold-to-talk
				isHoldToTalk = false;
				if (isRecording) {
					stopRecording();
				}
			} else {
				// Short press - toggle recording
				toggleRecording();
			}
		}
	}

	// Add keyboard event listeners when component mounts
	$effect(() => {
		window.addEventListener('keydown', handleKeyDown);
		window.addEventListener('keyup', handleKeyUp);

		return () => {
			window.removeEventListener('keydown', handleKeyDown);
			window.removeEventListener('keyup', handleKeyUp);
		};
	});

</script>

<div class="recording-section">
	<!-- <p>{displayText}</p> -->
	<div class="button-container">
		<button
			class="record-button"
			onclick={toggleRecording}
			class:recording={isRecording}
			class:keyboard-active={keyPressed}
			disabled={isAnalyzing}
		>
			<img
				src={isRecording ? '/images/record-button-stop.svg' : '/images/record-button.svg'}
				alt="Record button"
			/>
		</button>
	</div>
	
	<!-- {#if keyPressed}
		<p class="keyboard-hint">Press '{recordKey.toUpperCase()}' to record • Hold for push-to-talk</p>
	{/if} -->
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

	.record-button.keyboard-active {
		transform: scale(1.05);
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.5);
		border-radius: 50%;
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

	.keyboard-hint {
		margin-top: 1rem;
		font-size: 0.875rem;
		color: #666;
		text-align: center;
	}

</style>