<script lang="ts">
	import MainMessage from "$lib/components/MainMessage.svelte";
	import TranscriptionRecordingSection from "$lib/components/TranscriptionRecordingSection.svelte";
	import { _ } from "svelte-i18n";
</script>

<main class="app">
	<div class="close-button" style="display: none;">
		<a href="/2">✕</a>
	</div>

	<div class="content">
		<MainMessage
			headerText={$_("messages.aiMessage")}
			mainText={$_("messages.ideas")}
		/>

		<div class="tags">
			<span class="tag">🎉&nbsp;&nbsp;{$_("concept2.tags.people")}</span>
			<span class="tag"
				>🍾&nbsp;&nbsp;{$_("concept2.tags.champagne")}</span
			>
			<span class="tag">🎯&nbsp;&nbsp;{$_("concept2.tags.games")}</span>
			<span class="tag">🎵&nbsp;&nbsp;{$_("concept2.tags.band")}</span>
			<span class="tag"
				>🎆&nbsp;&nbsp;{$_("concept2.tags.fireworks")}</span
			>
			<span class="tag">🍖&nbsp;&nbsp;{$_("concept2.tags.bbq")}</span>
			<span class="tag">🚗&nbsp;&nbsp;{$_("concept2.tags.carshow")}</span>
		</div>

		<TranscriptionRecordingSection continueUrl="/2/agents-chat" />
	</div>
</main>

<style>
	.app {
		height: calc(100vh - 70px);
		background-color: #f8f9fa;
		display: flex;
		flex-direction: column;
		position: relative;
	}

	.close-button {
		position: absolute;
		top: 2rem;
		left: 2rem;
		z-index: 10;
	}

	.close-button a {
		font-size: 2rem;
		color: #dc3545;
		text-decoration: none;
		font-weight: bold;
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

	.tags {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem;
		justify-content: flex-start;
		margin-bottom: 3rem;
		width: 1400px;
		margin-left: -100px;
	}

	.tag {
		background-color: #e9ecef;
		padding: 0.8rem 1.5rem;
		border-radius: 25px;
		font-size: 1.1rem;
		color: #495057;
		border: 1px solid #dee2e6;
	}

	@media (max-width: 768px) {
		.content {
			padding: 1rem;
		}

		.tags {
			gap: 0.5rem;
		}

		.tag {
			font-size: 0.8rem;
			padding: 0.4rem 0.8rem;
		}
	}
</style>
