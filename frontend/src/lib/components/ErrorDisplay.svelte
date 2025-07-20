<script lang="ts">
	import { _ } from 'svelte-i18n';
	import { errorStore, type AppError } from '$lib/stores/errorStore';

	function dismissError(id: string) {
		errorStore.removeError(id);
	}

	function getErrorIcon(type: AppError['type']) {
		switch (type) {
			case 'error': return '❌';
			case 'warning': return '⚠️';
			case 'info': return 'ℹ️';
			default: return '❌';
		}
	}

	function getErrorClass(type: AppError['type']) {
		switch (type) {
			case 'error': return 'error-item--error';
			case 'warning': return 'error-item--warning';
			case 'info': return 'error-item--info';
			default: return 'error-item--error';
		}
	}
</script>

{#if $errorStore.length > 0}
	<div class="error-container">
		{#each $errorStore as error (error.id)}
			<div class="error-item {getErrorClass(error.type)}">
				<span class="error-icon">{getErrorIcon(error.type)}</span>
				<span class="error-message">{error.message}</span>
				{#if error.dismissible}
					<button 
						class="error-dismiss" 
						onclick={() => dismissError(error.id)}
						aria-label={$_('errors.dismissLabel')}
					>
						✕
					</button>
				{/if}
			</div>
		{/each}
	</div>
{/if}

<style>
	.error-container {
		position: fixed;
		top: 80px; /* Below header */
		right: 1rem;
		z-index: 1000;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		max-width: 400px;
	}

	.error-item {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem 1rem;
		border-radius: 8px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		animation: slideIn 0.3s ease-out;
		border-left: 4px solid;
	}

	.error-item--error {
		background-color: #fef2f2;
		border-left-color: #dc2626;
		color: #991b1b;
	}

	.error-item--warning {
		background-color: #fffbeb;
		border-left-color: #d97706;
		color: #92400e;
	}

	.error-item--info {
		background-color: #eff6ff;
		border-left-color: #2563eb;
		color: #1d4ed8;
	}

	.error-icon {
		font-size: 1.1rem;
		flex-shrink: 0;
	}

	.error-message {
		flex: 1;
		font-size: 0.9rem;
		line-height: 1.4;
	}

	.error-dismiss {
		background: none;
		border: none;
		font-size: 1.1rem;
		cursor: pointer;
		color: inherit;
		opacity: 0.7;
		padding: 0.25rem;
		border-radius: 4px;
		transition: opacity 0.2s, background-color 0.2s;
	}

	.error-dismiss:hover {
		opacity: 1;
		background-color: rgba(0, 0, 0, 0.1);
	}

	@keyframes slideIn {
		from {
			opacity: 0;
			transform: translateX(100%);
		}
		to {
			opacity: 1;
			transform: translateX(0);
		}
	}

	@media (max-width: 768px) {
		.error-container {
			left: 1rem;
			right: 1rem;
			max-width: none;
		}
		
		.error-item {
			padding: 0.5rem 0.75rem;
		}
		
		.error-message {
			font-size: 0.85rem;
		}
	}
</style>