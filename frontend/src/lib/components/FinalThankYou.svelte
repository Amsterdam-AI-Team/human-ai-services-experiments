<script lang="ts">
	import { _ } from "svelte-i18n";
	import { goto } from "$app/navigation";
	import ButtonSketchy from "$lib/components/ButtonSketchy.svelte";

	interface Props {
		concept: number;
	}

	let { concept }: Props = $props();

	// Auto-redirect to concept home after 5 seconds
	$effect(() => {
		const redirectUrl = `/${concept}`;
		const timer = setTimeout(() => {
			goto(redirectUrl);
		}, 5000);

		return () => clearTimeout(timer);
	});

	function handleGoHome() {
		goto(`/${concept}`);
	}
</script>

<main class="app">
	<div class="content">
		<div class="icon-container">
			<img src="/images/checkmark.svg" alt="Success checkmark" width="120" height="120" />
		</div>

		<h1 class="main-title">{$_("finalThanks.title")}</h1>
		
		<p class="subtitle">{$_("finalThanks.message")}</p>

		<ButtonSketchy
			text={$_("finalThanks.goHome")}
			onclick={handleGoHome}
		/>

		<p class="auto-redirect">{$_("finalThanks.autoRedirect")}</p>
	</div>
</main>

<style>
	.app {
		height: calc(100vh - 100px);
		background-color: #f8f9fa;
		display: flex;
		flex-direction: column;
		font-family: 'Amsterdam Sans', sans-serif;
	}

	.content {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		text-align: center;
		max-width: 600px;
		margin: 0 auto;
		padding: 2rem;
	}

	.icon-container {
		margin-bottom: 2rem;
	}

	.main-title {
		font-size: 3rem;
		font-weight: 600;
		color: #333;
		margin: 0 0 1.5rem 0;
		line-height: 1.2;
	}

	.subtitle {
		font-size: 1.25rem;
		color: #666;
		margin: 0 0 3rem 0;
		max-width: 500px;
		line-height: 1.4;
	}

	.content :global(.svg-button) {
		margin-bottom: 2rem;
	}

	.auto-redirect {
		font-size: 0.9rem;
		color: #999;
		margin: 0;
		font-style: italic;
	}

	@media (max-width: 768px) {
		.content {
			padding: 1rem;
		}

		.main-title {
			font-size: 2.5rem;
		}

		.subtitle {
			font-size: 1.1rem;
		}
	}
</style>