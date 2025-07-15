<script>
	import MainMessage from '$lib/components/MainMessage.svelte';
	import ButtonSketchy from '$lib/components/ButtonSketchy.svelte';

	let isRecording = $state(false);
	let mediaRecorder = $state();
	let audioChunks = $state([]);
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
					console.error('Error accessing microphone:', error);
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
		? 'Bezig met transcriberen...' 
		: (transcriptionText.length > 0 ? 'Voeg een opname toe of ga door met aanvragen' : 'Klik om te starten met opnemen'));

	async function transcribeAudio(audioBlob) {
		isTranscribing = true;

		const formData = new FormData();
		formData.append('audio', audioBlob);

		try {
			const response = await fetch('/2/record/transcribe', {
				method: 'POST',
				body: formData
			});

			const result = await response.json();
			console.log('Server response:', result);

			if (result.success && result.transcription) {
				// Append transcription to existing text
				if (transcriptionText.length > 0) {
					transcriptionText += ' ' + result.transcription;
				} else {
					transcriptionText = result.transcription;
				}
			} else {
				console.error('Transcription failed:', result);
			}
		} catch (error) {
			console.error('Transcription error:', error);
		} finally {
			isTranscribing = false;
		}
	}
</script>

<main class="app">
	<div class="close-button" style="display: none;">
		<a href="/2">✕</a>
	</div>

	<div class="content">
		<MainMessage
			headerText="Inkomend bericht van jouw persoonlijke AI-agent:"
			mainText="Wat voor ideeën heb je al voor het buurtfeest? Dan nemen we die mee."
		/>

		<div class="tags">
			<span class="tag">🎉&nbsp;&nbsp;50 mensen</span>
			<span class="tag">🍾&nbsp;&nbsp;Champagnefontijn</span>
			<span class="tag">🎯&nbsp;&nbsp;Spelletjesmiddag</span>
			<span class="tag">🎵&nbsp;&nbsp;Grote band</span>
			<span class="tag">🎆&nbsp;&nbsp;Vuurwerkshow</span>
			<span class="tag">🍖&nbsp;&nbsp;Sparerib BBQ</span>
			<span class="tag">🚗&nbsp;&nbsp;Autoshow</span>
		</div>

		<div class="recording-section">
			<textarea
				class="ams-text-area"
				dir="auto"
				bind:value={transcriptionText}
				placeholder="Transcriptie verschijnt hier..."
			></textarea>
			<p>{displayText}</p>
			<div class="button-container">
				<div class="record-button-wrapper">
					<button
						class="record-button"
						on:click={toggleRecording}
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
					<ButtonSketchy text="aanvragen →" />
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
