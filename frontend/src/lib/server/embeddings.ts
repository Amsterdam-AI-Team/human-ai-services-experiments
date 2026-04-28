import { env } from "$env/dynamic/private";
import { INTENTS } from "./intents";
import type { Intent } from "./i18n";

const API_VERSION = env.OPENAI_API_VERSION || "2024-10-01-preview";

function embeddingUrl(): string {
	const dep = env.AZURE_OPENAI_EMBEDDING_DEPLOYMENT;
	if (!dep) throw new Error("AZURE_OPENAI_EMBEDDING_DEPLOYMENT not set");
	// Accept either a deployment name or a full URL.
	if (/^https?:\/\//.test(dep)) return dep;
	if (!env.AZURE_OPENAI_ENDPOINT) throw new Error("AZURE_OPENAI_ENDPOINT not set");
	const base = env.AZURE_OPENAI_ENDPOINT.replace(/\/$/, "");
	return `${base}/openai/deployments/${dep}/embeddings?api-version=${API_VERSION}`;
}

function embeddingApiKey(): string {
	// Embeddings may live on a different Azure resource than chat/transcribe;
	// allow a separate key, fall back to the main one.
	const key = env.AZURE_OPENAI_EMBEDDING_API_KEY || env.AZURE_OPENAI_API_KEY;
	if (!key) throw new Error("AZURE_OPENAI_API_KEY (or AZURE_OPENAI_EMBEDDING_API_KEY) not set");
	return key;
}

export async function embed(input: string | string[]): Promise<number[][]> {
	const r = await fetch(embeddingUrl(), {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"api-key": embeddingApiKey(),
		},
		body: JSON.stringify({ input }),
	});
	if (!r.ok) {
		const body = await r.text();
		throw new Error(`Azure embeddings failed: ${r.status} ${body.slice(0, 500)}`);
	}
	const data = (await r.json()) as { data: { embedding: number[] }[] };
	return data.data.map((d) => d.embedding);
}

export async function embedOne(input: string): Promise<number[]> {
	const [vec] = await embed(input);
	return vec;
}

function l2Normalize(v: number[]): number[] {
	let sum = 0;
	for (const x of v) sum += x * x;
	const norm = Math.sqrt(sum) || 1;
	return v.map((x) => x / norm);
}

export function cosineNormalized(a: number[], b: number[]): number {
	let dot = 0;
	for (let i = 0; i < a.length; i++) dot += a[i] * b[i];
	return dot;
}

let intentEmbeddingsPromise: Promise<{ intent: Intent; vec: number[] }[]> | null = null;

export function getIntentEmbeddings(): Promise<{ intent: Intent; vec: number[] }[]> {
	if (!intentEmbeddingsPromise) {
		intentEmbeddingsPromise = (async () => {
			const vecs = await embed(INTENTS.map((i) => i.intent));
			return INTENTS.map((intent, i) => ({ intent, vec: l2Normalize(vecs[i]) }));
		})();
	}
	return intentEmbeddingsPromise;
}

export async function topKIntents(
	query: string,
	k: number,
): Promise<{ intent: Intent; similarity: number }[]> {
	const [qRaw, intentVecs] = await Promise.all([embedOne(query), getIntentEmbeddings()]);
	const q = l2Normalize(qRaw);
	const scored = intentVecs.map(({ intent, vec }) => ({
		intent,
		similarity: cosineNormalized(q, vec),
	}));
	scored.sort((a, b) => b.similarity - a.similarity);
	return scored.slice(0, Math.max(1, Math.min(k, scored.length)));
}
