'use client';

import { useEffect, useRef, useState, useCallback, KeyboardEvent } from 'react';
import type { DisplayMessage, User, ExportLink } from '@/types';
import MessageBubble from './MessageBubble';
import AgentThoughtBar from './AgentThoughtBar';
import ScientificConsole from './ScientificConsole';

const Icon = ({ path, size = 16 }: { path: string; size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d={path} />
  </svg>
);
const ICONS = {
  send: 'M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z',
  brain: 'M9.5 2a6 6 0 0 1 5.5 8.5M9.5 2A6 6 0 0 0 4 8.5c0 3.1 2 5.7 4.8 6.5M9.5 2v3M15 10.5A6 6 0 0 1 9.5 17M15 10.5A6 6 0 0 0 21 8.5c0-3.3-2.7-6-6-6M15 10.5v3M9.5 17v5M9.5 17H5m4.5 5H5m9.5-7v5m0-5h4m-4 5h4',
};

const SUGGESTIONS = [
  { icon: '📚', text: 'Giải thích thuật toán quicksort' },
  { icon: '🌐', text: 'So sánh TCP và UDP' },
  { icon: '🐍', text: 'Vẽ sơ đồ kiến trúc microservices bằng Mermaid' },
  { icon: '∫', text: 'Giải phương trình vi phân $\\frac{dy}{dx} = 2x$' },
];

interface Props {
  messages: DisplayMessage[];
  isConnected: boolean;
  isThinking: boolean;
  onSend: (text: string) => void;
  user: User | null;
  sessionTitle?: string;
}

export default function ChatWindow({
  messages,
  isConnected,
  isThinking,
  onSend,
  user,
  sessionTitle,
}: Props) {
  const [input, setInput] = useState('');
  const [selectedMessageId, setSelectedMessageId] = useState<string | null>(null);
  const [localMessages, setLocalMessages] = useState<DisplayMessage[]>([]);

  useEffect(() => {
    setLocalMessages(messages);
  }, [messages]);

  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  /* Auto-scroll */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isThinking]);

  /* Auto-resize textarea */
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 160) + 'px';
  }, [input]);

  const handleSend = useCallback(() => {
    const text = input.trim();
    if (!text || isThinking || !isConnected) return;
    onSend(text);
    setInput('');
  }, [input, isThinking, isConnected, onSend]);

  const handleKey = useCallback((e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  const handleUpdateMessageLinks = useCallback((msgId: string, links: ExportLink[]) => {
    setLocalMessages(prev => prev.map(m => {
      if (m.id === msgId) {
        return {
          ...m,
          export_links: links,
          exportLinks: links,
        };
      }
      return m;
    }));
  }, []);

  const agentMessages = localMessages.filter(m => m.role === 'agent');
  const lastAgentMessage = agentMessages[agentMessages.length - 1] || null;
  const selectedMessage = selectedMessageId 
    ? localMessages.find(m => m.id === selectedMessageId) || null
    : lastAgentMessage;

  const isEmpty = localMessages.length === 0;

  return (
    <div style={{
      display: 'flex',
      height: '100%',
      width: '100%',
      background: 'var(--surface)',
      overflow: 'hidden',
    }}>
      {/* Center Column: Chat View */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        minWidth: 0,
        overflow: 'hidden',
      }}>
        {/* ─── Message list ─── */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: isEmpty ? '0' : '20px 24px',
        }}>
          {isEmpty ? (
            /* ─── Empty state ─── */
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              textAlign: 'center',
              padding: '40px 24px',
              gap: '24px',
            }}>
            <div style={{
              width: '72px', height: '72px',
              background: 'var(--primary-fixed)',
              border: '1px solid var(--primary-fixed-dim)',
              borderRadius: 'var(--radius-xl)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--primary-container)',
            }}>
              <Icon path={ICONS.brain} size={32} />
            </div>
            <div>
              <h2 style={{
                fontFamily: 'var(--font-display)',
                fontSize: '20px',
                fontWeight: 700,
                color: 'var(--on-surface)',
                marginBottom: '8px',
              }}>
                Agentic RAG Research Assistant
              </h2>
              <p style={{
                color: 'var(--on-surface-variant)',
                fontSize: '14px',
                maxWidth: '400px',
                lineHeight: '1.6',
              }}>
                Đặt câu hỏi về IT, Toán, Vật lý hay Điện tử
              </p>
            </div>

            {/* Suggestion chips — Stitch "quick prompt" style */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '10px',
              maxWidth: '500px',
              width: '100%',
            }}>
              {SUGGESTIONS.map(s => (
                <button
                  key={s.text}
                  onClick={() => { setInput(s.text); textareaRef.current?.focus(); }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '12px 14px',
                    background: 'var(--surface-container-lowest)',
                    border: '1px solid var(--outline-variant)',
                    borderRadius: 'var(--radius-md)',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'border-color 0.15s, background 0.15s',
                    fontSize: '13px',
                    color: 'var(--on-surface)',
                    fontFamily: 'var(--font-body)',
                  }}
                  onMouseEnter={e => {
                    (e.currentTarget as HTMLElement).style.borderColor = 'var(--primary-container)';
                    (e.currentTarget as HTMLElement).style.background = 'var(--primary-fixed)';
                  }}
                  onMouseLeave={e => {
                    (e.currentTarget as HTMLElement).style.borderColor = 'var(--outline-variant)';
                    (e.currentTarget as HTMLElement).style.background = 'var(--surface-container-lowest)';
                  }}
                >
                  <span style={{ fontSize: '18px', flexShrink: 0 }}>{s.icon}</span>
                  <span style={{ lineHeight: '1.4' }}>{s.text}</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* ─── Message list ─── */
          <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {localMessages.map((msg, i) => (
              <div key={msg.id ?? i} className="animate-fade-up">
                {msg.isStreaming && msg.activeNodes && msg.activeNodes.length > 0 && (
                  <AgentThoughtBar nodes={msg.activeNodes} isStreaming={msg.isStreaming} />
                )}
                <MessageBubble 
                  message={msg} 
                  isSelected={msg.id === selectedMessage?.id}
                  onSelect={() => {
                    if (msg.role === 'agent' && msg.id) {
                      setSelectedMessageId(msg.id);
                    }
                  }}
                />
              </div>
            ))}

            {/* Typing indicator */}
            {isThinking && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 0',
              }}>
                <div style={{
                  width: '28px', height: '28px',
                  background: 'var(--primary-fixed)',
                  borderRadius: 'var(--radius-sm)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: 'var(--primary-container)',
                  flexShrink: 0,
                }}>
                  <Icon path={ICONS.brain} size={14} />
                </div>
                <div style={{
                  background: 'var(--surface-container-lowest)',
                  border: '1px solid var(--outline-variant)',
                  borderRadius: 'var(--radius-md)',
                  padding: '10px 14px',
                  display: 'flex',
                  gap: '4px',
                  alignItems: 'center',
                }}>
                  {[0, 1, 2].map(i => (
                    <span key={i} className="typing-dot"
                      style={{ animationDelay: `${i * 0.2}s` }} />
                  ))}
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* ─── Input bar — matches Stitch style ─── */}
      <div style={{
        flexShrink: 0,
        padding: '12px 24px 16px',
        background: 'var(--surface)',
        borderTop: isEmpty ? 'none' : '1px solid var(--surface-container-high)',
        maxWidth: isEmpty ? '600px' : '100%',
        margin: isEmpty ? '0 auto' : undefined,
        width: '100%',
        boxSizing: 'border-box',
      }}>
        <div className="chat-input-bar" style={{
          display: 'flex',
          alignItems: 'flex-end',
          gap: '8px',
          padding: '10px 12px 10px 16px',
        }}>
          <textarea
            id="chat-input"
            ref={textareaRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Nhập câu hỏi... (Enter để gửi, Shift+Enter xuống dòng)"
            rows={1}
            disabled={!isConnected}
            style={{
              flex: 1,
              resize: 'none',
              border: 'none',
              outline: 'none',
              background: 'transparent',
              font: 'inherit',
              fontSize: '14px',
              lineHeight: '1.6',
              color: 'var(--on-surface)',
              minHeight: '24px',
              maxHeight: '160px',
              overflowY: 'auto',
            }}
          />
          <button
            id="chat-send-btn"
            onClick={handleSend}
            disabled={!input.trim() || isThinking || !isConnected}
            style={{
              width: '34px', height: '34px',
              borderRadius: 'var(--radius-sm)',
              background: input.trim() && !isThinking && isConnected
                ? 'var(--primary-container)' : 'var(--surface-container-high)',
              color: input.trim() && !isThinking && isConnected
                ? 'var(--on-primary)' : 'var(--on-surface-variant)',
              border: 'none',
              cursor: input.trim() && !isThinking && isConnected ? 'pointer' : 'default',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0,
              transition: 'background 0.15s',
            }}
          >
            <Icon path={ICONS.send} size={16} />
          </button>
        </div>

        {/* Hint */}
        {!isConnected && (
          <p style={{
            textAlign: 'center',
            fontSize: '12px',
            color: 'var(--error)',
            marginTop: '6px',
          }}>
            Hệ thống có thể mắc sai lầm. Hãy kiểm chứng thông tin quan trọng.
          </p>
        )}
      </div>
    </div>

    {/* Right Column: Scientific Console */}
    <div style={{
      width: '380px',
      minWidth: '380px',
      height: '100%',
      flexShrink: 0,
    }}>
      <ScientificConsole
        selectedMessage={selectedMessage}
        onUpdateMessageLinks={handleUpdateMessageLinks}
      />
    </div>
  </div>
  );
}
