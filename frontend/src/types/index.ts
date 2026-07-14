// ============================================================
// AUTH
// ============================================================
export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

// ============================================================
// SESSIONS
// ============================================================
export interface ChatSession {
  id: string;
  user_id: string;
  title: string;
  updated_at: string;
}

export interface ChatSessionDetail extends ChatSession {
  messages: Message[];
}

// ============================================================
// MESSAGES
// ============================================================
export type MessageRole = 'user' | 'agent';

export interface ExportLink {
  type: 'google_docs' | 'google_sheets';
  url: string;
  title: string;
}

export interface MessageFlags {
  expert_required?: boolean;
  python_repl?: boolean;
  web_fallback?: boolean;
  export_to_workspace?: boolean;
}

export interface Message {
  id: string;
  session_id: string;
  role: MessageRole;
  content: string;
  export_links?: ExportLink[];
  flags?: MessageFlags;
  created_at: string;
}

// ============================================================
// WEBSOCKET EVENTS
// ============================================================
export type WSEventType =
  | 'status'
  | 'node_update'
  | 'token'
  | 'final_answer'
  | 'export_link'
  | 'error';

export interface WSEvent {
  type: WSEventType;
  id?: string;
  // for node_update
  node?: string;
  // for token / final_answer
  content?: string;
  // for export_link
  link_type?: string;
  url?: string;
  link_title?: string;
  // for error
  message?: string;
  // generic status message
  detail?: string;
  // query correction metadata
  original_question?: string | null;
  corrected_question?: string | null;
  // export links object (docs/sheets)
  export_links?: Record<string, string | null>;
  flags?: MessageFlags;
}

// ============================================================
// UI STATE
// ============================================================
export type NodeStatus = 'running' | 'done';

export interface ActiveNode {
  name: string;
  status: NodeStatus;
}

export interface StreamingMessage {
  role: 'agent';
  content: string;
  activeNodes: ActiveNode[];
  exportLinks: ExportLink[];
  isStreaming: boolean;
  // query correction
  original_question?: string | null;
  corrected_question?: string | null;
}

export type DisplayMessage =
  | (Message & { isStreaming?: false; original_question?: string | null; corrected_question?: string | null })
  | (StreamingMessage & { id?: string; session_id?: string; created_at?: string; isStreaming: true });
