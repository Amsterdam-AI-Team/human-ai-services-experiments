<script lang="ts">
	import Pill from '$lib/components/Pill.svelte';
	import ChatMessage from '$lib/components/ChatMessage.svelte';
	import ChecklistCard from '$lib/components/ChecklistCard.svelte';
	import ButtonSketchySmall from '$lib/components/ButtonSketchySmall.svelte';
	import ApiDebugger from '$lib/components/ApiDebugger.svelte';
	import SingleRecordingSection from '$lib/components/SingleRecordingSection.svelte';
	import { apiResponses, addApiResponse, clearApiResponses } from '$lib/stores/apiStore';
	import { setSessionId, getSessionId, clearSession, sessionData } from '$lib/stores/sessionStore';
	import { handleApiError, showError, showWarning, showInfo } from '$lib/stores/errorStore';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';


	// Get intentcode from URL slug
	const intentcode = $derived(page.params.slug);

	// Get the latest analyze response
	const latestAnalyzeResponse = $derived(() => {
		const analyzeResponses = $apiResponses.filter(r => r.endpoint === 'analyze');
		return analyzeResponses.length > 0 ? analyzeResponses[analyzeResponses.length - 1] : null;
	});

	// Get transcript from analyze endpoint
	const initialTranscript = $derived(() => {
		return latestAnalyzeResponse()?.data?.transcript || '';
	});

	// Find the matching intent object based on slug
	const matchingIntent = $derived(() => {
		const response = latestAnalyzeResponse();
		if (!response?.data?.matches) return null;
		
		return response.data.matches.find((match: any) => match.intent.intentcode === intentcode) || null;
	});

	// Get the heading from the intent
	const intentHeading = $derived(() => {
		const intent = matchingIntent();
		return intent?.intent?.intent || 'Formulier';
	});

	// Get chatAudio responses for AI replies
	const chatAudioResponses = $derived(() => {
		return $apiResponses.filter(r => r.endpoint === 'chatAudio');
	});

	// Get chat endpoint responses for AI replies
	const chatResponses = $derived(() => {
		return $apiResponses.filter(r => r.endpoint === 'chat');
	});

	// Send transcript to chat endpoint
	async function sendTranscriptToChat(transcript: string) {
		try {
			isSendingChat = true;
			const currentSessionId = getSessionId();
			const requestBody: any = { 
				message: transcript, 
				intentcode: intentcode 
			};
			
			if (currentSessionId) {
				requestBody.session_id = currentSessionId;
			}
			
			const response = await fetch('/api/chat', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify(requestBody)
			});

			const result = await response.json();
			addApiResponse('chat', result);
			
			// Store session_id from the first chat response
			if (result.session_id) {
				setSessionId(result.session_id);
			}
		} catch (error) {
			handleApiError(error, 'Sending transcript to chat');
		} finally {
			isSendingChat = false;
		}
	}

	// Track if we've already sent the transcript to chat
	let hasSentTranscript = $state(false);
	let isSendingChat = $state(false);

	// Send transcript to chat when it becomes available, but only if no chat messages exist yet
	$effect(() => {
		const transcript = initialTranscript();
		const existingChatMessages = chatResponses();
		
		if (transcript && !hasSentTranscript && existingChatMessages.length === 0) {
			hasSentTranscript = true;
			sendTranscriptToChat(transcript);
		}
	});

	// Helper function to convert text to backend format
	function textToBackendId(text: string): string {
		return text.toLowerCase().replace(/\s+/g, '-');
	}

	// Get checklist items from the intent steps
	const checklistItems = $derived(() => {
		const intent = matchingIntent();
		if (!intent?.intent?.steps) return [];
		
		return intent.intent.steps.map((step: any) => ({
			id: textToBackendId(step.title),
			text: step.title,
			checked: false
		}));
	});

	// Create a reactive state for checked items using backend IDs
	let checkedItems = $state(new Set<string>());

	// Get the latest checklist state from chat responses
	const latestChecklist = $derived(() => {
		const responses = [...chatResponses(), ...chatAudioResponses()];
		if (responses.length === 0) return null;
		
		const latest = responses[responses.length - 1];
		return latest.data?.checklist || null;
	});

	// Get the latest draft text from checklist
	const draftText = $derived(() => {
		const checklist = latestChecklist();
		return checklist?.draft || '';
	});

	// Sync checklist state with backend responses
	$effect(() => {
		const backendChecklist = latestChecklist();
		if (backendChecklist) {
			const newCheckedItems = new Set<string>();
			
			// Add checked items from backend state
			Object.entries(backendChecklist).forEach(([key, value]) => {
				if (key !== 'draft' && value === true) {
					newCheckedItems.add(key);
				}
			});
			
			checkedItems = newCheckedItems;
		}
	});

	function handleChecklistChange(id: string, checked: boolean) {
		if (checked) {
			checkedItems.add(id);
		} else {
			checkedItems.delete(id);
		}
		checkedItems = new Set(checkedItems); // Trigger reactivity
	}

	function handleBezwaarVersturen() {
		// Clear all stores
		clearApiResponses();
		clearSession();
		
		// Navigate back to /1
		goto('/1');
	}

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
				{#if initialTranscript()}
					<ChatMessage 
						type="user-message" 
						content={initialTranscript()}
					/>
				{/if}

				{#if isSendingChat}
					<div class="loading-indicator">
						<div class="loading-dots">
							<span>AI is processing your request</span>
							<div class="dots">
								<span>.</span>
								<span>.</span>
								<span>.</span>
							</div>
						</div>
					</div>
				{/if}

				{#each chatResponses() as response}
					{#if response.data?.reply}
						<ChatMessage 
							type="gemeente-ai" 
							content={response.data.reply}
							sender="Gemeente AI-agent:"
						/>
					{/if}
				{/each}

				{#each chatAudioResponses() as response}
					{#if response.data?.reply}
						<ChatMessage 
							type="gemeente-ai" 
							content={response.data.reply}
							sender="Gemeente AI-agent:"
						/>
					{/if}
				{/each}
			</div>
			
			<!-- Recording section fixed at bottom -->
			<div class="recording-section">
				<SingleRecordingSection endpoint="chatAudio" intentcode={intentcode} />
			</div>
		</div>
		<div class="right-section">
			<div class="content-section">
				<h1>{intentHeading()}</h1>

				<ChecklistCard 
					items={checklistItems().map((item: any) => ({
						...item,
						checked: checkedItems.has(item.id)
					}))}
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
							value={draftText()}
							readonly
						></textarea>
					</div>
				</div>

				<div class="submit-section">
					<ButtonSketchySmall text="Bezwaar versturen" onclick={handleBezwaarVersturen} />
				</div>
			</div>
		</div>
	</div>
	
	<!-- Debug components -->
	<div style="display: flex; gap: 1rem; margin: 1rem; flex-wrap: wrap;">
		<button onclick={clearSession} style="padding: 0.5rem; background: #ff4444; color: white; border: none; border-radius: 4px; cursor: pointer;">
			Clear Session ID: {$sessionData.sessionId ? $sessionData.sessionId.substring(0, 8) + '...' : 'None'}
		</button>
		
		<!-- Error Display Test Buttons -->
		<button onclick={() => showError('Dit is een test foutmelding')} style="padding: 0.5rem; background: #dc2626; color: white; border: none; border-radius: 4px; cursor: pointer;">
			Test Error
		</button>
		<button onclick={() => showWarning('Dit is een test waarschuwing')} style="padding: 0.5rem; background: #d97706; color: white; border: none; border-radius: 4px; cursor: pointer;">
			Test Warning
		</button>
		<button onclick={() => showInfo('Dit is een test informatie bericht')} style="padding: 0.5rem; background: #2563eb; color: white; border: none; border-radius: 4px; cursor: pointer;">
			Test Info
		</button>
		<button onclick={() => handleApiError(new Error('API verbinding mislukt'), 'Test API call')} style="padding: 0.5rem; background: #7c2d12; color: white; border: none; border-radius: 4px; cursor: pointer;">
			Test API Error
		</button>
	</div>
</main>
<ApiDebugger endpoint="analyze" />
<ApiDebugger endpoint="chat" />
<ApiDebugger endpoint="chatAudio" />

<style>
	.app {
		background-color: #f8f9fa;
		display: flex;
		flex-direction: column;
		min-height: calc(100vh - 70px); /* Account for header */
	}

	.layout {
		display: flex;
		height: calc(100vh - 70px); /* Fixed height for the main layout */
	}

	.left-section {
		flex: 1;
		background-color: #f8f9fa;
		display: flex;
		flex-direction: column;
		padding: 0rem 2rem;
		height: 100%;
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
		gap: 1rem;
		overflow-y: auto; /* Make chat area scrollable */
		min-height: 0; /* Allow flexbox to shrink */
		padding-bottom: 1rem;
	}

	.recording-section {
		flex-shrink: 0; /* Don't shrink the recording section */
		padding: 1rem 0;
		border-top: 1px solid #e9ecef;
		background-color: #f8f9fa;
		margin-bottom: 50px; /* Move record button 50px higher */
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

	.loading-indicator {
		padding: 1rem;
		margin: 0.5rem 0;
		background-color: #f8f9fa;
		border-radius: 8px;
		border-left: 4px solid #007bff;
	}

	.loading-dots {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		color: #666;
		font-style: italic;
	}

	.dots {
		display: flex;
		gap: 0.2rem;
	}

	.dots span {
		animation: pulse 1.4s ease-in-out infinite both;
	}

	.dots span:nth-child(1) { animation-delay: -0.32s; }
	.dots span:nth-child(2) { animation-delay: -0.16s; }
	.dots span:nth-child(3) { animation-delay: 0s; }

	@keyframes pulse {
		0%, 80%, 100% { 
			opacity: 0.3; 
		}
		40% { 
			opacity: 1; 
		}
	}
</style>
