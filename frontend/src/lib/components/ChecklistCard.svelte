<!-- ChecklistCard.svelte -->
<script lang="ts">
	interface ChecklistItem {
		id: string;
		text: string;
		checked: boolean;
	}

	let { 
		items = [], 
		title = 'Checklist', 
		subtitle = 'Vermeld de volgende gegevens voor een complete aanvraag:',
		onItemChange 
	} = $props<{
		items: ChecklistItem[];
		title?: string;
		subtitle?: string;
		onItemChange?: (id: string, checked: boolean) => void;
	}>();

	const completedCount = $derived(items.filter((item: ChecklistItem) => item.checked).length);
	const totalCount = $derived(items.length);
	const progressPercentage = $derived(totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0);

	function handleCheckboxChange(id: string, checked: boolean) {
		if (onItemChange) {
			onItemChange(id, checked);
		}
	}
</script>

<div class="checklist-card">
	<div class="checklist-header">
		<h3 class="checklist-title">{title}</h3>
		<p class="checklist-subtitle">{subtitle}</p>
	</div>

	<div class="checklist-items">
		{#each items as item (item.id)}
			<div class="checklist-item">
				<input 
					type="checkbox" 
					bind:checked={item.checked}
					disabled
				/>
				<span class="checkmark"></span>
				<span class="item-text">{item.text}</span>
			</div>
		{/each}
	</div>

	<div class="progress-section">
		<div class="progress-bar">
			<div class="progress-fill" style="width: {progressPercentage}%"></div>
		</div>
		<span class="progress-text">{progressPercentage}% compleet</span>
	</div>
</div>

<style>
	.checklist-card {
		background: #f3e8ff;
		border: 1px solid #e2d8f0;
		border-radius: 12px;
		padding: 1.5rem;
		margin-bottom: 1.5rem;
	}

	.checklist-header {
		margin-bottom: 1.5rem;
	}

	.checklist-title {
		font-size: 1.2rem;
		font-weight: 600;
		color: #553c9a;
		margin: 0 0 0.5rem 0;
	}

	.checklist-subtitle {
		font-size: 0.9rem;
		color: #6b46c1;
		margin: 0;
		line-height: 1.4;
	}

	.checklist-items {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		margin-bottom: 1.5rem;
	}

	.checklist-item {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		cursor: default;
		font-size: 0.9rem;
		color: #553c9a;
		line-height: 1.4;
	}

	.checklist-item input[type="checkbox"] {
		display: none;
	}

	.checkmark {
		width: 20px;
		height: 20px;
		border: 2px solid #a78bfa;
		border-radius: 4px;
		position: relative;
		flex-shrink: 0;
		background: white;
		transition: all 0.2s ease;
	}

	.checklist-item input[type="checkbox"]:checked + .checkmark {
		background: #8b5cf6;
		border-color: #8b5cf6;
	}

	.checklist-item input[type="checkbox"]:checked + .checkmark::after {
		content: '';
		position: absolute;
		left: 6px;
		top: 2px;
		width: 6px;
		height: 10px;
		border: solid white;
		border-width: 0 2px 2px 0;
		transform: rotate(45deg);
	}

	.item-text {
		flex: 1;
	}

	.progress-section {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.progress-bar {
		flex: 1;
		height: 8px;
		background: #e2d8f0;
		border-radius: 4px;
		overflow: hidden;
	}

	.progress-fill {
		height: 100%;
		background: #8b5cf6;
		border-radius: 4px;
		transition: width 0.3s ease;
	}

	.progress-text {
		font-size: 0.85rem;
		color: #6b46c1;
		font-weight: 500;
		white-space: nowrap;
	}
</style>