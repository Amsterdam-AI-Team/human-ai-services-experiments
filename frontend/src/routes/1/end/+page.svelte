<script lang="ts">
	import Confetti from "svelte-confetti";
	import { goto } from '$app/navigation';
	import { _ } from 'svelte-i18n';

	// Using Svelte 5 effect for the redirect timer
	$effect(() => {
		const timer = setTimeout(() => {
			// goto('/1/feedback');
			goto(`/1/final-thanks`);
		}, 5000);

		return () => clearTimeout(timer);
	});
</script>

<main class="app">
	<div class="content">
		<h1 class="success-header">{$_('success.requestSent')}</h1>
	</div>
</main>

<div
	style="
	position: fixed;
	top: -50px;
	left: 0;
	height: 100vh;
	width: 100vw;
	display: flex;
	justify-content: center;
	overflow: hidden;
	pointer-events: none;"
>
	<Confetti
		x={[-5, 5]}
		y={[0, 0.1]}
		delay={[500, 2000]}
		infinite
		duration={5000}
		amount={200}
		fallDistance="100vh"
	/>
</div>

<style>
	.app {
		height: calc(100vh - 100px);
		background-color: white;
		display: flex;
		flex-direction: column;
	}

	.content {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		text-align: center;
		transform: translateY(-100px);
	}

	.success-header {
		font-size: 3.5rem;
		font-weight: bold;
		color: #333;
		margin: 0;
	}

	@media (max-width: 768px) {
		.success-header {
			font-size: 2rem;
		}
	}
</style>
