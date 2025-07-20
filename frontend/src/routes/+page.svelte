<script lang="ts">
	import { _ } from 'svelte-i18n';
	import MainMessage from '$lib/components/MainMessage.svelte';
	import ButtonSketchy from '$lib/components/ButtonSketchy.svelte';
	import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
</script>

<main class="home-page">
	<!-- Language Switcher for testing -->
	<div class="language-switcher-container">
		<LanguageSwitcher />
	</div>

	<div class="hero-section">
		<MainMessage 
			center 
			headerText={$_('welcome.header')}
			mainText={$_('welcome.main')}
			subtitle={$_('welcome.subtitle')}
		/>
	</div>

	<nav class="concept-navigation" aria-label={$_('navigation.main')}>
		<section class="concept-card">
			<h2>{$_('concepts.concept1.title')}</h2>
			<p>{$_('concepts.concept1.description')}</p>
			<a href="/1" class="concept-link">
				<ButtonSketchy text={$_('concepts.concept1.button')} />
			</a>
		</section>

		<section class="concept-card">
			<h2>{$_('concepts.concept2.title')}</h2>
			<p>{$_('concepts.concept2.description')}</p>
			<a href="/2" class="concept-link">
				<ButtonSketchy text={$_('concepts.concept2.button')} />
			</a>
		</section>
	</nav>

	<footer class="development-info">
		<p><small>{$_('footer.disclaimer')}</small></p>
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

	.language-switcher-container {
		align-self: flex-end;
		margin-bottom: 2rem;
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
