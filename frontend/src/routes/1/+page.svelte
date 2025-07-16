<script>
	import MainMessage from '$lib/components/MainMessage.svelte';
	import CalloutBubble from '$lib/components/CalloutBubble.svelte';
	import SingleRecordingSection from '$lib/components/SingleRecordingSection.svelte';
	import ApiDebugger from '$lib/components/ApiDebugger.svelte';
	import { apiResponses } from '$lib/stores/apiStore';
	import { goto } from '$app/navigation';

	// Watch for analyze responses and redirect if similarity is low
	$effect(() => {
		const responses = $apiResponses;
		const latestAnalyzeResponse = responses
			.filter(r => r.endpoint === 'analyze')
			.slice(-1)[0];
		
		if (latestAnalyzeResponse?.data?.matches) {
			const maxSimilarity = Math.max(...latestAnalyzeResponse.data.matches.map(match => match.similarity));
			if (maxSimilarity <= 0.5) {
				goto('/1/choose');
			}
		}
	});
</script>

<main class="app">
	<div class="content">
		<MainMessage center mainText="Hoe kunnen we je helpen?" subtitle="Comment pouvons-nous vous aider?" />

		<CalloutBubble
			text="Voor nu kan ons prototype je alleen helpen met een paar scenario's: parkeerboetes, verhuizingen, en X, Y en Z. Probeer het alvast uit!"
		/>

		<SingleRecordingSection endpoint="analyze" />
		
		<ApiDebugger endpoint="analyze" />
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
		width: 1000px;
		flex-direction: column;
		align-items: center;
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
