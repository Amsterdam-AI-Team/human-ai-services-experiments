<script lang="ts">
	import MainMessage from '$lib/components/MainMessage.svelte';
	import ButtonSketchy from '$lib/components/ButtonSketchy.svelte';
	import { _ } from 'svelte-i18n';
</script>

<main class="app">
	<div class="content">
		<MainMessage
			headerText={$_('messages.aiMessage')}
			mainText={$_('messages.subsidyQuestion')}
		/>
		<a href="/2/record">
			<ButtonSketchy text={$_('buttons.start')} />
		</a>
	</div>
</main>

<style>
	.app {
		height: calc(100vh - 70px - 4rem);
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
