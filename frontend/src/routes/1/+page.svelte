<script lang="ts">
	import { _ } from 'svelte-i18n';
	import MainMessage from '$lib/components/MainMessage.svelte';
	import AnimatedSubtitle from '$lib/components/AnimatedSubtitle.svelte';
	import CalloutBubble from '$lib/components/CalloutBubble.svelte';
	import SingleRecordingSection from '$lib/components/SingleRecordingSection.svelte';
	import ApiDebugger from '$lib/components/ApiDebugger.svelte';
	import { apiResponses } from '$lib/stores/apiStore';
	import { configStore } from '$lib/stores/configStore';
	import { goto } from '$app/navigation';

	// Watch for analyze responses and redirect based on configurable similarity threshold
	// To modify the threshold, use: configStore.setSimilarityThreshold(0.7) or update configStore.ts
	$effect(() => {
		const responses = $apiResponses;
		const latestAnalyzeResponse = responses
			.filter(r => r.endpoint === 'analyze')
			.slice(-1)[0];
		
		if (latestAnalyzeResponse?.data?.matches) {
			const highestMatch = latestAnalyzeResponse.data.matches.reduce((prev: any, current: any) => 
				(prev.similarity > current.similarity) ? prev : current
			);
			
			if (highestMatch.similarity > $configStore.similarityThreshold) {
				goto(`/1/construct/${highestMatch.intent.intentcode}`);
			} else {
				goto('/1/choose');
			}
		}
	});
</script>

<main class="app">
	<div class="content">
		<div class="main-section">
			<MainMessage center mainText={$_('concept1.mainHelp')} />
			<AnimatedSubtitle />
		</div>

		<CalloutBubble
			text={$_('concept1.callout')}
		/>

		<SingleRecordingSection endpoint="analyze" />
		
	</div>
</main> 
<ApiDebugger endpoint="analyze" />

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
		width: 1000px;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 2rem;
		text-align: center;
		width: 1200px;
		margin: auto;
	}

	.main-section {
		margin-bottom: 80px;
	}

	@media (max-width: 768px) {
		.content {
			padding: 1rem;
		}
		
		.main-section {
			margin-bottom: 40px;
		}
	}
</style>
