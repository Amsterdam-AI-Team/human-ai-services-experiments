<!-- TranscriptionRecordingSection.svelte -->
<script lang="ts">
	import SingleRecordingSection from "./SingleRecordingSection.svelte";
	import ButtonSketchy from "./ButtonSketchy.svelte";
	import { apiResponses } from "$lib/stores/apiStore";
	import {
		setLanguageFromAPI,
		shouldSwitchLanguage,
	} from "$lib/stores/languageStore";
	import type { LanguageCode } from "$lib/i18n";
	import { _ } from "svelte-i18n";
	import { goto } from "$app/navigation";

	let { continueUrl = "/2/agents-chat" } = $props();

	let transcriptionText = $state("");
	let isTranscribing = $state(false);

	const displayText = $derived(
		isTranscribing
			? $_("recording.transcribing")
			: transcriptionText.length > 0
				? $_("recording.addRecording")
				: $_("recording.startRecording"),
	);

	// Watch for yap endpoint responses and update transcription
	$effect(() => {
		const responses = $apiResponses;
		const latestYapResponse = responses
			.filter((r) => r.endpoint === "yap")
			.slice(-1)[0];

		if (latestYapResponse?.data?.text) {
			transcriptionText = latestYapResponse.data.text;
			isTranscribing = false;

			// Handle language detection from API response
			if (latestYapResponse.data.language) {
				const detectedLang = latestYapResponse.data
					.language as LanguageCode;
				if (shouldSwitchLanguage(detectedLang)) {
					setLanguageFromAPI(detectedLang);
				}
			}
		} else if (latestYapResponse?.data?.error) {
			isTranscribing = false;
		}
	});

	function handleRecordingStateChange(
		recording: boolean,
		analyzing: boolean,
	) {
		isTranscribing = analyzing;
	}

	function handleContinue() {
		goto(continueUrl);
	}
</script>

<div class="recording-section">
	<textarea
		class="transcription-textarea"
		dir="auto"
		bind:value={transcriptionText}
		placeholder={$_("recording.placeholder")}
		readonly
	></textarea>
	<div class="button-container">
		<div class="record-button-wrapper">
			<SingleRecordingSection
				endpoint="yap"
				recordKey="e"
				onStateChange={handleRecordingStateChange}
				existingText={transcriptionText}
			/>
			{#if transcriptionText.length > 0}
				<span class="plus-symbol">+</span>
			{/if}
		</div>
		{#if transcriptionText.length > 0}
			<ButtonSketchy
				text={$_("buttons.continue")}
				onclick={handleContinue}
			/>
		{/if}
	</div>
	<p>
		{displayText}<br />
		<em>{$_("recording.privacyNotice")}</em>
	</p>
</div>

<style>
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

	.transcription-textarea {
		width: 100%;
		min-height: 150px;
		padding: 1rem;
		border: 1px solid #dee2e6;
		/* border-radius: 8px; */
		font-size: 1rem;
		font-family: inherit;
		resize: vertical;
		background-color: #fff;
		margin-bottom: 1rem;
	}

	.transcription-textarea:focus {
		outline: none;
		border-color: #007bff;
		box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
	}
</style>
