import { writable } from "svelte/store";
import { _, isLoading } from "svelte-i18n";
import { get } from "svelte/store";

export interface AppError {
  id: string;
  message: string;
  type: "error" | "warning" | "info";
  timestamp: Date;
  dismissible: boolean;
}

function createErrorStore() {
  const { subscribe, set, update } = writable<AppError[]>([]);

  return {
    subscribe,
    addError: (
      message: string,
      type: "error" | "warning" | "info" = "error",
      dismissible = true,
    ) => {
      const error: AppError = {
        id: crypto.randomUUID(),
        message,
        type,
        timestamp: new Date(),
        dismissible,
      };
      update((errors) => [error, ...errors]);

      // Auto-dismiss after 5 seconds for dismissible errors
      if (dismissible) {
        setTimeout(() => {
          update((errors) => errors.filter((e) => e.id !== error.id));
        }, 5000);
      }
    },
    removeError: (id: string) => {
      update((errors) => errors.filter((error) => error.id !== id));
    },
    clearAll: () => set([]),
  };
}

export const errorStore = createErrorStore();

// Helper functions for common error scenarios
export const showError = (message: string) =>
  errorStore.addError(message, "error");
export const showWarning = (message: string) =>
  errorStore.addError(message, "warning");
export const showInfo = (message: string) =>
  errorStore.addError(message, "info");

// Helper for API errors with translation support
export const handleApiError = (error: unknown, context: string = "apiCall") => {
  const $_ = get(_);
  const $isLoading = get(isLoading);

  // Fallback to context if translations aren't loaded yet
  const translatedContext =
    !$isLoading && $_ ? $_(`errors.${context}`) : context;
  const unknownErrorMsg =
    !$isLoading && $_ ? $_("errors.unknownError") : "Unknown error occurred";

  const message = error instanceof Error ? error.message : unknownErrorMsg;
  errorStore.addError(`${translatedContext}: ${message}`, "error");
  console.error(`Error in ${translatedContext}:`, error);
};

// Translated error helpers
export const showTranslatedError = (errorKey: string) => {
  const $_ = get(_);
  const $isLoading = get(isLoading);
  const message = !$isLoading && $_ ? $_(errorKey) : errorKey;
  errorStore.addError(message, "error");
};

export const showTranslatedWarning = (warningKey: string) => {
  const $_ = get(_);
  const $isLoading = get(isLoading);
  const message = !$isLoading && $_ ? $_(warningKey) : warningKey;
  errorStore.addError(message, "warning");
};

export const showTranslatedInfo = (infoKey: string) => {
  const $_ = get(_);
  const $isLoading = get(isLoading);
  const message = !$isLoading && $_ ? $_(infoKey) : infoKey;
  errorStore.addError(message, "info");
};
