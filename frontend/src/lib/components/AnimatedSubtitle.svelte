<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { currentLanguage } from '$lib/stores/languageStore';
	import type { LanguageCode } from '$lib/i18n';

	const subtitles: Record<LanguageCode, string> = {
		fr: "Comment pouvons-nous vous aider?",
		en: "How can we help you?",
		nl: "Hoe kunnen we je helpen?"
	};

	let currentIndex = $state(0);
	let intervalId: number | null = null;
	let isAnimating = $state(false);
	let currentText = $state("");

	// Get available languages (excluding the currently selected one)
	let availableLanguages = $derived((Object.keys(subtitles) as LanguageCode[])
		.filter(lang => lang !== $currentLanguage));

	// Update current text when available languages or index changes
	$effect(() => {
		if (availableLanguages.length > 0) {
			currentText = subtitles[availableLanguages[currentIndex % availableLanguages.length]];
		}
	});

	async function animateTextChange() {
		isAnimating = true;
		
		// Wait for fade out
		await new Promise(resolve => setTimeout(resolve, 200));
		
		// Change to next language
		currentIndex = (currentIndex + 1) % availableLanguages.length;
		
		// Wait a bit then fade in
		await new Promise(resolve => setTimeout(resolve, 50));
		isAnimating = false;
	}

	onMount(() => {
		// Initialize with first available subtitle
		if (availableLanguages.length > 0) {
			currentText = subtitles[availableLanguages[0]];
		}

		// Change subtitle every 3 seconds with animation
		intervalId = setInterval(animateTextChange, 3000) as unknown as number;
	});

	onDestroy(() => {
		if (intervalId) {
			clearInterval(intervalId);
		}
	});
</script>

<p class="subtitle" class:animating={isAnimating}>
	{currentText}
</p>

<style>
	.subtitle {
		font-size: 2rem;
		font-style: normal;
		font-weight: 400;
		color: #999;
		margin: 20px 0 0 0;
		text-align: center;
		min-height: 2.5rem;
		transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
		transform: translateY(0);
		opacity: 1;
	}

	.subtitle.animating {
		opacity: 0;
		transform: translateY(-10px) scale(0.98);
	}

	/* Slide in animation for new text */
	.subtitle:not(.animating) {
		animation: slideInUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
	}

	@keyframes slideInUp {
		0% {
			opacity: 0;
			transform: translateY(15px) scale(0.95);
		}
		50% {
			opacity: 0.7;
			transform: translateY(-2px) scale(1.02);
		}
		100% {
			opacity: 1;
			transform: translateY(0) scale(1);
		}
	}

	@media (max-width: 768px) {
		.subtitle {
			font-size: 1.5rem;
		}
	}
</style>