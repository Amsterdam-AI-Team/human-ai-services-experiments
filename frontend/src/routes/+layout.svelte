<script lang="ts">
	import '../main.css';
	import { isLoading } from 'svelte-i18n';
	import { initI18n } from '$lib/i18n';
	import { initLanguage } from '$lib/stores/languageStore';
	import Header from '$lib/components/Header.svelte';
	import ErrorDisplay from '$lib/components/ErrorDisplay.svelte';
	import { apiResponses } from '$lib/stores/apiStore';

	let { children } = $props();
	let i18nReady = $state(false);

	// Initialize i18n on app start
	$effect(() => {
		(async () => {
			try {
				await initI18n();
				initLanguage();
				i18nReady = true;
			} catch (error) {
				console.error('Failed to initialize i18n:', error);
				i18nReady = true; // Show page anyway
			}
		})();
	});

	// Debug: Log API store changes
	$effect(() => {
		console.log('📊 API Store:', $apiResponses);
	});
</script>

{#if i18nReady && !$isLoading}
	<Header />
	{@render children()}
	<ErrorDisplay />
{:else}
	<div class="loading">
		<div class="loading-content">
			<div class="logo">
				<img src="/images/logo-sketchy.svg" alt="Logo" style="width: 60px; height: auto;" />
			</div>
			<p>Loading...</p>
		</div>
	</div>
{/if}

<style>
	.loading {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100vh;
		background-color: #f8f9fa;
	}

	.loading-content {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
	}

	.loading-content p {
		font-size: 1.2rem;
		color: #666;
		margin: 0;
	}
</style>
