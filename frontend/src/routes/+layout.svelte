<script lang="ts">
	import '../main.css';
	import { onMount } from 'svelte';
	import { initI18n } from '$lib/i18n';
	import { initLanguage } from '$lib/stores/languageStore';
	import Header from '$lib/components/Header.svelte';
	import ErrorDisplay from '$lib/components/ErrorDisplay.svelte';

	let { children } = $props();

	// Initialize i18n on app start
	onMount(() => {
		initI18n();
		initLanguage();
	});
</script>

<Header />
{@render children()}
<ErrorDisplay />
