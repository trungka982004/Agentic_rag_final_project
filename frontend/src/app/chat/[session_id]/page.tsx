'use client';

import { useEffect, use } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useAuth } from '@/hooks/useAuth';
import { apiGetSession } from '@/services/api';
import ChatWindow from '@/components/ChatWindow';
import type { Message } from '@/types';

interface PageProps {
  params: Promise<{ session_id: string }>;
}

export default function SessionPage({ params }: PageProps) {
  const { session_id } = use(params);
  const { user } = useAuth();

  const {
    messages,
    isConnected,
    isThinking,
    sendMessage,
    loadHistory,
  } = useWebSocket(session_id);

  // Load historical messages when switching sessions
  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const session = await apiGetSession(session_id);
        if (!cancelled && session.messages) {
          const history = session.messages.map((m: Message) => ({
            ...m,
            isStreaming: false as const,
          }));
          loadHistory(history);
        }
      } catch {
        // session may not exist yet — OK
      }
    }
    load();
    return () => { cancelled = true; };
  }, [session_id, loadHistory]);

  return (
    <ChatWindow
      messages={messages}
      isConnected={isConnected}
      isThinking={isThinking}
      onSend={sendMessage}
      user={user}
      sessionTitle={undefined}
    />
  );
}
