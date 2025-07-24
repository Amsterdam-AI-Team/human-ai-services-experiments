<script lang="ts">
</script>

<main class="app">
	<div class="content">
		<h1 class="feedback-header">Feedback?</h1>
	</div>
</main>

<style>
	.app {
		height: calc(100vh - 70px);
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
		transform: translateY(-140px);
	}

	.feedback-header {
		font-size: 3.5rem;
		font-weight: bold;
		color: #333;
		margin: 0;
	}

	@media (max-width: 768px) {
		.feedback-header {
			font-size: 2rem;
		}
	}
</style>