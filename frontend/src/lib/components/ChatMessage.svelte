<!-- ChatMessage.svelte -->
<script lang="ts">
	import { _ } from "svelte-i18n";

	type MessageType = "gemeente-ai" | "user-message";

	let {
		type,
		content,
		sender = "",
	} = $props<{
		type: MessageType;
		content: string;
		sender?: string;
	}>();

	// Process content to convert literal \n to actual newlines
	const processedContent = $derived(() => content.replace(/\\n/g, "\n"));
</script>

<div class="chat-message {type}">
	{#if type === "gemeente-ai"}
		<div class="message-header">
			<img
				src="/images/chat-gemeente-avatar.png"
				alt="Gemeente AI"
				class="avatar"
			/>
			<span class="sender-name">{sender || "Gemeente AI-agent:"}</span>
		</div>
	{/if}
	{#if type === "user-message"}
		<div class="message-header">
			<!-- <img src="/images/chat-gemeente-avatar.png" alt="Gemeente AI" class="avatar" /> -->
			<span class="sender-name">{sender || $_("messages.yourAgent")}</span
			>
		</div>
	{/if}

	<div class="message-content">
		{#if processedContent().includes("\n")}
			{#each processedContent().split("\n") as paragraph}
				{#if paragraph.trim()}
					<p>{paragraph}</p>
				{/if}
			{/each}
		{:else}
			<p>{processedContent()}</p>
		{/if}
	</div>
</div>

<style>
	.chat-message {
		padding: 1rem;
		max-width: 80%;
		margin-bottom: 1rem;
		font-family: "Amsterdam Sans", Arial, sans-serif;
	}

	.chat-message.gemeente-ai {
		background: #f8f9fa;
		align-self: flex-start;
	}

	.chat-message.user-message {
		background: #e5e5e5;
		align-self: flex-end;
		margin-left: auto;
	}

	.message-header {
		display: flex;
		align-items: center;
		gap: 0rem;
		margin-bottom: 0.5rem;
	}

	.avatar {
		width: 36px;
		height: 36px;
		flex-shrink: 0;
		margin-left: -35px;
	}

	.sender-name {
		font-weight: 600;
		color: #333;
		font-size: 1rem;
	}

	.message-content {
		color: #333;
		line-height: 1.4;
	}

	.message-content p {
		margin: 0 0 0.5rem 0;
		font-size: 1rem;
	}

	.message-content p:last-child {
		margin-bottom: 0;
	}
</style>
