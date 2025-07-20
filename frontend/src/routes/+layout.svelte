<script lang="ts">
	import '../main.css';
	import { onMount } from 'svelte';
	import { isLoading } from 'svelte-i18n';
	import { initI18n } from '$lib/i18n';
	import { initLanguage } from '$lib/stores/languageStore';
	import Header from '$lib/components/Header.svelte';
	import ErrorDisplay from '$lib/components/ErrorDisplay.svelte';

	let { children } = $props();

	// Initialize i18n on app start
	onMount(async () => {
		await initI18n();
		initLanguage();
	});
</script>

{#if !$isLoading}
	<Header />
	{@render children()}
	<ErrorDisplay />
{:else}
	<div class="loading">Loading...</div>
{/if}

<style>
	.loading {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100vh;
		font-size: 1.2rem;
		color: #666;
	}
</style>
