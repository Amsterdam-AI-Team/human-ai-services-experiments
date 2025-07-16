<script>
	import SingleRecordingSection from '$lib/components/SingleRecordingSection.svelte';
</script>

<main class="app">
	<div class="content">
		<h1>Test Different Endpoints</h1>
		
		<div class="endpoint-section">
			<h2>Analyze Endpoint</h2>
			<p>Sends audio to /api/analyze for analysis</p>
			<SingleRecordingSection endpoint="analyze" />
		</div>
		
		<div class="endpoint-section">
			<h2>Chat Audio Endpoint</h2>
			<p>Sends audio to /api/chatAudio for chat processing</p>
			<SingleRecordingSection endpoint="chatAudio" />
		</div>
	</div>
</main>

<style>
	.app {
		min-height: calc(100vh - 70px - 4rem);
		background-color: #f8f9fa;
		display: flex;
		flex-direction: column;
	}

	.content {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 2rem;
		text-align: center;
		max-width: 1200px;
		margin: auto;
	}

	.endpoint-section {
		margin: 2rem 0;
		padding: 2rem;
		border: 1px solid #dee2e6;
		border-radius: 8px;
		background: white;
		width: 100%;
		max-width: 800px;
	}

	h1 {
		color: #333;
		margin-bottom: 2rem;
	}

	h2 {
		color: #007bff;
		margin-bottom: 1rem;
	}

	p {
		color: #666;
		margin-bottom: 1rem;
	}

	@media (max-width: 768px) {
		.content {
			padding: 1rem;
		}
		
		.endpoint-section {
			padding: 1rem;
		}
	}
</style>