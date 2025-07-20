<script lang="ts">
	import '../main.css';
	import { onMount } from 'svelte';
	import { initI18n } from '$lib/i18n';
	import { initLanguage } from '$lib/stores/languageStore';
	import Header from '$lib/components/Header.svelte';
	import ErrorDisplay from '$lib/components/ErrorDisplay.svelte';

	let { children } = $props();
	let mounted = $state(false);

	// Initialize i18n on app start
	onMount(async () => {
		await initI18n();
		initLanguage();
		mounted = true;
	});
</script>

<Header />
{@render children()}
<ErrorDisplay />

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
