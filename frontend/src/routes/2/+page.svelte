<script lang="ts">
	import MainMessage from "$lib/components/MainMessage.svelte";
	import ButtonSketchy from "$lib/components/ButtonSketchy.svelte";
	import { _ } from "svelte-i18n";
	import { clearApiResponses } from "$lib/stores/apiStore";
	import { clearSession } from "$lib/stores/sessionStore";
	import { setLanguage } from "$lib/stores/languageStore";

	let initialized = $state(false);

	// Clear state when entering the flow root (on mount, run once)
	$effect(() => {
		if (!initialized) {
			clearApiResponses();
			clearSession();
			setLanguage('nl');
			initialized = true;
		}
	});
</script>

<main class="app">
	<div class="content">
		<MainMessage
			headerText={$_("messages.aiMessage")}
			mainText={$_("messages.subsidyQuestion")}
		/>
		<a href="/2/record">
			<ButtonSketchy text={$_("buttons.start")} />
		</a>
	</div>
</main>

<style>
	.app {
		height: calc(100vh - 100px);
		background-color: #f8f9fa;
		display: flex;
		flex-direction: column;
	}

	.content {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: start;
		justify-content: center;
		padding: 2rem;
		text-align: center;
		width: 1200px;
		margin: auto;
	}

	@media (max-width: 768px) {
		.content {
			padding: 1rem;
		}
	}
</style>
