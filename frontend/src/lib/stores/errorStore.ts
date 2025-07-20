import { writable } from 'svelte/store';

export interface AppError {
	id: string;
	message: string;
	type: 'error' | 'warning' | 'info';
	timestamp: Date;
	dismissible: boolean;
}

function createErrorStore() {
	const { subscribe, set, update } = writable<AppError[]>([]);

	return {
		subscribe,
		addError: (message: string, type: 'error' | 'warning' | 'info' = 'error', dismissible = true) => {
			const error: AppError = {
				id: crypto.randomUUID(),
				message,
				type,
				timestamp: new Date(),
				dismissible
			};
			update(errors => [error, ...errors]);
			
			// Auto-dismiss after 5 seconds for dismissible errors
			if (dismissible) {
				setTimeout(() => {
					update(errors => errors.filter(e => e.id !== error.id));
				}, 5000);
			}
		},
		removeError: (id: string) => {
			update(errors => errors.filter(error => error.id !== id));
		},
		clearAll: () => set([])
	};
}

export const errorStore = createErrorStore();

// Helper functions for common error scenarios
export const showError = (message: string) => errorStore.addError(message, 'error');
export const showWarning = (message: string) => errorStore.addError(message, 'warning');
export const showInfo = (message: string) => errorStore.addError(message, 'info');

// Helper for API errors
export const handleApiError = (error: unknown, context: string = 'API call') => {
	const message = error instanceof Error ? error.message : 'Unknown error occurred';
	errorStore.addError(`${context}: ${message}`, 'error');
	console.error(`Error in ${context}:`, error);
};