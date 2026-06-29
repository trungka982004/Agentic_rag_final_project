'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { buildWsUrl } from '@/services/api';
import type { WSEvent, ActiveNode, ExportLink, DisplayMessage } from '@/types';

export type ChatSendFn = (question: string) => void;

export function useWebSocket(sessionId: string | null) {
  const ws = useRef<WebSocket | null>(null);
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isThinking, setIsThinking] = useState(false);

  // Streaming accumulator refs
  const streamContentRef = useRef('');
  const streamNodesRef   = useRef<ActiveNode[]>([]);
  const streamLinksRef   = useRef<ExportLink[]>([]);

  const resetStream = () => {
    streamContentRef.current = '';
    streamNodesRef.current   = [];
    streamLinksRef.current   = [];
  };

  // Patch the last streaming message in state
  const patchStreaming = useCallback((
    content: string,
    nodes: ActiveNode[],
    links: ExportLink[],
    done = false
  ) => {
    setMessages(prev => {
      const copy = [...prev];
      const last = copy[copy.length - 1];
      if (last && 'isStreaming' in last && last.isStreaming) {
        copy[copy.length - 1] = {
          ...last,
          content,
          activeNodes: nodes,
          exportLinks: links,
          isStreaming: !done,
        } as DisplayMessage;
      }
      return copy;
    });
  }, []);

  const handleEvent = useCallback((raw: string) => {
    let event: WSEvent;
    try { event = JSON.parse(raw); } catch { return; }

    switch (event.type) {
      case 'status':
        // optional: show status banner — ignore silently
        break;

      case 'node_update': {
        const nodeName = event.node ?? '';
        streamNodesRef.current = [
          ...streamNodesRef.current.filter(n => n.name !== nodeName),
          { name: nodeName, status: 'running' }
        ];
        patchStreaming(streamContentRef.current, [...streamNodesRef.current], [...streamLinksRef.current]);
        break;
      }

      case 'token': {
        streamContentRef.current += event.content ?? '';
        patchStreaming(streamContentRef.current, [...streamNodesRef.current], [...streamLinksRef.current]);
        break;
      }

      case 'export_link': {
        const link: ExportLink = {
          type: (event.link_type ?? 'google_docs') as ExportLink['type'],
          url: event.url ?? '',
          title: event.link_title ?? '',
        };
        streamLinksRef.current = [...streamLinksRef.current, link];
        patchStreaming(streamContentRef.current, [...streamNodesRef.current], [...streamLinksRef.current]);
        break;
      }

      case 'final_answer': {
        const finalContent = event.content ?? streamContentRef.current;
        let finalLinks = [...streamLinksRef.current];
        const rawLinks = (event as any).export_links;
        if (rawLinks) {
          if (typeof rawLinks === 'object' && !Array.isArray(rawLinks)) {
            const list: ExportLink[] = [];
            if (rawLinks.docs || rawLinks.google_docs) {
              list.push({
                type: 'google_docs',
                url: rawLinks.docs || rawLinks.google_docs,
                title: 'Mở trong Google Docs',
              });
            }
            if (rawLinks.sheets || rawLinks.google_sheets) {
              list.push({
                type: 'google_sheets',
                url: rawLinks.sheets || rawLinks.google_sheets,
                title: 'Mở trong Google Sheets',
              });
            }
            finalLinks = list;
          }
        }
        patchStreaming(finalContent, [...streamNodesRef.current], finalLinks, true);
        setIsThinking(false);
        resetStream();
        break;
      }

      case 'error': {
        patchStreaming(`❌ **Lỗi:** ${event.message ?? 'Unknown error'}`, [], [], true);
        setIsThinking(false);
        resetStream();
        break;
      }
    }
  }, [patchStreaming]);

  // Connect / reconnect when sessionId changes
  useEffect(() => {
    if (!sessionId) return;

    const url = buildWsUrl(sessionId);
    const socket = new WebSocket(url);
    ws.current = socket;

    socket.onopen = () => setIsConnected(true);
    socket.onclose = () => setIsConnected(false);
    socket.onerror = () => setIsConnected(false);
    socket.onmessage = (e) => handleEvent(e.data);

    return () => {
      socket.close();
      ws.current = null;
      setIsConnected(false);
    };
  }, [sessionId, handleEvent]);

  const sendMessage = useCallback((question: string) => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) return;

    // Append user bubble
    const userMsg: DisplayMessage = {
      id: crypto.randomUUID(),
      session_id: sessionId ?? '',
      role: 'user',
      content: question,
      created_at: new Date().toISOString(),
    };

    // Append empty streaming agent bubble
    const agentMsg: DisplayMessage = {
      role: 'agent',
      content: '',
      activeNodes: [],
      exportLinks: [],
      isStreaming: true,
    };

    setMessages(prev => [...prev, userMsg, agentMsg]);
    setIsThinking(true);
    resetStream();

    ws.current.send(JSON.stringify({ question }));
  }, [sessionId]);

  const loadHistory = useCallback((history: DisplayMessage[]) => {
    setMessages(history);
  }, []);

  return { messages, isConnected, isThinking, sendMessage, loadHistory };
}
