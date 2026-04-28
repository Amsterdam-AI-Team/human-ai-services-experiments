export interface ChatHistoryMessage {
	role: "user" | "assistant";
	content: string;
}

export interface ChatSession {
	history: ChatHistoryMessage[];
	checklist: Record<string, boolean>;
	intentcode: string;
	draft: string;
	language: string | null;
}

export interface YapMessage {
	speaker: "burger" | "gemeente";
	message: string;
}

export interface YapSession {
	transcript: string;
	messages: YapMessage[];
	turn: number;
	finished: boolean;
	draft: string | null;
	language: string;
}

const CHAT_SESSIONS = new Map<string, ChatSession>();
const YAP_SESSIONS = new Map<string, YapSession>();

export function newSessionId(): string {
	return crypto.randomUUID();
}

export function getOrCreateChatSession(sid: string, intentcode: string): ChatSession {
	const existing = CHAT_SESSIONS.get(sid);
	// Reset on intent switch: an existing session belongs to its original
	// intent and its history/checklist would be meaningless for a different
	// flow. Reusing the session_id is fine; the contents start fresh.
	if (existing && existing.intentcode === intentcode) return existing;
	const fresh: ChatSession = {
		history: [],
		checklist: {},
		intentcode,
		draft: "",
		language: null,
	};
	CHAT_SESSIONS.set(sid, fresh);
	return fresh;
}

export function getYapSession(sid: string): YapSession | undefined {
	return YAP_SESSIONS.get(sid);
}

export function setYapSession(sid: string, session: YapSession): void {
	YAP_SESSIONS.set(sid, session);
}
