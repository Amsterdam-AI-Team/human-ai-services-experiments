<script lang="ts">
	import SingleRecordingSection from "$lib/components/SingleRecordingSection.svelte";
	import ButtonSketchy from "$lib/components/ButtonSketchy.svelte";
	import { goto } from "$app/navigation";
	import { _ } from "svelte-i18n";
	import { handleApiError } from "$lib/stores/errorStore";
	import { getSessionId } from "$lib/stores/sessionStore";
	import { clearApiResponses } from "$lib/stores/apiStore";

	interface Props {
		concept: number;
	}

	let { concept }: Props = $props();

	let feedbackText = $state("");
	let isSubmitting = $state(false);
	let isRecording = $state(false);
	let hasError = $state(false);
	let errorMessage = $state("");

	function handleRecordingStateChange(
		recording: boolean,
		analyzing: boolean,
	) {
		isRecording = recording || analyzing;
	}

	async function handleSubmit() {
		if (!feedbackText.trim()) {
			hasError = true;
			errorMessage = $_("feedback.errorEmpty");
			return;
		}

		isSubmitting = true;
		hasError = false;

		try {
			const currentSessionId = getSessionId();
			const requestBody: any = {
				feedback: feedbackText.trim(),
				concept: concept,
			};

			if (currentSessionId) {
				requestBody.session_id = currentSessionId;
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
		goto("/");
	}
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
		<div class="icon-container">
			<svg
				width="72"
				height="72"
				viewBox="0 0 72 72"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<rect
					x="8"
					y="20"
					width="56"
					height="40"
					rx="4"
					stroke="white"
					stroke-width="2"
				/>
				<path
					d="M12 26L36 44L60 26"
					stroke="white"
					stroke-width="2"
					stroke-linecap="round"
				/>
				<path
					d="M8 20L36 8L64 20"
					stroke="white"
					stroke-width="2"
					stroke-linecap="round"
				/>
			</svg>
		</div>

		<h1 class="main-title">{$_("feedback.title")}</h1>

		<p class="subtitle">{$_("feedback.subtitle")}</p>

		<div class="feedback-form">
			<textarea
				class="feedback-textarea"
				bind:value={feedbackText}
				placeholder={$_("feedback.placeholder")}
				disabled={isSubmitting}
			></textarea>

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

			<div class="submit-section">
				<div class="record-button-wrapper">
					<SingleRecordingSection
						endpoint="feedback"
						recordKey="e"
						onStateChange={handleRecordingStateChange}
					/>
				</div>

				<div class="verstuur-button-container">
					<div class="button-wrapper">
						<ButtonSketchy
							text={isSubmitting
								? $_("feedback.submitting")
								: $_("feedback.submit")}
							onclick={handleSubmit}
							disabled={isSubmitting || isRecording}
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
			</div>
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
		align-items: center;
		justify-content: center;
		text-align: center;
		max-width: 800px;
		margin: 0 auto;
		padding: 2rem;
	}

	.icon-container {
		margin-bottom: 2rem;
	}

	.main-title {
		font-size: 3rem;
		font-weight: 600;
		color: white;
		margin: 0 0 1.5rem 0;
		line-height: 1.2;
	}

	.subtitle {
		font-size: 1.25rem;
		color: rgba(255, 255, 255, 0.9);
		margin: 0 0 3rem 0;
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
		margin-bottom: 2rem;
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

	.feedback-textarea:disabled {
		opacity: 0.6;
		cursor: not-allowed;
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

	.submit-section {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 3rem;
	}

	.record-button-wrapper {
		flex-shrink: 0;
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

		.submit-section {
			flex-direction: column;
			gap: 2rem;
		}

		.close-button {
			top: 16px;
			right: 16px;
		}
	}
</style>
