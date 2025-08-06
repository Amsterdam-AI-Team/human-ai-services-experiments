<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { page } from '$app/stores';
	import { startInactivityTimer, InactivityTimer } from '$lib/utils/inactivityTimer';

	let inactivityTimer: InactivityTimer | null = null;

	onMount(() => {
		inactivityTimer = startInactivityTimer($page.url.pathname);
	});

	onDestroy(() => {
		if (inactivityTimer) {
			inactivityTimer.stop();
		}
	});
</script>

<slot />