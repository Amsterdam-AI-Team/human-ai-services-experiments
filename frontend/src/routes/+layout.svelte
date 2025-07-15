<script>
	import '../main.css';
	let { children } = $props();
    import Header from '$lib/components/Header.svelte';
</script>

<!-- <div class="grid-wrapper-wrapper">
	<div class="grid-wrapper ams-screen ams-screen--wide">
		<div class="ams-grid">
			<div class="ams-grid__cell ams-grid__cell--span-all">
				{@render children()}
			</div>
		</div>
	</div>
</div> -->


<Header />
{@render children()}


<!-- oud grid -->
<!-- .grid-wrapper-wrapper {
		background-color: #f5f5f5;
		min-height: 100vh; /* Make it at least full viewport height */
		width: 100vw;
	}
    
	.grid-wrapper {
		background-color: #f5f5f5;
	} -->

<style>
	
</style>
