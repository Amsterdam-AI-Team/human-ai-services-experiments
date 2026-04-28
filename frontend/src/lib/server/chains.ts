import { z } from "zod";
import {
	AZURE_OPENAI_ENDPOINT,
	AZURE_OPENAI_API_KEY,
	OPENAI_API_VERSION,
	AZURE_OPENAI_DEPLOYMENT_NAME,
} from "$env/static/private";
import {
	getSystemPrompt,
	getLanguageSuffix,
	getTranslation,
	type Intent,
	type LanguageCode,
} from "./i18n";
import {
	buildStepSchema,
	BurgerTurnSchema,
	GemeenteTurnSchema,
	type BurgerTurn,
	type GemeenteTurn,
} from "./schemas";
import type { ChatHistoryMessage, ChatSession, YapMessage } from "./sessions";

const API_VERSION = OPENAI_API_VERSION || "2025-01-01-preview";

interface ChatMessage {
	role: "system" | "user" | "assistant";
	content: string;
}

function chatUrl(): string {
	if (!AZURE_OPENAI_ENDPOINT) throw new Error("AZURE_OPENAI_ENDPOINT not set");
	if (!AZURE_OPENAI_DEPLOYMENT_NAME) throw new Error("AZURE_OPENAI_DEPLOYMENT_NAME not set");
	const base = AZURE_OPENAI_ENDPOINT.replace(/\/$/, "");
	return `${base}/openai/deployments/${AZURE_OPENAI_DEPLOYMENT_NAME}/chat/completions?api-version=${API_VERSION}`;
}

async function chatCompletionJSON(messages: ChatMessage[], temperature = 0.4): Promise<string> {
	if (!AZURE_OPENAI_API_KEY) throw new Error("AZURE_OPENAI_API_KEY not set");
	const r = await fetch(chatUrl(), {
		method: "POST",
		headers: {
			"api-key": AZURE_OPENAI_API_KEY,
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			messages,
			temperature,
			response_format: { type: "json_object" },
		}),
	});
	if (!r.ok) {
		const body = await r.text();
		throw new Error(`Azure chat failed: ${r.status} ${body.slice(0, 500)}`);
	}
	const data = (await r.json()) as { choices: { message: { content: string } }[] };
	return data.choices[0].message.content;
}

async function callTyped<T extends z.ZodTypeAny>(
	messages: ChatMessage[],
	schema: T,
	temperature = 0.4,
): Promise<z.infer<T>> {
	const raw = await chatCompletionJSON(messages, temperature);
	let parsed: unknown;
	try {
		parsed = JSON.parse(raw);
	} catch (e) {
		throw new Error(`LLM returned non-JSON: ${raw.slice(0, 200)}`);
	}
	return schema.parse(parsed);
}

// Strip JSON Schema 'default' annotations recursively. Defaults in the schema
// signal to the LLM that an empty/false/null value is acceptable, which
// undermines instructions like "ask a follow-up question for every false
// boolean". We still apply Zod defaults at parse time for robustness.
function stripDefaults(node: unknown): unknown {
	if (Array.isArray(node)) return node.map(stripDefaults);
	if (node && typeof node === "object") {
		const out: Record<string, unknown> = {};
		for (const [k, v] of Object.entries(node as Record<string, unknown>)) {
			if (k === "default") continue;
			out[k] = stripDefaults(v);
		}
		return out;
	}
	return node;
}

// ─── Chat (juridisch medewerker) ────────────────────────────────────────────

// Same shape as LangChain Python's JsonOutputParser.get_format_instructions().
// Without the explicit instance-vs-schema example the model often replies with
// the schema itself instead of a valid instance.
function formatInstructions(schemaJSON: string): string {
	return [
		"The output should be formatted as a JSON instance that conforms to the JSON schema below.",
		"",
		'As an example, for the schema {"properties": {"foo": {"description": "a list of strings", "type": "array", "items": {"type": "string"}}}, "required": ["foo"]}',
		'the object {"foo": ["bar", "baz"]} is a well-formatted instance of the schema. The object {"properties": {"foo": ["bar", "baz"]}} is NOT well-formatted.',
		"",
		"Here is the output schema:",
		"```",
		schemaJSON,
		"```",
	].join("\n");
}

function buildChatSystemPrompt(language: LanguageCode, schemaJSON: string): string {
	const p = getSystemPrompt(language, "juridisch_medewerker");
	const suffix = getLanguageSuffix(language);
	return [
		p.role ?? "",
		formatInstructions(schemaJSON),
		p.workflow ?? "",
		p.important ?? "",
		"Belangrijke regel voor `vragen`: zo lang er ook maar één boolean op `false` staat, MOET de array `vragen` minstens één concrete vraag bevatten. Een lege `vragen`-array is alléén toegestaan als ALLE booleans op `true` staan.",
		`- ${suffix}`,
	]
		.filter(Boolean)
		.join("\n\n");
}

function historyToMessages(history: ChatHistoryMessage[]): ChatMessage[] {
	return history.map((m) => ({ role: m.role, content: m.content }));
}

export async function runChat(
	intent: Intent,
	session: ChatSession,
	userText: string,
	language: LanguageCode,
): Promise<{ stepObj: Record<string, unknown>; reply: string; checklist: Record<string, boolean>; finished: boolean; draft: string }> {
	const stepSchema = buildStepSchema(intent);
	const schemaJSON = JSON.stringify(stripDefaults(z.toJSONSchema(stepSchema)), null, 2);
	const messages: ChatMessage[] = [
		{ role: "system", content: buildChatSystemPrompt(language, schemaJSON) },
	];

	if (Object.keys(session.checklist).length > 0 || session.draft) {
		messages.push({
			role: "assistant",
			content: JSON.stringify({ checklist: session.checklist, draft: session.draft }),
		});
	}

	messages.push(...historyToMessages(session.history));
	messages.push({ role: "user", content: userText });

	const stepObj = (await callTyped(messages, stepSchema)) as Record<string, unknown> & {
		draft: string;
		vragen: string[];
	};

	session.draft = stepObj.draft ?? "";
	const checklist: Record<string, boolean> = {};
	for (const [k, v] of Object.entries(stepObj)) {
		if (k === "draft" || k === "vragen") continue;
		if (typeof v === "boolean") checklist[k] = v;
	}
	const finished = Object.values(checklist).every(Boolean) && Object.keys(checklist).length > 0;
	const fallback = getTranslation(language, "responses.all_steps_completed", "Alle stappen zijn afgerond!");
	const reply = stepObj.vragen?.[0] || fallback;

	return { stepObj, reply, checklist, finished, draft: session.draft };
}

// ─── Yap (burger / gemeente) ────────────────────────────────────────────────

function buildYapSystemPrompt(
	role: "burger" | "gemeente",
	transcript: string,
	language: LanguageCode,
	schemaJSON: string,
): string {
	const p = getSystemPrompt(language, role === "burger" ? "burger_system" : "gemeente_system");
	const suffix = getLanguageSuffix(language);
	const transcriptLabel = getTranslation(
		language,
		"labels.transcript",
		"Transcript (door de gebruiker aangeleverd):",
	);

	const contextBlock =
		role === "burger"
			? `<Context>\n${p.context ?? ""}\n${transcriptLabel}\n${transcript}\n</Context>`
			: `<Context>\n${p.context ?? ""}\n</Context>`;

	return [
		contextBlock,
		`<Objective>\n${p.objective ?? ""}\n</Objective>`,
		`<Style>\n${p.style ?? ""}\n${formatInstructions(schemaJSON)}\n</Style>`,
		`<Tone>\n${p.tone ?? ""}\n</Tone>`,
		`<Audience>\n${p.audience ?? ""}\n</Audience>`,
		`<Response>\n${p.response ?? ""}\n${suffix}\n</Response>`,
	].join("\n\n");
}

function yapHistoryToMessages(history: YapMessage[]): ChatMessage[] {
	// burger = HumanMessage, gemeente = AIMessage (matches Python mapping)
	return history.map((m) => ({
		role: m.speaker === "burger" ? "user" : "assistant",
		content: m.message,
	}));
}

export async function yapGenerate(
	role: "burger" | "gemeente",
	transcript: string,
	history: YapMessage[],
	language: LanguageCode,
): Promise<BurgerTurn | GemeenteTurn> {
	const schema = role === "burger" ? BurgerTurnSchema : GemeenteTurnSchema;
	const schemaJSON = JSON.stringify(stripDefaults(z.toJSONSchema(schema)), null, 2);
	const messages: ChatMessage[] = [
		{ role: "system", content: buildYapSystemPrompt(role, transcript, language, schemaJSON) },
		...yapHistoryToMessages(history),
	];
	return await callTyped(messages, schema);
}
