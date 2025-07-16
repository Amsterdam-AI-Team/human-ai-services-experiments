<script lang="ts">
	import { apiResponses } from "$lib/stores/apiStore";
	import { goto } from "$app/navigation";
	import SketchyCard from "$lib/components/SketchyCard.svelte";
	import ApiDebugger from "$lib/components/ApiDebugger.svelte";

	// Get the latest analyze response to show available options
	const latestAnalyzeResponse = $derived(
		$apiResponses.filter((r) => r.endpoint === "analyze").slice(-1)[0],
	);

	// Extract matches from the response
	const matches = $derived(latestAnalyzeResponse?.data?.matches || []);

	function getIconForIntent(intentCode: string): string {
		if (intentCode === "create_objection_parking_fine") {
			return "/images/pencil.svg";
		} else if (intentCode === "update_address_municipal_records") {
			return "/images/wallet.svg";
		} else {
			return "/images/pencil.svg"; // Default icon
		}
	}

	function handleOptionClick(intentCode: string) {
		// Navigate to the appropriate page based on intent
		if (intentCode === "create_objection_parking_fine") {
			goto("/1/construct");
		} else {
			// For other intents, we could add more routes later
			console.log("Selected intent:", intentCode);
		}
	}

	function handleBackClick() {
		goto("/1");
	}
</script>

<main class="app">
	<div class="content">
		<div class="page-header">
			<h1>Parkeerboete</h1>
			<p class="subtitle">
				Als je een parkeerboete hebt ontvangen kan je de volgende dingen
				doen:
			</p>
		</div>

		<div class="options-grid">
			{#each matches as match}
				<div onclick={() => handleOptionClick(match.intent.intentcode)}>
					<SketchyCard
						logo={getIconForIntent(match.intent.intentcode)}
						linkText={match.intent.intent}
						href="#"
					/>
				</div>
			{/each}
		</div>

		<button class="back-button" onclick={handleBackClick}> ← terug </button>
	</div>
</main>

<ApiDebugger endpoint="analyze" />

<style>
	.app {
		min-height: calc(100vh - 140px);
		background-color: #f8f9fa;
		display: flex;
		flex-direction: column;
		padding: 2rem;
	}

	.content {
		max-width: 1200px;
		margin: 0 auto;
		width: 100%;
	}

	.page-header {
		text-align: center;
		margin-bottom: 3rem;
	}

	.page-header h1 {
		font-size: 2.5rem;
		color: #333;
		margin: 0 0 1rem 0;
		font-weight: 700;
	}

	.subtitle {
		font-size: 1.2rem;
		color: #666;
		margin: 0;
		line-height: 1.5;
	}

	.options-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: 2rem;
		margin-bottom: 3rem;
		max-width: 900px;
		margin-left: auto;
		margin-right: auto;
		justify-items: center;
	}

	.options-grid > div {
		cursor: pointer;
		transition: transform 0.2s ease;
	}

	.options-grid > div:hover {
		transform: translateY(-2px);
	}

	.back-button {
		background: #ffffff;
		border: 2px solid #004699;
		border-radius: 8px;
		color: #004699;
		font-size: 1rem;
		padding: 0.75rem 1.5rem;
		cursor: pointer;
		transition: all 0.2s ease;
		font-weight: 500;
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
	}

	.back-button:hover {
		background: #004699;
		color: white;
		transform: translateY(-1px);
	}

	@media (max-width: 768px) {
		.app {
			padding: 1rem;
		}

		.page-header h1 {
			font-size: 2rem;
		}

		.subtitle {
			font-size: 1rem;
		}

		.options-grid {
			grid-template-columns: 1fr;
			gap: 1rem;
		}
	}
</style>
