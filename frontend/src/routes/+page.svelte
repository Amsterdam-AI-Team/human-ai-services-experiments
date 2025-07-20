<script lang="ts">
	import MainMessage from '$lib/components/MainMessage.svelte';
	import ButtonSketchy from '$lib/components/ButtonSketchy.svelte';
</script>

<main class="home-page">
	<div class="hero-section">
		<MainMessage 
			center 
			headerText="Welkom bij de AI Services Prototype"
			mainText="Ontdek onze experimentele AI-aangedreven gemeentelijke diensten"
			subtitle="Kies een concept om te beginnen"
		/>
	</div>

	<nav class="concept-navigation" aria-label="Hoofdnavigatie">
		<section class="concept-card">
			<h2>Concept 1: Intentie Analyse</h2>
			<p>AI-gestuurde intentieherkenning en formulierconstructie voor gemeentelijke diensten. Neem je stem op en laat onze AI begrijpen wat je nodig hebt.</p>
			<a href="/1" class="concept-link">
				<ButtonSketchy text="Probeer Concept 1 →" />
			</a>
		</section>

		<section class="concept-card">
			<h2>Concept 2: Spraakopname</h2>
			<p>Spraak-naar-tekst transcriptie en AI-assistentie voor gemeentelijke verzoeken. Perfect voor toegankelijkheid en handsfree interactie.</p>
			<a href="/2" class="concept-link">
				<ButtonSketchy text="Probeer Concept 2 →" />
			</a>
		</section>
	</nav>

	<footer class="development-info">
		<p><small>Dit is een prototype voor experimentele AI gemeentelijke diensten. Alleen voor testdoeleinden.</small></p>
	</footer>
</main>

<style>
	.home-page {
		min-height: calc(100vh - 70px);
		background-color: #f8f9fa;
		display: flex;
		flex-direction: column;
		padding: 2rem;
	}

	.hero-section {
		flex: 0 0 auto;
		margin-bottom: 3rem;
	}

	.concept-navigation {
		flex: 1;
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
		gap: 2rem;
		max-width: 1000px;
		margin: 0 auto;
		width: 100%;
	}

	.concept-card {
		background: white;
		border-radius: 12px;
		padding: 2rem;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		border: 1px solid #e9ecef;
		transition: transform 0.2s ease, box-shadow 0.2s ease;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.concept-card:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
	}

	.concept-card h2 {
		margin: 0;
		color: #333;
		font-size: 1.5rem;
		font-weight: 600;
	}

	.concept-card p {
		margin: 0;
		color: #666;
		line-height: 1.6;
		flex: 1;
	}

	.concept-link {
		text-decoration: none;
		margin-top: auto;
	}

	.development-info {
		margin-top: 3rem;
		text-align: center;
		color: #6c757d;
	}

	.development-info p {
		margin: 0;
	}

	@media (max-width: 768px) {
		.home-page {
			padding: 1rem;
		}

		.concept-navigation {
			grid-template-columns: 1fr;
			gap: 1.5rem;
		}

		.concept-card {
			padding: 1.5rem;
		}

		.concept-card h2 {
			font-size: 1.3rem;
		}
	}
</style>
