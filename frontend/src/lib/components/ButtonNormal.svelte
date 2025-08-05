<!-- ButtonNormal.svelte -->
<script lang="ts">
	let { 
		text = 'Wijziging aanbrengen',
		icon = '/images/agent-button-icon-chat.svg',
		onclick = () => {}
	} = $props<{
		text?: string;
		icon?: string;
		onclick?: () => void;
	}>();
</script>

<button class="button-normal" {onclick}>
	<img src={icon} alt="" class="button-icon" />
	{text}
</button>

<style>
	.button-normal {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		background: transparent;
		border: 2px solid #004699;
		padding: 0.5rem 1rem;
		font-family: 'Amsterdam Sans', Arial, sans-serif;
		font-size: 1rem;
		color: #004699;
		cursor: pointer;
		transition: background-color 0.2s, color 0.2s;
	}

	.button-normal:hover {
		background: #004699;
		color: white;
	}

	.button-icon {
		width: 32px;
		height: 32px;
		flex-shrink: 0;
	}
</style>