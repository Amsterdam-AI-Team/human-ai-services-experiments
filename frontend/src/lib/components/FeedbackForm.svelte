<script lang="ts">
	import SingleRecordingSection from "$lib/components/SingleRecordingSection.svelte";
	import ButtonSketchy from "$lib/components/ButtonSketchy.svelte";
	import { goto } from "$app/navigation";
	import { _ } from "svelte-i18n";
	import { handleApiError } from "$lib/stores/errorStore";
	import { getSessionId } from "$lib/stores/sessionStore";
	import { clearApiResponses, apiResponses } from "$lib/stores/apiStore";
	import { get } from "svelte/store";
	import {
		setLanguageFromAPI,
		shouldSwitchLanguage,
		setLanguage,
		currentLanguage,
	} from "$lib/stores/languageStore";
	import type { LanguageCode } from "$lib/i18n";
	import { Confetti } from "svelte-confetti";

	interface Props {
		concept: number;
	}

	let { concept }: Props = $props();

	let transcriptionText = $state("");
	let isSubmitting = $state(false);
	let isTranscribing = $state(false);
	let hasError = $state(false);
	let errorMessage = $state("");
	let showConfetti = $state(true);

	const displayText = $derived(
		isTranscribing
			? $_("recording.transcribing")
			: transcriptionText.length > 0
				? $_("recording.addRecording")
				: $_("recording.startRecording"),
	);

	// Watch for feedback-transcribe endpoint responses and update transcription
	$effect(() => {
		const responses = $apiResponses;
		const latestTranscribeResponse = responses
			.filter((r) => r.endpoint === "feedback-transcribe")
			.slice(-1)[0];

		if (latestTranscribeResponse?.data?.text) {
			transcriptionText = latestTranscribeResponse.data.text;
			isTranscribing = false;

			// Handle language detection from API response
			if (latestTranscribeResponse.data.language) {
				const detectedLang = latestTranscribeResponse.data
					.language as LanguageCode;
				if (shouldSwitchLanguage(detectedLang)) {
					setLanguageFromAPI(detectedLang);
				}
			}
		} else if (latestTranscribeResponse?.data?.error) {
			isTranscribing = false;
		}
	});

	function handleRecordingStateChange(
		recording: boolean,
		analyzing: boolean,
	) {
		isTranscribing = analyzing;
	}

	async function handleSubmit() {
		if (!transcriptionText.trim()) {
			hasError = true;
			errorMessage = $_("feedback.errorEmpty");
			return;
		}

		isSubmitting = true;
		hasError = false;

		try {
			const currentSessionId = getSessionId();
			const lang = get(currentLanguage);
			const requestBody: any = {
				feedback: transcriptionText.trim(),
				concept: concept,
			};

			if (currentSessionId) {
				requestBody.session_id = currentSessionId;
			}
			
			if (lang) {
				requestBody.language = lang;
			}

			const response = await fetch("/api/feedback", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(requestBody),
			});

			const result = await response.json();

			if (response.ok) {
				goto(`/${concept}/final-thanks`);
			} else {
				hasError = true;
				errorMessage = result.error || $_("feedback.errorGeneric");
			}
		} catch (error) {
			hasError = true;
			errorMessage = $_("feedback.errorNetwork");
			handleApiError(error, "feedbackSubmission");
		} finally {
			isSubmitting = false;
		}
	}

	function handleClose() {
		clearApiResponses();
		setLanguage("nl");
		goto(`/${concept}`);
	}

	// Periodic confetti sparkle effect
	$effect(() => {
		const sparkleInterval = setInterval(() => {
			showConfetti = true;
			setTimeout(() => {
				showConfetti = false;
			}, 2000); // Duration matches the confetti duration
		}, 5000); 

		return () => clearInterval(sparkleInterval);
	});
</script>

<main class="app">
	<button class="close-button" onclick={handleClose} aria-label="Close">
		<svg
			width="24"
			height="24"
			viewBox="0 0 24 24"
			fill="none"
			xmlns="http://www.w3.org/2000/svg"
		>
			<path
				d="M18 6L6 18M6 6L18 18"
				stroke="white"
				stroke-width="2"
				stroke-linecap="round"
			/>
		</svg>
	</button>

	<div class="content">
		<div class="title-section">
			{#if showConfetti}
				<div class="confetti-container">
					<Confetti
						y={[-0.5, 0.5]}
						x={[-0.5, 0.5]}
						colorRange={[30, 50]}
						amount={25}
						fallDistance="10px"
						duration={2000}
						size={4}
					/>
				</div>
			{/if}
			<img
				src="/images/feedback-envelope.svg"
				alt="Feedback envelope"
				width="72"
				height="72"
			/>
			<h1 class="main-title">{$_("feedback.title")}</h1>
		</div>

		<p class="subtitle">{$_("feedback.subtitle")}</p>

		<div class="feedback-form">
			<textarea
				class="feedback-textarea"
				dir="auto"
				bind:value={transcriptionText}
				placeholder={$_("feedback.placeholder")}
				readonly
			></textarea>

			<p class="display-text">{displayText}</p>

			<div class="recording-section">
				<div class="record-button-wrapper">
					<SingleRecordingSection
						endpoint="feedback-transcribe"
						recordKey="e"
						onStateChange={handleRecordingStateChange}
						existingText={transcriptionText}
					/>
					{#if transcriptionText.length > 0}
						<span class="plus-symbol">+</span>
					{/if}
				</div>
				{#if transcriptionText.length > 0}
					<div class="verstuur-button-container">
						<div class="button-wrapper">
							<ButtonSketchy
								text={isSubmitting
									? $_("feedback.submitting")
									: $_("feedback.submit")}
								onclick={handleSubmit}
								disabled={isSubmitting || isTranscribing}
							/>
						</div>
						{#if !isSubmitting}
							<img
								src="/images/checkmark.svg"
								alt="checkmark"
								class="checkmark-icon"
							/>
						{/if}
					</div>
				{/if}
			</div>

			<div class="privacy-info">
				<ul>
					<li>{$_("feedback.privacy1")}</li>
					<li>{$_("feedback.privacy2")}</li>
				</ul>
			</div>

			{#if hasError}
				<div class="error-message">
					{errorMessage}
				</div>
			{/if}
		</div>
	</div>
</main>

<style>
	.app {
		height: 100vh;
		background-color: #343434;
		display: flex;
		flex-direction: column;
		position: relative;
		color: white;
		font-family: "Amsterdam Sans", sans-serif;
	}

	.close-button {
		position: absolute;
		top: 32px;
		right: 32px;
		background: none;
		border: none;
		cursor: pointer;
		padding: 8px;
		z-index: 10;
	}

	.close-button:hover {
		opacity: 0.8;
	}

	.content {
		flex: 1;
		display: flex;
		flex-direction: column;
		justify-content: center;
		max-width: 800px;
		margin: 0 auto;
		padding: 2rem;
	}

	.title-section {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin-bottom: 1.5rem;
		position: relative;
	}

	.confetti-container {
		position: absolute;
		top: 50%;
		left: 100%;
		transform: translate(-5%, -60%);
		width: 100%;
		height: 100%;
		pointer-events: none;
	}

	.main-title {
		font-size: 2.75rem;
		font-weight: 600;
		color: white;
		margin: 0;
		line-height: 1.2;
	}

	.subtitle {
		font-size: 1.25rem;
		color: rgba(255, 255, 255, 0.9);
		margin: 0 0 1rem 0;
		max-width: 600px;
		line-height: 1.4;
	}

	.feedback-form {
		width: 100%;
		max-width: 600px;
	}

	.feedback-textarea {
		width: 100%;
		min-height: 120px;
		padding: 1rem;
		border: 1px solid rgba(255, 255, 255, 0.3);
		background-color: rgba(255, 255, 255, 0.1);
		color: white;
		font-size: 1rem;
		font-family: "Amsterdam Sans", sans-serif;
		resize: vertical;
		margin-bottom: 1.5rem;
		border-radius: 4px;
	}

	.feedback-textarea::placeholder {
		color: rgba(255, 255, 255, 0.6);
		font-style: italic;
	}

	.feedback-textarea:focus {
		outline: none;
		border-color: rgba(255, 255, 255, 0.6);
		background-color: rgba(255, 255, 255, 0.15);
	}

	.display-text {
		font-size: 1.1rem;
		color: rgba(255, 255, 255, 0.8);
		margin: 0 0 1.5rem 0;
		text-align: center;
	}

	.recording-section {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 3rem;
		margin-bottom: 2rem;
	}

	.record-button-wrapper {
		position: relative;
		display: inline-block;
		flex-shrink: 0;
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

	.verstuur-button-container {
		position: relative;
		display: inline-block;
		transition: transform 0.1s ease;
	}

	.verstuur-button-container:hover {
		transform: translateY(-2px);
	}

	.button-wrapper {
		pointer-events: none;
	}

	.button-wrapper :global(.svg-button) {
		pointer-events: auto;
	}

	.button-wrapper :global(.svg-button:hover:not(:disabled)) {
		transform: none !important;
	}

	.button-wrapper :global(.svg-button:hover:not(:disabled) .button-svg) {
		filter: brightness(1.1);
	}

	.checkmark-icon {
		position: absolute;
		top: 45%;
		right: 4rem;
		transform: translateY(-50%) scale(2.5);
		height: 20px;
		pointer-events: none;
		z-index: 11;
	}

	.privacy-info {
		text-align: left;
		margin-bottom: 2rem;
	}

	.privacy-info ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.privacy-info li {
		position: relative;
		padding-left: 1.5rem;
		margin-bottom: 0.75rem;
		font-size: 0.95rem;
		color: rgba(255, 255, 255, 0.8);
		line-height: 1.4;
	}

	.privacy-info li::before {
		content: "•";
		position: absolute;
		left: 0;
		color: rgba(255, 255, 255, 0.6);
	}

	.error-message {
		background-color: rgba(220, 38, 38, 0.2);
		border: 1px solid rgba(220, 38, 38, 0.4);
		color: #fca5a5;
		padding: 1rem;
		border-radius: 4px;
		margin-bottom: 2rem;
		text-align: center;
		font-size: 0.95rem;
	}

	@media (max-width: 768px) {
		.content {
			padding: 1rem;
		}

		.main-title {
			font-size: 2.5rem;
		}

		.subtitle {
			font-size: 1.1rem;
		}

		.recording-section {
			flex-direction: column;
			gap: 2rem;
		}

		.close-button {
			top: 16px;
			right: 16px;
		}
	}
</style>
