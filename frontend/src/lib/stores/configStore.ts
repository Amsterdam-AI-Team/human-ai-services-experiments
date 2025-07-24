import { writable } from "svelte/store";

interface AppConfig {
  similarityThreshold: number;
  // Add other configuration options here as needed
}

const defaultConfig: AppConfig = {
  similarityThreshold: 0.5, // Default threshold for intent matching
};

function createConfigStore() {
  const { subscribe, set, update } = writable<AppConfig>(defaultConfig);

  return {
    subscribe,
    setSimilarityThreshold: (threshold: number) => {
      if (threshold < 0 || threshold > 1) {
        throw new Error("Similarity threshold must be between 0 and 1");
      }
      update((config) => ({ ...config, similarityThreshold: threshold }));
    },
    resetToDefaults: () => set(defaultConfig),
    updateConfig: (updates: Partial<AppConfig>) =>
      update((config) => ({ ...config, ...updates })),
  };
}

export const configStore = createConfigStore();

// Export getter functions for easier access
export const getSimilarityThreshold = () => {
  let threshold = 0.5;
  configStore.subscribe((config) => (threshold = config.similarityThreshold))();
  return threshold;
};
