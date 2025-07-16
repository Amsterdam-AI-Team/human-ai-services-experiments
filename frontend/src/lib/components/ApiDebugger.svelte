<!-- ApiDebugger.svelte -->
<script lang="ts">
	import { apiResponses, clearApiResponsesForEndpoint } from '$lib/stores/apiStore';

	let { endpoint } = $props<{
		endpoint?: string;
	}>();

	// Get responses, optionally filtered by endpoint
	const responses = $derived(
		endpoint 
			? $apiResponses.filter(r => r.endpoint === endpoint)
			: $apiResponses
	);

	// Get the latest response for display
	const latestResponse = $derived(responses.slice(-1)[0]);

	function formatTimestamp(timestamp: number): string {
		return new Date(timestamp).toLocaleTimeString();
	}

	function formatJson(data: any): string {
		return JSON.stringify(data, null, 2);
	}
</script>

{#if latestResponse}
	<div class="api-debugger">
		<div class="debugger-header">
			<div class="header-top">
				<h3>🐛 API Debug</h3>
				{#if endpoint}
					<button onclick={() => clearApiResponsesForEndpoint(endpoint)} class="clear-button">
						Clear {endpoint} responses
					</button>
				{/if}
			</div>
			<div class="endpoint-info">
				<span class="endpoint-label">Endpoint:</span>
				<code class="endpoint-value">{latestResponse.endpoint}</code>
			</div>
			<div class="timestamp">
				<span class="timestamp-label">Last updated:</span>
				<span class="timestamp-value">{formatTimestamp(latestResponse.timestamp)}</span>
			</div>
		</div>

		<div class="response-content">
			<div class="response-header">
				<span class="response-label">Response Data:</span>
				<span class="response-count">({responses.length} total)</span>
			</div>
			<pre class="response-json">{formatJson(latestResponse.data)}</pre>
		</div>

		{#if responses.length > 1}
			<details class="response-history">
				<summary>View History ({responses.length - 1} previous)</summary>
				<div class="history-list">
					{#each responses.slice(0, -1).reverse() as response}
						<div class="history-item">
							<div class="history-header">
								<span class="history-timestamp">{formatTimestamp(response.timestamp)}</span>
								<code class="history-endpoint">{response.endpoint}</code>
							</div>
							<pre class="history-json">{formatJson(response.data)}</pre>
						</div>
					{/each}
				</div>
			</details>
		{/if}
	</div>
{:else}
	<div class="api-debugger empty">
		<div class="empty-state">
			<span class="empty-icon">📡</span>
			<p class="empty-text">No API responses yet</p>
			{#if endpoint}
				<p class="empty-subtext">Waiting for responses from <code>{endpoint}</code></p>
			{/if}
		</div>
	</div>
{/if}

<style>
	.api-debugger {
		background: #f8f9fa;
		border: 1px solid #dee2e6;
		border-radius: 8px;
		padding: 1rem;
		margin: 1rem 0;
		font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
	}

	.debugger-header {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		margin-bottom: 1rem;
		padding-bottom: 1rem;
		border-bottom: 1px solid #dee2e6;
	}

	.header-top {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
	}

	.debugger-header h3 {
		margin: 0;
		color: #333;
		font-size: 1.1rem;
		font-weight: 600;
	}

	.clear-button {
		padding: 0.25rem 0.5rem;
		background-color: #dc3545;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		font-size: 0.75rem;
		font-weight: 500;
	}

	.clear-button:hover {
		background-color: #c82333;
	}

	.endpoint-info, .timestamp {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.85rem;
	}

	.endpoint-label, .timestamp-label {
		color: #666;
		font-weight: 500;
	}

	.endpoint-value {
		background: #e9ecef;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		font-size: 0.8rem;
		color: #0d6efd;
	}

	.timestamp-value {
		color: #666;
	}

	.response-content {
		margin-bottom: 1rem;
	}

	.response-header {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 0.5rem;
	}

	.response-label {
		font-weight: 600;
		color: #333;
		font-size: 0.9rem;
	}

	.response-count {
		color: #666;
		font-size: 0.8rem;
	}

	.response-json {
		background: #ffffff;
		border: 1px solid #e9ecef;
		border-radius: 4px;
		padding: 1rem;
		overflow-x: auto;
		font-size: 0.8rem;
		line-height: 1.4;
		margin: 0;
		white-space: pre-wrap;
		word-wrap: break-word;
	}

	.response-history {
		margin-top: 1rem;
		border-top: 1px solid #dee2e6;
		padding-top: 1rem;
	}

	.response-history summary {
		cursor: pointer;
		font-weight: 500;
		color: #666;
		font-size: 0.9rem;
		padding: 0.5rem 0;
	}

	.response-history summary:hover {
		color: #333;
	}

	.history-list {
		margin-top: 1rem;
	}

	.history-item {
		margin-bottom: 1rem;
		padding: 0.75rem;
		background: #ffffff;
		border: 1px solid #e9ecef;
		border-radius: 4px;
	}

	.history-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
		padding-bottom: 0.5rem;
		border-bottom: 1px solid #f1f3f4;
	}

	.history-timestamp {
		color: #666;
		font-size: 0.8rem;
	}

	.history-endpoint {
		background: #f8f9fa;
		padding: 0.2rem 0.4rem;
		border-radius: 3px;
		font-size: 0.75rem;
		color: #0d6efd;
	}

	.history-json {
		background: #f8f9fa;
		border: 1px solid #e9ecef;
		border-radius: 3px;
		padding: 0.75rem;
		overflow-x: auto;
		font-size: 0.75rem;
		line-height: 1.3;
		margin: 0;
		white-space: pre-wrap;
		word-wrap: break-word;
	}

	.empty {
		text-align: center;
		padding: 2rem;
	}

	.empty-state {
		color: #666;
	}

	.empty-icon {
		font-size: 2rem;
		display: block;
		margin-bottom: 1rem;
	}

	.empty-text {
		margin: 0 0 0.5rem 0;
		font-size: 1rem;
		font-weight: 500;
	}

	.empty-subtext {
		margin: 0;
		font-size: 0.85rem;
		color: #999;
	}

	.empty-subtext code {
		background: #e9ecef;
		padding: 0.2rem 0.4rem;
		border-radius: 3px;
		font-size: 0.8rem;
	}

	@media (max-width: 768px) {
		.api-debugger {
			font-size: 0.9rem;
		}
		
		.response-json, .history-json {
			font-size: 0.75rem;
		}
	}
</style>