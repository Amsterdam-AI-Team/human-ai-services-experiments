<script>
	import '../main.css';
	let { children } = $props();
    import Header from '$lib/components/Header.svelte';
</script>

<Header />
{@render children()}
