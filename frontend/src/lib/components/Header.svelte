<!-- Header.svelte -->
<script lang="ts">
	import { _ } from "svelte-i18n";
	import { page } from "$app/state";
	import { goto } from "$app/navigation";
	import { setLanguage, currentLanguage } from "$lib/stores/languageStore";
	import { clearApiResponses } from "$lib/stores/apiStore";
	import type { LanguageCode } from "$lib/i18n";

	const currentRoute = $derived(page.route.id);

	// Map current language to dropdown value
	const dropdownValue = $derived($currentLanguage);

	function handleDropdownChange(event: Event) {
		const value = (event.target as HTMLSelectElement).value;

		// Handle supported languages
		if (value === "nl" || value === "en" || value === "fr") {
			setLanguage(value as LanguageCode);
		} else if (value === "auto") {
			// 'Auto' means default to Dutch for now
			setLanguage("nl");
		} else {
			// For unsupported languages, show message and revert to current language
			alert(`${value} is not yet supported. Coming soon!`);
			// The dropdown will automatically revert due to reactive dropdownValue
		}
	}

	function handleBackClick() {
		clearApiResponses();
		setLanguage('nl');
		goto("/1");
	}

	function handleLogoPanicClick() {
		clearApiResponses();
		
		// Determine current concept from URL and navigate to concept root
		if (currentRoute?.startsWith("/2")) {
			goto("/2");
		} else {
			goto("/1");
		}
	}
</script>

<header class="header">
	{#if currentRoute?.startsWith("/1/construct")}
		<div class="header-layout">
			<div class="header-left">
				<div class="logo-container">
					<button onclick={handleLogoPanicClick} class="logo-button">
						<img
							src="/images/logo-sketchy.svg"
							alt="Logo"
							class="logo"
						/>
					</button>
					<button onclick={handleBackClick} class="back-button">
						<img
							src="/images/chevron-left.svg"
							alt="Back"
							class="back-arrow"
						/>
						<span class="back-text"
							>{$_("concept1.construct.backButton")}</span
						>
					</button>
				</div>
			</div>
			<div class="header-right">
				<div class="dropdown-container">
					<select
						class="sketchy-dropdown"
						value={dropdownValue}
						onchange={handleDropdownChange}
					>
						<!-- <option value="auto">Language: auto</option> -->
						<option value="nl">Nederlands</option>
						<option value="en">English</option>
						<option value="fr">Français</option>
						<!-- <option value="ar">العربية</option>
						<option value="tr">Türkçe</option>
						<option value="es">Español</option>
						<option value="de">Deutsch</option>
						<option value="it">Italiano</option>
						<option value="pt">Português</option>
						<option value="pl">Polski</option>
						<option value="ru">Русский</option>
						<option value="zh">中文</option>
						<option value="hi">हिन्दी</option>
						<option value="ja">日本語</option>
						<option value="ko">한국어</option> -->
					</select>
				</div>
			</div>
		</div>
	{:else}
		<!-- Default header for all other routes including homepage -->
		<div class="logo-container">
			<button onclick={handleLogoPanicClick} class="logo-button">
				<img src="/images/logo-sketchy.svg" alt="Logo" class="logo" />
			</button>
		</div>

		<!-- Always show language dropdown on non-construct pages -->
		<div class="dropdown-container">
			<select
				class="sketchy-dropdown"
				value={dropdownValue}
				onchange={handleDropdownChange}
			>
				<!-- <option value="auto">Language: auto</option> -->
				<option value="nl">Nederlands</option>
				<option value="en">English</option>
				<option value="fr">Français</option>
				<!-- <option value="ar">العربية</option>
				<option value="tr">Türkçe</option>
				<option value="es">Español</option>
				<option value="de">Deutsch</option>
				<option value="it">Italiano</option>
				<option value="pt">Português</option>
				<option value="pl">Polski</option>
				<option value="ru">Русский</option>
				<option value="zh">中文</option>
				<option value="hi">हिन्दी</option>
				<option value="ja">日本語</option>
				<option value="ko">한국어</option> -->
			</select>
		</div>
	{/if}
</header>

<style>
	/* @import url("https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap"); */

	.header {
		height: 100px;
		min-height: 100px;
		background: transparent;
	}

	.header-layout {
		display: flex;
		height: 100%;
	}

	.header-left {
		flex: 1;
		background-color: #f8f9fa;
		display: flex;
		align-items: center;
		padding: 2rem;
	}

	.header-right {
		flex: 2;
		background-color: #ffffff;
		display: flex;
		align-items: center;
		justify-content: flex-end;
		padding: 2rem;
	}

	/* Default header layout for non-construct pages */
	.header:not(:has(.header-layout)) {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 2rem;
	}

	.logo-container {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.back-button {
		background: none;
		border: none;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		cursor: pointer;
		font-size: 1.1rem;
		color: #1864ab;
		padding: 0.5rem 0;
		text-decoration: none;
		font-family: 'Amsterdam Sans', sans-serif
	}

	.back-button:hover {
		color: #0d47a1;
	}

	.back-arrow {
		width: 16px;
		height: 16px;
		object-fit: contain;
	}

	.back-text {
		font-size: 1.1rem;
	}

	.logo-button {
		background: none;
		border: none;
		cursor: pointer;
		padding: 0;
	}

	.logo {
		width: 60px;
		height: auto;
		object-fit: contain;
	}

	.dropdown-container {
		display: flex;
		align-items: center;
	}

	.sketchy-dropdown {
		appearance: none;
		-webkit-appearance: none;
		-moz-appearance: none;
		background: #f8f9fa;
		border: 2px solid #1864ab;
		border-radius: 8px;
		padding: 8px 32px 8px 12px;
		/* font-family: "Patrick Hand", cursive; */
		font-family: "Amsterdam Sans", sans-serif;
		font-size: 1rem;
		color: #000;
		cursor: pointer;
		position: relative;
		background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath d='M2 4l4 4 4-4' stroke='%231864AB' stroke-width='2' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
		background-repeat: no-repeat;
		background-position: right 10px center;
		background-size: 12px;
		outline: none;
		transition: all 0.2s ease;
	}

	.sketchy-dropdown:hover {
		background-color: #e9ecef;
		border-color: #0d47a1;
	}

	.sketchy-dropdown:focus {
		box-shadow: 0 0 0 2px rgba(24, 100, 171, 0.2);
		border-color: #1864ab;
	}

	.sketchy-dropdown option {
		font-family: "Patrick Hand", cursive;
		font-size: 1.1rem;
		padding: 8px;
		background: white;
		color: #000;
	}

	/* Responsive adjustments */
	@media (max-width: 768px) {
		.header {
			padding: 1rem;
		}

		.logo {
			width: 40px;
		}

		.sketchy-dropdown {
			font-size: 1rem;
			padding: 6px 28px 6px 10px;
		}
	}
</style>
