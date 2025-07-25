<script lang="ts">
	import Pill from "$lib/components/Pill.svelte";
	import ChatMessage from "$lib/components/ChatMessage.svelte";
	import ChecklistCard from "$lib/components/ChecklistCard.svelte";
	import ButtonSketchySmall from "$lib/components/ButtonSketchySmall.svelte";
	import ApiDebugger from "$lib/components/ApiDebugger.svelte";
	import SingleRecordingSection from "$lib/components/SingleRecordingSection.svelte";
	import { _ } from "svelte-i18n";
	import {
		apiResponses,
		addApiResponse,
		clearApiResponses,
	} from "$lib/stores/apiStore";
	import {
		setSessionId,
		getSessionId,
		clearSession,
		sessionData,
	} from "$lib/stores/sessionStore";
	import {
		handleApiError,
		showTranslatedError,
		showTranslatedWarning,
		showTranslatedInfo,
	} from "$lib/stores/errorStore";
	import { page } from "$app/state";
	import { goto } from "$app/navigation";

	// Get intentcode from URL slug
	const intentcode = $derived(page.params.slug);

	// Get the latest analyze response
	const latestAnalyzeResponse = $derived(() => {
		const analyzeResponses = $apiResponses.filter(
			(r) => r.endpoint === "analyze",
		);
		return analyzeResponses.length > 0
			? analyzeResponses[analyzeResponses.length - 1]
			: null;
	});

	// Get transcript from analyze endpoint
	const initialTranscript = $derived(() => {
		return latestAnalyzeResponse()?.data?.transcript || "";
	});

	// Find the matching intent object based on slug
	const matchingIntent = $derived(() => {
		const response = latestAnalyzeResponse();
		if (!response?.data?.matches) return null;

		return (
			response.data.matches.find(
				(match: any) => match.intent.intentcode === intentcode,
			) || null
		);
	});

	// Get the heading from the intent
	const intentHeading = $derived(() => {
		const intent = matchingIntent();
		return intent?.intent?.intent || "Formulier";
	});

	// Get chat endpoint responses for AI replies
	const chatResponses = $derived(() => {
		return $apiResponses.filter((r) => r.endpoint === "chat");
	});

	// Send transcript to chat endpoint
	async function sendTranscriptToChat(transcript: string) {
		try {
			isSendingChat = true;
			const currentSessionId = getSessionId();
			const requestBody: any = {
				message: transcript,
				intentcode: intentcode,
			};

			if (currentSessionId) {
				requestBody.session_id = currentSessionId;
			}

			const response = await fetch("/api/chat", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(requestBody),
			});

			const result = await response.json();
			addApiResponse("chat", result);

			// Store session_id from the first chat response
			if (result.session_id) {
				setSessionId(result.session_id);
			}
		} catch (error) {
			handleApiError(error, "chatSending");
		} finally {
			isSendingChat = false;
		}
	}

	// Track if we've already sent the transcript to chat
	let hasSentTranscript = $state(false);
	let isSendingChat = $state(false);
	
	// Chat scrolling references
	let chatContainer: HTMLElement;
	let shouldAutoScroll = $state(true);

	// Send transcript to chat when it becomes available, but only if no chat messages exist yet
	$effect(() => {
		const transcript = initialTranscript();
		const existingChatMessages = chatResponses();

		if (
			transcript &&
			!hasSentTranscript &&
			existingChatMessages.length === 0
		) {
			hasSentTranscript = true;
			sendTranscriptToChat(transcript);
		}
	});

	// Helper function to convert text to backend format
	function textToBackendId(text: string): string {
		return text.toLowerCase().replace(/\s+/g, "-");
	}

	// Get checklist items from the intent steps
	const checklistItems = $derived(() => {
		const intent = matchingIntent();
		if (!intent?.intent?.steps) return [];

		return intent.intent.steps.map((step: any) => ({
			id: textToBackendId(step.title),
			text: step.title,
			checked: false,
		}));
	});

	// Create a reactive state for checked items using backend IDs
	let checkedItems = $state(new Set<string>());

	// Get the latest checklist state from chat responses
	const latestChecklist = $derived(() => {
		const responses = chatResponses();
		if (responses.length === 0) return null;

		const latest = responses[responses.length - 1];
		return latest.data?.checklist || null;
	});

	// Get the latest draft text from checklist
	const draftText = $derived(() => {
		const checklist = latestChecklist();
		return checklist?.draft || "";
	});

	// Sync checklist state with backend responses
	$effect(() => {
		const backendChecklist = latestChecklist();
		if (backendChecklist) {
			const newCheckedItems = new Set<string>();

			// Add checked items from backend state
			Object.entries(backendChecklist).forEach(([key, value]) => {
				if (key !== "draft" && value === true) {
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

	// Auto-scroll to bottom when new messages arrive
	$effect(() => {
		const messages = chatResponses();
		const transcript = initialTranscript();
		
		if (chatContainer && shouldAutoScroll && (messages.length > 0 || transcript)) {
			requestAnimationFrame(() => {
				chatContainer.scrollTop = chatContainer.scrollHeight;
			});
		}
	});

	// Handle scroll to detect if user scrolled up
	function handleScroll() {
		if (!chatContainer) return;
		
		const { scrollTop, scrollHeight, clientHeight } = chatContainer;
		const isAtBottom = scrollTop + clientHeight >= scrollHeight - 10;
		shouldAutoScroll = isAtBottom;
	}


	function handleBezwaarVersturen() {
		// Clear all stores
		clearApiResponses();
		clearSession();

		// Navigate to /1/end
		goto("/1/end");
	}
</script>

<main class="app">
	<div class="layout">
		<div class="left-section">
			<div class="pill-container">
				<Pill
					icon="/images/document.svg"
					text="Parkeerboete bezwaarformulier"
					onclick={() => console.log("Pill clicked")}
				/>
			</div>

			<div class="chat-container" bind:this={chatContainer} onscroll={handleScroll}>
				<div class="chat-messages">
					{#if initialTranscript()}
						<div class="message-wrapper">
							<ChatMessage
								type="user-message"
								content={initialTranscript()}
							/>
						</div>
					{/if}

					{#each chatResponses() as response}
						{#if response.data?.reply}
							{#if initialTranscript() !== response.data.user_text}
								<div class="message-wrapper">
									<ChatMessage
										type="user-message"
										content={response.data.user_text}
									/>
								</div>
							{/if}
							<div class="message-wrapper">
								<ChatMessage
									type="gemeente-ai"
									content={response.data.reply}
									sender={$_("concept1.construct.senderAI")}
								/>
							</div>
						{/if}
					{/each}

					{#if isSendingChat}
						<div class="message-wrapper">
							<div class="loading-indicator">
								<div class="loading-dots">
									<span>{$_("concept1.construct.loadingAI")}</span>
									<div class="dots">
										<span>.</span>
										<span>.</span>
										<span>.</span>
									</div>
								</div>
							</div>
						</div>
					{/if}
				</div>
			</div>

			<!-- Recording section fixed at bottom -->
			<div class="recording-section">
				<SingleRecordingSection endpoint="chat" {intentcode} />
			</div>
		</div>
		<div class="right-section">
			<div class="content-section">
				<h1>{intentHeading()}</h1>

				<ChecklistCard
					items={checklistItems().map((item: any) => ({
						...item,
						checked: checkedItems.has(item.id),
					}))}
					onItemChange={handleChecklistChange}
				/>

				<div class="form-section">
					<h2>{$_("concept1.construct.formTitle")}</h2>

					<div class="form-field">
						<label class="field-label" for="bezwaar-textarea"
							>{$_("concept1.construct.formLabel")}</label
						>
						<textarea
							id="bezwaar-textarea"
							class="field-input"
							placeholder={$_(
								"concept1.construct.formPlaceholder",
							)}
							rows="6"
							value={draftText()}
							readonly
						></textarea>
					</div>
				</div>

				<div class="submit-section">
					<ButtonSketchySmall
						text={$_("buttons.submit")}
						onclick={handleBezwaarVersturen}
					/>
				</div>
			</div>
		</div>
	</div>

	<!-- Debug components -->
	<!-- <div style="display: flex; gap: 1rem; margin: 1rem; flex-wrap: wrap;"> -->
	<!-- <button onclick={clearSession} style="padding: 0.5rem; background: #ff4444; color: white; border: none; border-radius: 4px; cursor: pointer;">
			Clear Session ID: {$sessionData.sessionId ? $sessionData.sessionId.substring(0, 8) + '...' : 'None'}
		</button> -->

	<!-- Error Display Test Buttons -->
	<!-- <button onclick={() => showTranslatedError('errors.testError')} style="padding: 0.5rem; background: #dc2626; color: white; border: none; border-radius: 4px; cursor: pointer;">
			Test Error
		</button>
		<button onclick={() => showTranslatedWarning('errors.testWarning')} style="padding: 0.5rem; background: #d97706; color: white; border: none; border-radius: 4px; cursor: pointer;">
			Test Warning
		</button>
		<button onclick={() => showTranslatedInfo('errors.testInfo')} style="padding: 0.5rem; background: #2563eb; color: white; border: none; border-radius: 4px; cursor: pointer;">
			Test Info
		</button>
		<button onclick={() => handleApiError(new Error($_('errors.apiConnectionFailed')), 'apiCall')} style="padding: 0.5rem; background: #7c2d12; color: white; border: none; border-radius: 4px; cursor: pointer;">
			Test API Error
		</button>
		<button onclick={() => handleApiError(new Error($_('errors.transcriptionTimeout')), 'recordingAnalysis')} style="padding: 0.5rem; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer;">
			Test Recording Timeout
		</button> -->
	<!-- </div> -->
</main>

<!-- <ApiDebugger endpoint="analyze" /> -->
<!-- <ApiDebugger endpoint="chat" />	 -->

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
		margin-top: 15px;
		margin-bottom: 1rem;
	}

	.chat-container {
		flex: 1;
		display: flex;
		flex-direction: column-reverse; /* Bottom-anchored scrolling */
		overflow-y: auto;
		min-height: 0;
		padding: 0 0 1rem 0;
		scroll-behavior: smooth;
	}

	.chat-messages {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		padding-top: 1rem;
	}

	.message-wrapper {
		animation: slideInFromBottom 0.3s ease-out;
	}

	@keyframes slideInFromBottom {
		from {
			opacity: 0;
			transform: translateY(20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.recording-section {
		flex-shrink: 0; /* Don't shrink the recording section */
		padding: 1rem 0;
		border-top: 1px solid #e9ecef;
		background-color: #f8f9fa;
		margin-bottom: 70px; /* Move record button 70px higher */
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
		/* border-radius: 8px; */
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
		/* border-radius: 8px; */
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

	.dots span:nth-child(1) {
		animation-delay: -0.32s;
	}
	.dots span:nth-child(2) {
		animation-delay: -0.16s;
	}
	.dots span:nth-child(3) {
		animation-delay: 0s;
	}

	@keyframes pulse {
		0%,
		80%,
		100% {
			opacity: 0.3;
		}
		40% {
			opacity: 1;
		}
	}
</style>
