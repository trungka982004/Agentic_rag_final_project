import axios from 'axios';
import type {
  AuthTokens,
  User,
  ChatSession,
  ChatSessionDetail,
} from '@/types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Attach Bearer token from localStorage on each request
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Redirect to login on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

// ============================================================
// AUTH
// ============================================================
export async function apiRegister(email: string, password: string): Promise<User> {
  const res = await api.post<User>('/api/auth/register', { email, password });
  return res.data;
}

export async function apiLogin(email: string, password: string): Promise<AuthTokens> {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  const res = await api.post<AuthTokens>('/api/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return res.data;
}

export async function apiGetMe(): Promise<User> {
  const res = await api.get<User>('/api/auth/me');
  return res.data;
}

// ============================================================
// SESSIONS
// ============================================================
export async function apiListSessions(): Promise<ChatSession[]> {
  const res = await api.get<ChatSession[]>('/api/sessions');
  return res.data;
}

export async function apiCreateSession(title: string): Promise<ChatSession> {
  const res = await api.post<ChatSession>('/api/sessions', { title });
  return res.data;
}

export async function apiGetSession(sessionId: string): Promise<ChatSessionDetail> {
  const res = await api.get<ChatSessionDetail>(`/api/sessions/${sessionId}`);
  return res.data;
}

export async function apiDeleteSession(sessionId: string): Promise<void> {
  await api.delete(`/api/sessions/${sessionId}`);
}

// ============================================================
// DOCUMENTS
// ============================================================
export interface DocumentInfo {
  id: string;
  name: string;
  author: string;
  year: number;
  date: string;
  size: string;
  size_bytes?: number;
  status: 'done' | 'indexing' | 'pending';
}

export async function apiListDocuments(): Promise<DocumentInfo[]> {
  const res = await api.get<DocumentInfo[]>('/api/documents');
  return res.data;
}

export async function apiUploadDocument(file: File, domain: string): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('domain', domain);
  const res = await api.post('/api/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

export async function apiDeleteDocumentsBulk(ids: string[]): Promise<any> {
  const res = await api.delete('/api/documents/bulk', {
    data: { ids },
  });
  return res.data;
}

export async function apiReassignDocument(id: string, targetDomain: string): Promise<any> {
  const res = await api.post('/api/documents/reassign', { id, target_domain: targetDomain });
  return res.data;
}

// ============================================================
// WEBSOCKET HELPERS
// ============================================================
export function buildWsUrl(sessionId: string): string {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : '';
  const wsBase = BASE_URL.replace(/^http/, 'ws');
  return `${wsBase}/api/ws/chat/${sessionId}?token=${token}`;
}

// ============================================================
// CHAT EXPORTS  (sync with Library / Academic dashboards)
// ============================================================
export interface ChatExport {
  message_id: string;
  session_id: string;
  session_title: string;
  question_preview: string;
  export_links: { docs?: string; sheets?: string };
  created_at: string;
}

export async function apiListChatExports(): Promise<ChatExport[]> {
  const res = await api.get<ChatExport[]>('/api/chat-exports');
  return res.data;
}

export default api;
