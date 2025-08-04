<script lang="ts">
	import { _ } from "svelte-i18n";
	import { goto } from "$app/navigation";
	import ButtonSketchySecondary from "$lib/components/ButtonSketchySecondary.svelte";
	import ButtonSketchySmall from "$lib/components/ButtonSketchySmall.svelte";
	import ButtonNormal from "$lib/components/ButtonNormal.svelte";
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
			isPlaceholder?: boolean;
		}>
	>([]);

	let yapSessionId = $state<string | null>(null);
	let isLoading = $state(false);
	let currentStep = $state(0); // For animating the process steps
	let isFinished = $state(false);

	// Process steps for animation
	const processSteps = [
		{ icon: "/images/agent-icon-search.svg", text: "regels opzoeken" },
		{ icon: "/images/agent-icon-edit.svg", text: "voorstel schrijven" },
		{
			icon: "/images/agent-icon-agree.svg",
			text: "overleggen met gemeente AI-agent",
		},
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

			// Add gemeente-agent placeholder immediately
			conversation = [
				{
					type: "gemeente-ai",
					content: "schrijft antwoord...",
					sender: "Gemeente AI-agent:",
					isPlaceholder: true,
				},
			];

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
				// Add user-agent placeholder for next response
				conversation = [
					...conversation,
					{
						type: "user-message",
						content: "schrijft antwoord...",
						sender: "Burger:",
						isPlaceholder: true,
					},
				];

				// Add a small delay before next call to make conversation feel more natural
				setTimeout(() => continueYapConversation(), 1500);
			} else {
				// Remove any remaining placeholder before finishing
				conversation = conversation.filter((msg) => !msg.isPlaceholder);
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
				const newConversation = result.messages.map((msg: any) => ({
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

				conversation = newConversation;

				// Continue if not finished - add placeholder for next response
				if (!result.finished) {
					// Determine what type of response comes next
					const lastMessage =
						newConversation[newConversation.length - 1];
					const nextType =
						lastMessage.type === "gemeente-ai"
							? "user-message"
							: "gemeente-ai";
					const nextSender =
						nextType === "gemeente-ai"
							? "Gemeente AI-agent:"
							: "Burger:";

					conversation = [
						...conversation,
						{
							type: nextType,
							content: "schrijft antwoord...",
							sender: nextSender,
							isPlaceholder: true,
						},
					];

					// Add a small delay before next call to make conversation feel more natural
					setTimeout(() => continueYapConversation(), 1500);
				} else {
					// Remove any remaining placeholder before finishing
					conversation = conversation.filter(
						(msg) => !msg.isPlaceholder,
					);
					isFinished = true;
					isLoading = false;
				}
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

	// Auto-scroll to bottom when new content is added
	$effect(() => {
		if (conversation.length > 0) {
			requestAnimationFrame(() => {
				window.scrollTo({
					top: document.body.scrollHeight,
					behavior: "smooth",
				});
			});
		}
	});

	// Get the final approved result from the API response
	const approvedResult = $derived(() => {
		if (!isFinished) return null;

		// Get the latest yapNext response
		const yapNextResponses = $apiResponses.filter(
			(r) => r.endpoint === "yapNext",
		);
		const latestResponse =
			yapNextResponses.length > 0
				? yapNextResponses[yapNextResponses.length - 1]
				: null;

		if (!latestResponse?.data?.message) {
			return {
				title: 'Goedgekeurde subsidie: Buurtfeest "Samen aan Tafel" – €750',
				description:
					"Een duurzaam, inclusief buurtfeest voor 50 bewoners met een gemengde BBQ (biologische sparerib én plantaardige alternatieven), kleurrijke decoratie van gerecycled materiaal, en een knutselmiddag vooraf. Het feest bevordert saamhorigheid, culturele uitwisseling en milieubewustzijn. Toegang is gratis, met aandacht voor dieetvetsen en participatie van alle buurtbewoners.",
			};
		}

		const message = latestResponse.data.draft;
		const sentences = message.split(/(?<=\.)\s+/);
		const title = sentences[0] || message;
		const description = sentences.slice(1).join(" ").trim() || message;

		return {
			title,
			description,
		};
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

	function handleSubmit() {
		// Navigate to /2/end
		goto("/2/end");
	}
</script>

<main class="agents-chat">
	<header class="page-header">
		<ButtonSketchySecondary onclick={goBack} />
		<ChatMessage
			type="user-message"
			content={userMessage()}
			sender="Jouw agent"
		/>
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
					<img src={step.icon} alt="" class="step-icon" />
					{step.text}
				</div>
			{/each}
		</div>

		<div class="conversation-container">
			<div class="conversation-line"></div>
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
						<!-- {#if message.type === "user-message" && !message.isPlaceholder}
							<div class="user-button-wrapper">
								<ButtonNormal onclick={() => handleAction('wijziging')} />
							</div>
						{/if} -->
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
		</div>

		<!-- <div class="final-action">
			<button class="primary-button">↗ onderhandeling bekijken</button>
		</div> -->

		{#if isFinished && approvedResult()}
			{@const result = approvedResult()}
			<div class="approved-result">
				<div class="approval-header">
					<span class="checkmark">✅</span>
					<h3>{result?.title}</h3>
				</div>
				<div class="approval-subtitle">
					Omschrijving aangepast plan:
				</div>
				<p class="approval-description">{result?.description}</p>

				<div class="submit-section">
					<ButtonSketchySmall
						text={$_("buttons.submit")}
						onclick={handleSubmit}
					/>
				</div>
			</div>
		{/if}

		<!-- <div class="reset-section">
			<button class="reset-button" onclick={handleReset}>
				🔄 Reset conversation & return
			</button>
		</div> -->
	</div>
</main>

<style>
	.agents-chat {
		min-height: calc(100vh - 100px);
		background-color: #f8f9fa;
		font-family: "Amsterdam Sans", Arial, sans-serif;
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
		padding: 1rem;
		font-size: 1rem;
		flex: 1;
	}

	.user-style {
		background: #e5e5e5;
		text-align: right;
		font-size: 1rem;
		max-width: 300px;
		margin-left: auto;
	}

	.content {
		max-width: 1000px;
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
		font-size: 1rem;
		color: #6b7280;
		padding: 0.25rem 0;
		transition: all 0.3s ease;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.step-icon {
		width: 32px;
		height: 32px;
		flex-shrink: 0;
	}

	.step.active {
		color: #111827;
	}

	.step.bold {
		font-weight: 600;
	}

	.conversation-container {
		display: flex;
		align-items: flex-start;
		gap: 1rem;
		margin: 0 auto 2rem auto;
	}

	.conversation-line {
		width: 3px;
		background-color: #d1d5db;
		flex-shrink: 0;
		align-self: stretch;
		min-height: 200px;
	}

	.conversation {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
		flex: 1;
	}

	.message-wrapper {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
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
		font-size: 1rem;
		cursor: pointer;
		font-family: "Amsterdam Sans", Arial, sans-serif;
	}

	.action-button:hover {
		background: #2563eb;
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
		font-size: 1rem;
		cursor: pointer;
		font-family: "Amsterdam Sans", Arial, sans-serif;
	}

	.primary-button:hover {
		background: #2563eb;
	}

	.approved-result {
		background: #f0fdf4;
		border: 2px solid #22c55e;
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
		font-size: 0.875rem;
		cursor: pointer;
		transition: background-color 0.2s;
		font-family: "Amsterdam Sans", Arial, sans-serif;
	}

	.reset-button:hover {
		background: #4b5563;
	}

	.submit-section {
		display: flex;
		justify-content: flex-end;
		margin-top: 1.5rem;
	}

	.user-button-wrapper {
		display: flex;
		justify-content: flex-end;
		margin-top: 0.5rem;
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
