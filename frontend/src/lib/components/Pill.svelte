<!-- Pill.svelte -->
<script lang="ts">
	let { icon, text, onclick } = $props();
</script>

<button class="pill-button" {onclick}>
	{#if icon}
		<img src={icon} alt="icon" class="pill-icon" />
	{/if}
	<span class="pill-text">{text}</span>
</button>

<style>
	.pill-button {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		background: #f8f9fa;
		border: 1px solid #dee2e6;
		border-radius: 20px;
		cursor: pointer;
		transition: all 0.2s ease;
		color: #333;
		text-decoration: none;
		white-space: nowrap;
	}

	.pill-button:hover {
		background: #e9ecef;
		border-color: #ced4da;
	}

	.pill-button:active {
		transform: translateY(1px);
	}

	.pill-icon {
		width: 24px;
		height: 24px;
		object-fit: contain;
	}

	.pill-text {
		font-family: "Amsterdam Sans", sans-serif;
		font-size: 0.9rem;
		font-weight: 700;
	}
</style>
