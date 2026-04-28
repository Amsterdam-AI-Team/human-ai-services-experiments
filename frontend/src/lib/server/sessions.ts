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
	let s = CHAT_SESSIONS.get(sid);
	if (!s) {
		s = { history: [], checklist: {}, intentcode, draft: "", language: null };
		CHAT_SESSIONS.set(sid, s);
	}
	return s;
}

export function getYapSession(sid: string): YapSession | undefined {
	return YAP_SESSIONS.get(sid);
}

export function setYapSession(sid: string, session: YapSession): void {
	YAP_SESSIONS.set(sid, session);
}
