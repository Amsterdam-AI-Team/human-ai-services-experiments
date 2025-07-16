<script lang="ts">
	import MainMessage from '$lib/components/MainMessage.svelte';
	import CalloutBubble from '$lib/components/CalloutBubble.svelte';
	import Pill from '$lib/components/Pill.svelte';
	import ChatMessage from '$lib/components/ChatMessage.svelte';
	import ChecklistCard from '$lib/components/ChecklistCard.svelte';
	import ButtonSketchySmall from '$lib/components/ButtonSketchySmall.svelte';

	let isRecording = $state(false);
	let mediaRecorder = $state<MediaRecorder | null>(null);
	let audioChunks = $state<Blob[]>([]);
	let transcriptionText = $state('');
	let isTranscribing = $state(false);

	// Checklist items
	let checklistItems = $state([
		{ id: 'datum', text: 'de datum van de bon', checked: false },
		{ id: 'kenteken', text: 'het kenteken van de auto', checked: false },
		{ id: 'reden', text: 'de reden van je bezwaar', checked: false }
	]);

	function handleChecklistChange(id: string, checked: boolean) {
		const item = checklistItems.find((item) => item.id === id);
		if (item) {
			item.checked = checked;
		}
	}

	async function toggleRecording() {
		if (isRecording) {
			if (mediaRecorder && mediaRecorder.state !== 'inactive') {
				mediaRecorder.stop();
				mediaRecorder.stream.getTracks().forEach((track: MediaStreamTrack) => track.stop());
			}
		} else {
			if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
				try {
					const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
					mediaRecorder = new MediaRecorder(stream);
					mediaRecorder.start();
					isRecording = true;

					mediaRecorder.addEventListener('dataavailable', (event: BlobEvent) => {
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
								// Auto-check the first item when transcription is received
								handleChecklistChange('datum', true);
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
			<div class="pill-container">
				<Pill 
					icon="/images/document.svg" 
					text="Parkeerboete bezwaarformulier"
					onclick={() => console.log('Pill clicked')}
				/>
			</div>
			
			<div class="chat-container">
				<ChatMessage 
					type="gemeente-ai" 
					content="Hier is het bezwaarformulier voor een parkeerboete. Vertel ons wat er is gebeurd dan zal ik je helpen met het invullen van het formulier.\n\nRechts zie je een checklist van dingen die we nodig hebben om je bezwaar te behandelen. Laat het weten als je vragen hebt over het invullen van je bezwaar!" 
					sender="Gemeente AI-agent:"
				/>

				{#if isTranscribing || transcriptionText}
					<ChatMessage 
						type="user-message" 
						content={isTranscribing ? 'Bezig met transcriberen...' : transcriptionText}
					/>
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
							onclick={toggleRecording}
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
				<h1>Parkeerboete bezwaarschrift</h1>

				<ChecklistCard 
					items={checklistItems}
					onItemChange={handleChecklistChange}
				/>

				<div class="form-section">
					<h2>Dit ga je opsturen:</h2>
					
					<div class="form-field">
						<label class="field-label" for="bezwaar-textarea">Betreft: Bezwaar tegen parkeerboete</label>
						<textarea 
							id="bezwaar-textarea"
							class="field-input"
							placeholder="Omschrijf je situatie"
							rows="6"
						></textarea>
					</div>
				</div>

				<div class="submit-section">
					<ButtonSketchySmall text="Bezwaar versturen" />
				</div>
			</div>
		</div>
	</div>
</main>

<style>
	.app {
		height: calc(100vh - 140px);
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
		padding: 0rem 2rem;
		overflow: hidden;
		gap: 1rem;
	}

	.pill-container {
		display: flex;
		justify-content: flex-start;
		margin-bottom: 1rem;
	}

	.chat-container {
		flex: 1;
		display: flex;
		flex-direction: column;
		justify-content: flex-end;
		gap: 1rem;
		margin-bottom: 1rem;
	}



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
		width: 80px;
		height: 80px;
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
		padding: 0rem 2rem;
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
		font-weight: 600;
	}


	.form-section {
		margin-bottom: 2rem;
	}

	.form-section h2 {
		font-size: 1.2rem;
		color: #333;
		margin: 0 0 1.5rem 0;
		font-weight: 600;
	}

	.form-field {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.field-label {
		font-weight: 600;
		color: #333;
		font-size: 1rem;
	}

	.field-input {
		padding: 1rem;
		border: 1px solid #dee2e6;
		border-radius: 8px;
		font-size: 1rem;
		line-height: 1.5;
		resize: vertical;
		font-family: inherit;
	}

	.field-input:focus {
		outline: none;
		border-color: #007bff;
		box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
	}

	.field-input::placeholder {
		color: #6c757d;
		font-style: italic;
	}

	.submit-section {
		display: flex;
		justify-content: flex-end;
		margin-top: 2rem;
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
