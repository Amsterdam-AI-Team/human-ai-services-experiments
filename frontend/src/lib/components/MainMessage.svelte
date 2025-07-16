<!-- MainMessage.svelte -->
<script>
	export let headerText = '';
	export let mainText = '';
	export let subtitle = '';
	export let center = false;
</script>

<div class="message-container" class:center>
	{#if headerText}
		<div class="message-header">
			<div class="computer-icon">💻</div>
			<span class="header-text">{headerText}</span>
		</div>
	{/if}

	<div class="main-message">
		{mainText}
		{#if subtitle}
			<div class="subtitle">{subtitle}</div>
		{/if}
	</div>
</div>

<style>
	.message-container {
		text-align: left;
	}

	.message-container.center {
		text-align: center;
	}

	.message-header {
		display: flex;
		align-items: center;
		gap: 12px;
		margin-bottom: 20px;
		color: #888;
		font-size: 2rem;
	}

	.computer-icon {
		font-size: 28px;
	}

	.header-text {
		font-weight: normal;
	}

	.main-message {
		font-size: 72px;
		font-style: italic;
		font-weight: 700;
		line-height: 1.15;
		color: #000;
		margin-bottom: 80px;
	}

	.subtitle {
		font-size: 2rem;
		font-style: normal;
		font-weight: 400;
		color: #999;
		margin-top: 20px;
	}
</style>
