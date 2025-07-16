<!-- ChatMessage.svelte -->
<script lang="ts">
	type MessageType = 'gemeente-ai' | 'user-message';
	
	let { type, content, sender = '' } = $props<{
		type: MessageType;
		content: string;
		sender?: string;
	}>();
</script>

<div class="chat-message {type}">
	{#if type === 'gemeente-ai'}
		<div class="message-header">
			<span class="sender-indicator">🔴</span>
			<span class="sender-name">{sender || 'Gemeente AI-agent:'}</span>
		</div>
	{/if}
	
	<div class="message-content">
		{#if content.includes('\n')}
			{#each content.split('\n') as paragraph}
				{#if paragraph.trim()}
					<p>{paragraph}</p>
				{/if}
			{/each}
		{:else}
			<p>{content}</p>
		{/if}
	</div>
</div>

<style>
	.chat-message {
		border-radius: 12px;
		padding: 1rem;
		max-width: 80%;
		margin-bottom: 1rem;
	}

	.chat-message.gemeente-ai {
		background: #f8f9fa;
		border: 1px solid #e9ecef;
		align-self: flex-start;
	}

	.chat-message.user-message {
		background: #e9ecef;
		border: 1px solid #dee2e6;
		align-self: flex-end;
		margin-left: auto;
	}

	.message-header {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 0.5rem;
	}

	.sender-indicator {
		font-size: 0.8rem;
		line-height: 1;
	}

	.sender-name {
		font-weight: 600;
		color: #333;
		font-size: 0.9rem;
	}

	.message-content {
		color: #333;
		line-height: 1.4;
	}

	.message-content p {
		margin: 0 0 0.5rem 0;
		font-size: 0.9rem;
	}

	.message-content p:last-child {
		margin-bottom: 0;
	}
</style>