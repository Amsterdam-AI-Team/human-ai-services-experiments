<script lang="ts">
	import { setLanguage, currentLanguage } from '$lib/stores/languageStore';
	import { languages, type LanguageCode } from '$lib/i18n';

	function handleLanguageChange(languageCode: LanguageCode) {
		setLanguage(languageCode);
	}
</script>

<div class="language-switcher">
	{#each languages as language}
		<button 
			class="language-button"
			class:active={$currentLanguage === language.code}
			onclick={() => handleLanguageChange(language.code)}
		>
			{language.name}
		</button>
	{/each}
</div>

<style>
	.language-switcher {
		display: flex;
		gap: 0.5rem;
		padding: 1rem;
		background: white;
		border-radius: 8px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
		border: 1px solid #e9ecef;
	}

	.language-button {
		padding: 0.5rem 1rem;
		border: 1px solid #dee2e6;
		background: white;
		border-radius: 4px;
		cursor: pointer;
		font-size: 0.9rem;
		transition: all 0.2s ease;
	}

	.language-button:hover {
		background: #f8f9fa;
		border-color: #adb5bd;
	}

	.language-button.active {
		background: #007bff;
		color: white;
		border-color: #007bff;
	}
</style>