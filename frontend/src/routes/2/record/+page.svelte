<script lang="ts">
	import MainMessage from '$lib/components/MainMessage.svelte';
	import ButtonSketchy from '$lib/components/ButtonSketchy.svelte';
	import { handleApiError, showTranslatedError } from '$lib/stores/errorStore';
	import { sendToEndpoint } from '$lib/utils/apiHelpers';
	import { addApiResponse } from '$lib/stores/apiStore';
	import { _ } from 'svelte-i18n';
	import { goto } from '$app/navigation';

	let isRecording = $state(false);
	let mediaRecorder = $state<MediaRecorder | undefined>();
	let audioChunks = $state<Blob[]>([]);
	let transcriptionText = $state('');
	let isTranscribing = $state(false);

	function startRecording() {
		if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
			navigator.mediaDevices
				.getUserMedia({ audio: true })
				.then((stream) => {
					mediaRecorder = new MediaRecorder(stream);
					mediaRecorder.start();
					isRecording = true;

					mediaRecorder.addEventListener('dataavailable', (event) => {
						audioChunks.push(event.data);
					});

					mediaRecorder.addEventListener('stop', async () => {
						const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
						console.log('Recording stopped', audioBlob);
						audioChunks = [];
						isRecording = false;

						// Start transcription
						await transcribeAudio(audioBlob);
					});
				})
				.catch((error) => {
					handleApiError(error, 'microphoneAccess');
				});
		}
	}

	function stopRecording() {
		if (mediaRecorder && mediaRecorder.state !== 'inactive') {
			mediaRecorder.stop();
			mediaRecorder.stream.getTracks().forEach((track) => track.stop());
		}
	}

	function toggleRecording() {
		if (isRecording) {
			stopRecording();
		} else {
			startRecording();
		}
	}

	const displayText = $derived(isTranscribing 
		? $_('recording.transcribing') 
		: (transcriptionText.length > 0 ? $_('recording.addRecording') : $_('recording.startRecording')));

	async function transcribeAudio(audioBlob) {
		isTranscribing = true;

		const formData = new FormData();
		formData.append('audio', audioBlob, 'recording.wav');
		
		// Add existing transcript for incremental building
		if (transcriptionText.length > 0) {
			formData.append('text', transcriptionText);
			console.log('Sending existing transcript:', transcriptionText);
		}

		try {
			const result = await sendToEndpoint('yap', formData);
			console.log('YAP API response:', result);
			
			// Store the response in the API store
			addApiResponse('yap', result);

			if (result.text) {
				// Replace the entire transcript with the accumulated result
				transcriptionText = result.text;
			} else {
				showTranslatedError('errors.transcriptionFailed');
			}
		} catch (error) {
			handleApiError(error, 'audioTranscription');
		} finally {
			isTranscribing = false;
		}
	}

	function handleContinue() {
		goto('/2/agents-chat');
	}
</script>

<main class="app">
	<div class="close-button" style="display: none;">
		<a href="/2">✕</a>
	</div>

	<div class="content">
		<MainMessage
			headerText={$_('messages.aiMessage')}
			mainText={$_('messages.ideas')}
		/>

		<div class="tags">
			<span class="tag">🎉&nbsp;&nbsp;{$_('concept2.tags.people')}</span>
			<span class="tag">🍾&nbsp;&nbsp;{$_('concept2.tags.champagne')}</span>
			<span class="tag">🎯&nbsp;&nbsp;{$_('concept2.tags.games')}</span>
			<span class="tag">🎵&nbsp;&nbsp;{$_('concept2.tags.band')}</span>
			<span class="tag">🎆&nbsp;&nbsp;{$_('concept2.tags.fireworks')}</span>
			<span class="tag">🍖&nbsp;&nbsp;{$_('concept2.tags.bbq')}</span>
			<span class="tag">🚗&nbsp;&nbsp;{$_('concept2.tags.carshow')}</span>
		</div>

		<div class="recording-section">
			<textarea
				class="ams-text-area"
				dir="auto"
				bind:value={transcriptionText}
				placeholder={$_('recording.placeholder')}
			></textarea>
			<p>{displayText}</p>
			<div class="button-container">
				<div class="record-button-wrapper">
					<button
						class="record-button"
						onclick={toggleRecording}
						class:recording={isRecording}
						disabled={isTranscribing}
					>
						<img
							src={isRecording ? '/images/record-button-stop.svg' : '/images/record-button.svg'}
							alt="Record button"
						/>
					</button>
					{#if transcriptionText.length > 0}
						<span class="plus-symbol">+</span>
					{/if}
				</div>
				{#if transcriptionText.length > 0}
					<ButtonSketchy text={$_('buttons.continue')} onclick={handleContinue} />
				{/if}
			</div>
		</div>
	</div>
</main>

<style>
	.app {
		height: 100vh;
		background-color: #f8f9fa;
		display: flex;
		flex-direction: column;
		position: relative;
	}

	.close-button {
		position: absolute;
		top: 2rem;
		left: 2rem;
		z-index: 10;
	}

	.close-button a {
		font-size: 2rem;
		color: #dc3545;
		text-decoration: none;
		font-weight: bold;
	}

	.content {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: start;
		justify-content: center;
		padding: 2rem;
		text-align: center;
		width: 1200px;
		margin: auto;
	}

	.tags {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem;
		justify-content: flex-start;
		margin-bottom: 4rem;
		width: 1400px;
		margin-left: -100px;
	}

	.tag {
		background-color: #e9ecef;
		padding: 0.8rem 1.5rem;
		border-radius: 25px;
		font-size: 1.1rem;
		color: #495057;
		border: 1px solid #dee2e6;
	}

	.recording-section {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
		width: 100%;
		justify-content: center;
	}

	.recording-section p {
		font-size: 1.1rem;
		color: #666;
		margin: 0;
	}

	.button-container {
		display: flex;
		align-items: center;
		gap: 2rem;
		justify-content: center;
	}

	.record-button-wrapper {
		position: relative;
		display: inline-block;
	}

	.plus-symbol {
		position: absolute;
		top: -7px;
		right: -7px;
		background: #6c757d;
		color: white;
		border-radius: 50%;
		width: 22px;
		height: 22px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 16px;
		font-weight: bold;
		z-index: 10;
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

	@media (max-width: 768px) {
		.content {
			padding: 1rem;
		}

		h1 {
			font-size: 2rem;
		}

		.tags {
			gap: 0.5rem;
		}

		.tag {
			font-size: 0.8rem;
			padding: 0.4rem 0.8rem;
		}
	}
</style>
