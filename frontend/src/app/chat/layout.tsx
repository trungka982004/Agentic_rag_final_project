'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { apiListSessions, apiCreateSession } from '@/services/api';
import type { ChatSession } from '@/types';
import Sidebar from '@/components/Sidebar';
import TopBar from '@/components/TopBar';

export default function ChatLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [sessionsLoading, setSessionsLoading] = useState(true);

  // Auth guard
  useEffect(() => {
    if (!loading && !user) router.replace('/login');
  }, [loading, user, router]);

  const fetchSessions = useCallback(async () => {
    if (!user) return;
    try {
      const data = await apiListSessions();
      setSessions(data);
    } catch { /* interceptor handles 401 */ }
    finally { setSessionsLoading(false); }
  }, [user]);

  useEffect(() => { fetchSessions(); }, [fetchSessions]);

  const handleSessionCreated = useCallback((s: ChatSession) => setSessions(p => [s, ...p]), []);
  const handleSessionDeleted = useCallback((id: string) => setSessions(p => p.filter(s => s.id !== id)), []);

  if (loading || !user) {
    return (
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        height: '100vh', background: 'var(--surface)',
        gap: '10px', color: 'var(--on-surface-variant)', fontSize: '14px',
      }}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          strokeWidth="2" style={{ animation: 'spin 1s linear infinite' }}>
          <path d="M21 12a9 9 0 1 1-6.219-8.56" />
        </svg>
        Đang tải...
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      <Sidebar
        sessions={sessions}
        user={user}
        onLogout={logout}
        onSessionCreated={handleSessionCreated}
        onSessionDeleted={handleSessionDeleted}
        isLoading={sessionsLoading}
      />
      <main style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        <TopBar user={user} isConnected={true} />
        {children}
      </main>
    </div>
  );
}
