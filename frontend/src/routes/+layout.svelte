<script lang="ts">
	import '../main.css';
	let { children } = $props();
    import Header from '$lib/components/Header.svelte';
	import ErrorDisplay from '$lib/components/ErrorDisplay.svelte';
</script>

<Header />
{@render children()}
<ErrorDisplay />
