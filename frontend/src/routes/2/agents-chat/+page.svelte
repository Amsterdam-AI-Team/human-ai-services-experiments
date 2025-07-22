<script lang="ts">
	import { _ } from "svelte-i18n";
	import { goto } from "$app/navigation";
	import ButtonSketchySecondary from "$lib/components/ButtonSketchySecondary.svelte";
	import ChatMessage from "$lib/components/ChatMessage.svelte";
	import {
		apiResponses,
		addApiResponse,
		clearApiResponsesForEndpoint,
	} from "$lib/stores/apiStore";
	import { sendToEndpoint } from "$lib/utils/apiHelpers";
	import { handleApiError } from "$lib/stores/errorStore";

	// Get the latest YAP response for the user's initial message
	const latestYapResponse = $derived(() => {
		const yapResponses = $apiResponses.filter((r) => r.endpoint === "yap");
		return yapResponses.length > 0
			? yapResponses[yapResponses.length - 1]
			: null;
	});

	// Get user message content from API response or fallback to hardcoded
	const userMessage = $derived(() => {
		const yapData = latestYapResponse();
		return (
			yapData?.data?.text ||
			"Ik wil een groot feest met 50 mensen, blauwe vlaggen en een sparerib BBQ"
		);
	});

	// Dynamic conversation state
	let conversation = $state<
		Array<{
			type: string;
			content: string;
			sender?: string;
			actions?: string[];
		}>
	>([]);

	// $effect(() => {
	// 	console.log(conversation);
	// });

	let yapSessionId = $state<string | null>(null);
	let isLoading = $state(false);
	let currentStep = $state(0); // For animating the process steps
	let isFinished = $state(false);

	// Process steps for animation
	const processSteps = [
		"📋 subsidie regels opzoeken",
		"✏️ voorstel schrijven",
		"💬 overleggen met gemeente AI-agent",
	];

	// Start the yap conversation when user message is available
	$effect(() => {
		const message = userMessage();
		if (
			message &&
			conversation.length === 0 &&
			!isLoading &&
			!yapSessionId
		) {
			startYapConversation(message);
		}
	});

	async function startYapConversation(message: string) {
		try {
			isLoading = true;
			currentStep = 0;

			// Start step animation
			animateSteps();

			// Call yap/start
			const result = await sendToEndpoint("yapStart", { text: message });
			addApiResponse("yapStart", result);

			if (result.yap_session_id) {
				yapSessionId = result.yap_session_id;
			}

			// Process messages from yapStart response
			if (result.messages && Array.isArray(result.messages)) {
				conversation = result.messages.map((msg: any) => ({
					type:
						msg.speaker === "burger"
							? "user-message"
							: "gemeente-ai",
					content: msg.message,
					sender:
						msg.speaker === "burger"
							? "Burger:"
							: "Gemeente AI-agent:",
				}));
			}

			// Continue with yap/next if not finished
			if (!result.finished) {
				// Add a small delay before next call to make conversation feel more natural
				setTimeout(() => continueYapConversation(), 1500);
			} else {
				isFinished = true;
				isLoading = false;
			}
		} catch (error) {
			handleApiError(error, "yapStart");
			isLoading = false;
		}
	}

	async function continueYapConversation() {
		if (!yapSessionId || isFinished) return;

		try {
			const result = await sendToEndpoint("yapNext", {
				yap_session_id: yapSessionId,
			});
			addApiResponse("yapNext", result);

			// Process full conversation from yapNext response
			if (result.messages && Array.isArray(result.messages)) {
				conversation = result.messages.map((msg: any) => ({
					type:
						msg.speaker === "burger"
							? "user-message"
							: "gemeente-ai",
					content: msg.message,
					sender:
						msg.speaker === "burger"
							? "Burger:"
							: "Gemeente AI-agent:",
				}));
			}

			// Continue if not finished
			if (!result.finished) {
				// Add a small delay before next call to make conversation feel more natural
				setTimeout(() => continueYapConversation(), 1500);
			} else {
				isFinished = true;
				isLoading = false;
			}
		} catch (error) {
			handleApiError(error, "yapNext");
			isLoading = false;
		}
	}

	function animateSteps() {
		const interval = setInterval(() => {
			if (currentStep < processSteps.length - 1) {
				currentStep++;
			} else {
				clearInterval(interval);
			}
		}, 1000); // Change step every second
	}

	let approvedResult = $state({
		title: 'Goedgekeurde subsidie: Buurtfeest "Samen aan Tafel" – €750',
		description:
			"Een duurzaam, inclusief buurtfeest voor 50 bewoners met een gemengde BBQ (biologische sparerib én plantaardige alternatieven), kleurrijke decoratie van gerecycled materiaal, en een knutselmiddag vooraf. Het feest bevordert saamhorigheid, culturele uitwisseling en milieubewustzijn. Toegang is gratis, met aandacht voor dieetvetsen en participatie van alle buurtbewoners.",
	});

	function goBack() {
		goto("/2");
	}

	function handleAction(action: string) {
		console.log("Action clicked:", action);
		// Here you would implement the actual action handling
	}

	function handleReset() {
		// Clear all YAP-related API responses
		clearApiResponsesForEndpoint("yap");
		clearApiResponsesForEndpoint("yapStart");
		clearApiResponsesForEndpoint("yapNext");

		// Navigate back to /2
		goto("/2");
	}
</script>

<main class="agents-chat">
	<header class="page-header">
		<ButtonSketchySecondary onclick={goBack} />
		<div class="status-indicator">
			{userMessage()}
		</div>
	</header>

	<div class="content">
		<h1 class="page-title">Buurtfeest subsidie aanvragen</h1>

		<div class="process-steps">
			{#each processSteps as step, index}
				<div
					class="step"
					class:active={index <= currentStep}
					class:bold={index === currentStep}
				>
					{step}
				</div>
			{/each}
		</div>

		<div class="conversation">
			{#each conversation as message}
				<div class="message-wrapper">
					<ChatMessage
						type={message.type === "user-message"
							? "user-message"
							: "gemeente-ai"}
						content={message.content}
						sender={message.sender}
					/>
					{#if message.actions}
						<div class="message-actions">
							{#each message.actions as action}
								<button
									class="action-button"
									onclick={() => handleAction(action)}
								>
									📝 {action}
								</button>
							{/each}
						</div>
					{/if}
				</div>
			{/each}
		</div>

		{#if isLoading && !isFinished}
			<div class="loading-indicator">
				<div class="loading-dots">
					<span>Gesprek wordt opgebouwd</span>
					<div class="dots">
						<span>.</span>
						<span>.</span>
						<span>.</span>
					</div>
				</div>
			</div>
		{/if}

		<div class="final-action">
			<button class="primary-button">↗ onderhandeling bekijken</button>
		</div>

		{#if isFinished}
			<div class="approved-result">
				<div class="approval-header">
					<span class="checkmark">✅</span>
					<h3>{approvedResult.title}</h3>
				</div>
				<div class="approval-subtitle">
					Omschrijving aangepast plan:
				</div>
				<p class="approval-description">{approvedResult.description}</p>
			</div>
		{/if}

		<div class="reset-section">
			<button class="reset-button" onclick={handleReset}>
				🔄 Reset conversation & return
			</button>
		</div>
	</div>
</main>

<style>
	.agents-chat {
		min-height: calc(100vh - 70px);
		background-color: #f8f9fa;
		font-family:
			system-ui,
			-apple-system,
			sans-serif;
		padding: 2rem;
	}

	.page-header {
		max-width: 1200px;
		margin: 0 auto 2rem auto;
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.status-indicator {
		background: #f3f4f6;
		padding: 0.5rem 1rem;
		border-radius: 4px;
		font-size: 0.875rem;
		color: #6b7280;
		flex: 1;
	}

	.content {
		max-width: 1200px;
		margin: 0 auto;
		width: 100%;
	}

	.page-title {
		font-size: 2.5rem;
		color: #333;
		margin: 0 0 3rem 0;
		font-weight: 700;
		text-align: center;
	}

	.process-steps {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		margin-bottom: 2rem;
	}

	.step {
		font-size: 0.875rem;
		color: #6b7280;
		padding: 0.25rem 0;
		transition: all 0.3s ease;
	}

	.step.active {
		color: #111827;
	}

	.step.bold {
		font-weight: 600;
	}

	.conversation {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
		margin-bottom: 2rem;
	}

	.message-wrapper {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.message-actions {
		margin-top: 1rem;
		display: flex;
		gap: 0.5rem;
	}

	.action-button {
		background: #3b82f6;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 4px;
		font-size: 0.875rem;
		cursor: pointer;
	}

	.action-button:hover {
		background: #2563eb;
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

	.final-action {
		text-align: center;
		margin-bottom: 2rem;
	}

	.primary-button {
		background: #3b82f6;
		color: white;
		border: none;
		padding: 0.75rem 1.5rem;
		border-radius: 4px;
		font-size: 0.875rem;
		cursor: pointer;
	}

	.primary-button:hover {
		background: #2563eb;
	}

	.approved-result {
		background: #f0fdf4;
		border: 2px solid #22c55e;
		border-radius: 8px;
		padding: 1.5rem;
	}

	.approval-header {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin-bottom: 0.75rem;
	}

	.checkmark {
		font-size: 1.25rem;
	}

	.approval-header h3 {
		margin: 0;
		font-size: 1.125rem;
		font-weight: 600;
		color: #16a34a;
	}

	.approval-subtitle {
		font-size: 0.875rem;
		color: #16a34a;
		font-weight: 600;
		margin-bottom: 0.5rem;
	}

	.approval-description {
		margin: 0;
		line-height: 1.6;
		color: #166534;
	}

	.reset-section {
		margin-top: 2rem;
		text-align: center;
		padding: 1rem;
		border-top: 1px solid #e5e7eb;
	}

	.reset-button {
		background: #6b7280;
		color: white;
		border: none;
		padding: 0.75rem 1.5rem;
		border-radius: 4px;
		font-size: 0.875rem;
		cursor: pointer;
		transition: background-color 0.2s;
	}

	.reset-button:hover {
		background: #4b5563;
	}

	@media (max-width: 768px) {
		.agents-chat {
			padding: 1rem;
		}

		.page-title {
			font-size: 2rem;
		}
	}
</style>
