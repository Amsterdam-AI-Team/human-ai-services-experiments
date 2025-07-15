<script>
	import MainMessage from '$lib/components/MainMessage.svelte';
	import CalloutBubble from '$lib/components/CalloutBubble.svelte';

	let isRecording = $state(false);
	let mediaRecorder = $state();
	let audioChunks = $state([]);
	let transcriptionText = $state('');
	let isTranscribing = $state(false);
	let hasTranscribed = $state(false);
	let datumChecked = $state(false);

	async function toggleRecording() {
		if (isRecording) {
			if (mediaRecorder && mediaRecorder.state !== 'inactive') {
				mediaRecorder.stop();
				mediaRecorder.stream.getTracks().forEach((track) => track.stop());
			}
		} else {
			if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
				try {
					const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
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

						// Transcribe audio
						isTranscribing = true;
						const formData = new FormData();
						formData.append('audio', audioBlob);

						try {
							const response = await fetch('/1/construct/transcribe', {
								method: 'POST',
								body: formData
							});

							const result = await response.json();
							console.log('Server response:', result);

							if (result.success && result.transcription) {
								transcriptionText = result.transcription;
								hasTranscribed = true;
								datumChecked = true;
							} else {
								console.error('Transcription failed:', result);
							}
						} catch (error) {
							console.error('Transcription error:', error);
						} finally {
							isTranscribing = false;
						}
					});
				} catch (error) {
					console.error('Error accessing microphone:', error);
				}
			}
		}
	}

	const displayText = $derived(
		isTranscribing
			? 'Bezig met transcriberen...'
			: 'Klik om te starten met opnemen, spreek gewoon wat in!'
	);
</script>

<main class="app">
	<div class="layout">
		<div class="left-section">
			<div class="chat-container">
				<div class="chat-message gemeente-ai">
					<div class="message-header">
						<img src="/images/logo-sketchy.svg" alt="Gemeente AI" class="message-logo" />
						<span class="sender-name">Gemeente AI:</span>
					</div>
					<div class="message-content">
						<p>Omschrijf wat er precies is gebeurd, vraag het vooral als er iets onduidelijk is.</p>
						<p>
							Rechts zie je een checklist van dingen die we nodig hebben om je bezwaar te
							behandelen.
						</p>
					</div>
				</div>

				{#if isTranscribing || transcriptionText}
					<div class="chat-message user-message">
						<div class="message-content">
							{#if isTranscribing}
								<p class="transcribing-text">Bezig met transcriberen...</p>
							{:else}
								<p>{transcriptionText}</p>
							{/if}
						</div>
					</div>
				{/if}

				<!-- {#if !hasTranscribed}
					<CalloutBubble
						text="Vertel over de dingen in de checklist en we gaan aan de slag"
					/>
				{/if} -->

				<div class="recording-section">
					<div class="button-container">
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
					</div>
				</div>
			</div>
		</div>
		<div class="right-section">
			<div class="content-section">
				<h1>
					We denken dat je bezwaar voor een parkeerboete wil maken. Laten we dit samen doen.
					<span class="edit-option">
						<span class="edit-text">dit is niet wat ik wil</span>
						<img src="/images/pencil.svg" alt="Edit" class="pencil-icon" />
					</span>
				</h1>

				<div class="form-section">
					<h2>Vertel ons deze dingen voor een complete aanvraag:</h2>

					<div class="checkbox-group">
						<label class="checkbox-item">
							<input type="checkbox" bind:checked={datumChecked} />
							<span>de datum van de bon</span>
						</label>

						<label class="checkbox-item">
							<input type="checkbox" />
							<span>het kenteken van de auto</span>
						</label>

						<label class="checkbox-item">
							<input type="checkbox" />
							<span>de reden van je bezwaar</span>
						</label>
					</div>
				</div>
			</div>
		</div>
	</div>
</main>

<style>
	.app {
		height: calc(100vh - 100px);
		background-color: #f8f9fa;
		display: flex;
		flex-direction: column;
	}

	.layout {
		flex: 1;
		display: flex;
		height: 100%;
	}

	.left-section {
		flex: 1;
		background-color: #f8f9fa;
		display: flex;
		flex-direction: column;
		padding: 2rem;
		overflow: hidden;
	}

	.chat-container {
		flex: 1;
		display: flex;
		flex-direction: column;
		justify-content: flex-end;
		gap: 1rem;
	}

	.chat-message {
		background: white;
		border-radius: 12px;
		padding: 1rem;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		border: 1px solid #e0e0e0;
		max-width: 80%;
		align-self: flex-start;
	}

	.chat-message.gemeente-ai {
		background: white;
		align-self: flex-start;
	}

	.chat-message.user-message {
		background: #f5f5f5;
		align-self: flex-end;
		border: 1px solid #ddd;
	}

	.message-header {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 0.5rem;
	}

	.message-logo {
		width: 20px;
		height: 20px;
		object-fit: contain;
	}

	.sender-name {
		font-weight: bold;
		color: #1864ab;
		font-size: 0.9rem;
	}

	.message-content {
		color: #333;
		line-height: 1.4;
	}

	.message-content p {
		margin: 0 0 0.5rem 0;
		font-size: 0.9rem;
	}

	.message-content p:last-child {
		margin-bottom: 0;
	}

	.callout-bubble {
		background: #f0f8ff;
		border: 1px solid #d4e6f1;
		border-radius: 8px;
		padding: 1rem;
		text-align: center;
		margin: 1rem 0;
	}

	.callout-bubble p {
		margin: 0;
		font-size: 1rem;
		color: #333;
		font-style: italic;
	}

	.recording-section {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
		width: 100%;
		justify-content: center;
	}

	.transcribing-text {
		font-style: italic;
		color: #666;
		margin: 0 0 0.5rem 0;
		font-size: 0.9rem;
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

	.right-section {
		flex: 2;
		background-color: #ffffff;
		padding: 2rem;
		overflow: hidden;
	}

	.content-section {
		height: 100%;
		display: flex;
		flex-direction: column;
		max-width: 750px;
	}

	.content-section h1 {
		font-size: 2rem;
		color: #333;
		margin: 0 0 2rem 0;
		line-height: 1.3;
	}

	.edit-option {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		margin-left: 0.5rem;
		cursor: pointer;
		vertical-align: baseline;
	}

	.pencil-icon {
		width: 16px;
		height: 16px;
		object-fit: contain;
		transform: translateY(-0.1em) translateX(-0.1em);
	}

	.edit-text {
		font-size: 0.9rem;
		color: #1864ab;
		position: relative;
		text-decoration: none;
		transform: translateY(-0.2em);
	}

	.edit-text::after {
		content: '';
		position: absolute;
		left: 0;
		bottom: -3px;
		width: 100%;
		height: 1px;
		background-color: #1864ab;
	}

	.form-section {
		background-color: rgba(255, 20, 147, 0.5);
		padding: 1.5rem;
		border-radius: 8px;
	}

	.form-section h2 {
		font-size: 1.2rem;
		color: #333;
		margin: 0 0 1.5rem 0;
		font-weight: normal;
	}

	.checkbox-group {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.checkbox-item {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		cursor: default;
		font-size: 1rem;
		color: #333;
		pointer-events: none;
	}

	.checkbox-item input[type='checkbox'] {
		width: 18px;
		height: 18px;
		accent-color: #1864ab;
	}

	.checkbox-item span {
		line-height: 1.4;
	}

	p {
		font-size: 1.2rem;
		color: #666;
		margin: 0;
	}

	@media (max-width: 768px) {
		.layout {
			flex-direction: column;
		}

		.left-section {
			flex: none;
			height: auto;
		}

		.right-section {
			flex: 1;
		}
	}
</style>
