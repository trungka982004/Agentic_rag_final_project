'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useState, useCallback, useEffect } from 'react';
import type { ChatSession, User } from '@/types';
import { apiCreateSession, apiDeleteSession, apiListDocuments, apiUploadDocument, type DocumentInfo } from '@/services/api';
import { formatRelativeTime } from '@/lib/utils';

/* ─── Icon primitives ─────────────────────────────────────── */
const Icon = ({ path, size = 16 }: { path: string; size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d={path} />
  </svg>
);

const ICONS = {
  brain: 'M9.5 2a6 6 0 0 1 5.5 8.5M9.5 2A6 6 0 0 0 4 8.5c0 3.1 2 5.7 4.8 6.5M9.5 2v3M15 10.5A6 6 0 0 1 9.5 17M15 10.5A6 6 0 0 0 21 8.5c0-3.3-2.7-6-6-6M15 10.5v3M9.5 17v5M9.5 17H5m4.5 5H5m9.5-7v5m0-5h4m-4 5h4',
  plus: 'M12 5v14M5 12h14',
  chat: 'M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z',
  trash: 'M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2',
  logout: 'M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9',
  user: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8',
  settings: 'M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2zM12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
  ellipsis: 'M12 5h.01M12 12h.01M12 19h.01',
  library: 'M3 3h4v18H3zM9 3h4v18H9zM15 3l4 1-1 17-4-1',
  school: 'M22 10v6M2 10l10-5 10 5-10 5z M6 12v5c3 3 9 3 12 0v-5',
  bookmark: 'M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z',
  quote: 'M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1zM15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z',
  config: 'M4 6h16M4 12h16M4 18h7',
  support: 'M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3M12 17h.01',
  zap: 'M13 2L3 14h9l-1 8 10-12h-9l1-8z',
};

interface Props {
  sessions: ChatSession[];
  user: User | null;
  onLogout: () => void;
  onSessionCreated: (session: ChatSession) => void;
  onSessionDeleted: (id: string) => void;
  isLoading?: boolean;
}

export default function Sidebar({
  sessions,
  user,
  onLogout,
  onSessionCreated,
  onSessionDeleted,
  isLoading,
}: Props) {
  const pathname = usePathname();
  const router = useRouter();
  const [creating, setCreating] = useState(false);
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [selectedDomain, setSelectedDomain] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('active_domain') || 'it';
    }
    return 'it';
  });
  const [customDomains, setCustomDomains] = useState<{ id: string; label: string }[]>([]);
  const [uploading, setUploading] = useState(false);
  const [showAllChats, setShowAllChats] = useState(false);

  // Sync selectedDomain to localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('active_domain', selectedDomain);
    }
  }, [selectedDomain]);

  // Load custom domains from localStorage initially
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('custom_domains');
      if (saved) {
        setCustomDomains(JSON.parse(saved));
      }
    }
  }, []);

  const fetchDocs = useCallback(async () => {
    try {
      const data = await apiListDocuments();
      setDocuments(data);

      // Auto-discover domains present in documents but missing from categories
      const defaults = ['it', 'math', 'physics', 'electronics'];
      const detectedCustoms: { id: string; label: string }[] = [];
      data.forEach(doc => {
        const domainId = doc.author.toLowerCase();
        const isDefault = defaults.includes(domainId);
        if (!isDefault && !detectedCustoms.some(d => d.id === domainId)) {
          const rawLabel = doc.author;
          let label = rawLabel.charAt(0) + rawLabel.slice(1).toLowerCase();
          label = label.replace(/_/g, ' ');
          detectedCustoms.push({
            id: domainId,
            label,
          });
        }
      });

      if (detectedCustoms.length > 0) {
        setCustomDomains(prev => {
          const combined = [...prev];
          detectedCustoms.forEach(dc => {
            if (!combined.some(c => c.id === dc.id)) {
              combined.push(dc);
            }
          });
          if (typeof window !== 'undefined') {
            localStorage.setItem('custom_domains', JSON.stringify(combined));
          }
          return combined;
        });
      }
    } catch (e) {
      console.error(e);
    }
  }, []);

  useEffect(() => {
    fetchDocs();
    window.addEventListener('document-uploaded', fetchDocs);
    return () => {
      window.removeEventListener('document-uploaded', fetchDocs);
    };
  }, [fetchDocs]);

  const handleNewSession = useCallback(async () => {
    if (creating) return;
    setCreating(true);
    try {
      const session = await apiCreateSession('New Conversation');
      onSessionCreated(session);
      router.push(`/chat/${session.id}`);
    } catch (e) {
      console.error(e);
    } finally {
      setCreating(false);
    }
  }, [creating, onSessionCreated, router]);

  const handleDelete = useCallback(async (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      await apiDeleteSession(id);
      onSessionDeleted(id);
      if (pathname.includes(id)) router.push('/chat');
    } catch (e) {
      console.error(e);
    }
  }, [onSessionDeleted, pathname, router]);

  const currentSessionId = pathname.split('/chat/')[1];

  const filteredDocs = documents.filter(
    (doc) => doc.author.toLowerCase() === selectedDomain.toLowerCase()
  );

  return (
    <aside style={{
      width: 'var(--sidebar-width)',
      minWidth: 'var(--sidebar-width)',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: 'var(--surface-container-low)',
      borderRight: '1px solid var(--outline-variant)',
      overflow: 'hidden',
    }}>

      {/* ─── Logo / Brand header ─── */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        padding: '14px 16px',
        borderBottom: '1px solid var(--outline-variant)',
        flexShrink: 0,
      }}>
        <div style={{
          width: '32px', height: '32px',
          background: 'var(--primary-container)',
          borderRadius: 'var(--radius-sm)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexShrink: 0,
        }}>
          <Icon path={ICONS.brain} size={16} />
        </div>
        <div style={{ overflow: 'hidden' }}>
          <div style={{
            fontFamily: 'var(--font-display)',
            fontSize: '13px', fontWeight: 700,
            color: 'var(--on-surface)',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}>
            Intelligent Research Agent
          </div>
          <div style={{ fontSize: '11px', color: 'var(--on-surface-variant)' }}>
            {user?.email ? (
              <span>{user.email.split('@')[0]}</span>
            ) : 'Scholar Intelligence System'}
          </div>
        </div>
      </div>

      {/* ─── Scrollable nav body ─── */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '8px' }}>

        {/* New Chat button */}
        <button
          id="new-chat-btn"
          onClick={handleNewSession}
          disabled={creating}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            width: '100%',
            padding: '8px 12px',
            marginBottom: '8px',
            background: 'var(--primary-container)',
            color: 'var(--on-primary)',
            border: 'none',
            borderRadius: 'var(--radius-sm)',
            fontFamily: 'var(--font-label)',
            fontSize: '13.5px',
            fontWeight: 600,
            cursor: creating ? 'not-allowed' : 'pointer',
            opacity: creating ? 0.7 : 1,
            transition: 'background 0.15s',
          }}
          onMouseEnter={e => !creating && ((e.currentTarget as HTMLElement).style.background = 'var(--primary)')}
          onMouseLeave={e => ((e.currentTarget as HTMLElement).style.background = 'var(--primary-container)')}
        >
          {creating ? (
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
              strokeWidth="2" style={{ animation: 'spin 1s linear infinite' }}>
              <path d="M21 12a9 9 0 1 1-6.219-8.56" />
            </svg>
          ) : (
            <Icon path={ICONS.plus} size={15} />
          )}
          New Conversation
        </button>

        {/* ─── SECTION: Add Research Document (Ingestion Widget) ─── */}
        <div style={{
          padding: '4px',
          borderBottom: '1px solid var(--outline-variant)',
          marginBottom: '12px'
        }}>
          <div className="sidebar-section-label" style={{ marginBottom: '6px' }}>
            Add Research Document
          </div>
          <div style={{
            border: '1.5px dashed rgba(0, 85, 212, 0.4)',
            borderRadius: 'var(--radius-sm)',
            padding: '16px 8px',
            fontSize: '11px',
            color: uploading ? 'var(--warning)' : 'var(--on-surface-variant)',
            background: 'var(--surface-container-lowest)',
            cursor: uploading ? 'not-allowed' : 'pointer',
            transition: 'background 0.15s, border-color 0.15s',
            opacity: uploading ? 0.7 : 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
          }}
            onMouseEnter={e => {
              if (!uploading) {
                e.currentTarget.style.background = 'var(--surface-container-high)';
                e.currentTarget.style.borderColor = 'var(--primary)';
              }
            }}
            onMouseLeave={e => {
              if (!uploading) {
                e.currentTarget.style.background = 'var(--surface-container-lowest)';
                e.currentTarget.style.borderColor = 'rgba(0, 85, 212, 0.4)';
              }
            }}
            onClick={() => {
              if (!uploading) {
                document.getElementById('sidebar-file-upload')?.click();
              }
            }}
          >
            {uploading ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', padding: '12px 0' }}>
                <div style={{ display: 'inline-block', width: '16px', height: '16px', border: '2px solid var(--warning)', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                <div style={{ fontWeight: 500 }}>Uploading...</div>
              </div>
            ) : (
              <>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ color: 'var(--primary)', flexShrink: 0 }}>
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <div style={{
                  background: 'var(--primary-container)',
                  color: 'var(--on-primary)',
                  padding: '5px 18px',
                  borderRadius: '99px',
                  fontSize: '11.5px',
                  fontWeight: 600,
                  boxShadow: 'var(--shadow-1)',
                  marginTop: '2px',
                }}>
                  Browse
                </div>
                <div style={{ color: 'var(--on-surface-variant)', fontSize: '10.5px', opacity: 0.8 }}>
                  or drag &amp; drop files here
                </div>
                <div style={{ color: 'var(--error)', fontSize: '9px', fontWeight: 500, marginTop: '2px' }}>
                  *Supports .pdf format
                </div>
              </>
            )}
            <input
              id="sidebar-file-upload"
              type="file"
              multiple
              accept=".pdf"
              style={{ display: 'none' }}
              disabled={uploading}
              onChange={async (e) => {
                const files = e.target.files;
                if (!files || files.length === 0) return;
                setUploading(true);
                try {
                  for (let i = 0; i < files.length; i++) {
                    await apiUploadDocument(files[i], selectedDomain);
                  }
                  alert('Upload successful! The AI is analyzing the document in the background.');
                  fetchDocs();
                } catch (err) {
                  console.error(err);
                  alert('Document upload failed.');
                } finally {
                  setUploading(false);
                }
              }}
            />
          </div>
        </div>

        {/* ─── SECTION: Scientific Library (PDF files) ─── */}
        <div className="sidebar-section-label" style={{ marginTop: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>SCIENTIFIC LIBRARY</span>
          <select
            value={selectedDomain}
            onChange={async (e) => {
              const val = e.target.value;
              setSelectedDomain(val);
              await fetchDocs();
            }}
            onClick={e => e.stopPropagation()}
            style={{
              fontSize: '11px',
              padding: '2px 4px',
              borderRadius: '3px',
              border: '1px solid var(--outline-variant)',
              background: 'var(--surface-container-low)',
              color: 'var(--on-surface)',
              outline: 'none',
              cursor: 'pointer',
              maxWidth: '120px',
            }}
          >
            <option value="it">Computer Science</option>
            <option value="math">Mathematics</option>
            <option value="physics">Physics</option>
            <option value="electronics">Electronics</option>
            {customDomains.map(d => (
              <option key={d.id} value={d.id}>{d.label}</option>
            ))}
          </select>
        </div>

        {filteredDocs.length === 0 ? (
          <div style={{
            padding: '10px',
            fontSize: '12px',
            color: 'var(--on-surface-variant)',
            textAlign: 'center',
          }}>
            No documents yet.
          </div>
        ) : (
          <div style={{ marginBottom: '12px' }}>
            {filteredDocs.slice(0, 5).map(doc => (
              <div
                key={doc.id}
                draggable={doc.status === 'done'}
                onDragStart={(e) => {
                  e.dataTransfer.setData('text/plain', doc.name);
                  e.dataTransfer.effectAllowed = 'copy';
                }}
                onClick={() => {
                  if (doc.status === 'done') {
                    window.dispatchEvent(new CustomEvent('attach-document-to-chat', { detail: { name: doc.name } }));
                  } else {
                    alert('Document is currently indexing, please wait.');
                  }
                }}
                title={doc.status === 'done' ? "Drag and drop to Chat or click to attach" : "Processing document..."}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '6px 8px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '12.5px',
                  color: 'var(--on-surface)',
                  fontFamily: 'var(--font-body)',
                  marginBottom: '2px',
                  transition: 'background 0.1s, border-color 0.1s',
                  background: 'var(--surface-container-lowest)',
                  border: '1px solid var(--outline-variant)',
                  cursor: doc.status === 'done' ? 'grab' : 'wait',
                  userSelect: 'none',
                }}
                className="sidebar-bookcase-item"
              >
                <div style={{
                  width: '20px', height: '20px',
                  background: 'var(--error-container)',
                  borderRadius: '3px',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '8px', fontWeight: 700,
                  color: 'var(--error)',
                  flexShrink: 0,
                }}>PDF</div>
                <div style={{ flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {doc.name}
                </div>
                <span style={{
                  fontSize: '9.5px',
                  padding: '1px 4px',
                  background: doc.status === 'done' ? 'var(--success-container)' : 'var(--warning-container)',
                  color: doc.status === 'done' ? 'var(--success)' : 'var(--warning)',
                  borderRadius: '3px',
                  fontWeight: 600,
                  flexShrink: 0,
                }}>
                  {doc.status === 'done' ? 'AI' : '...'}
                </span>
              </div>
            ))}
            {filteredDocs.length > 5 && (
              <Link
                href="/settings/library"
                style={{
                  display: 'block',
                  width: '100%',
                  padding: '4px',
                  fontSize: '11.5px',
                  color: 'var(--primary)',
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  textAlign: 'center',
                  fontWeight: 600,
                  fontFamily: 'var(--font-label)',
                  textDecoration: 'none',
                }}
              >
                View more ({filteredDocs.length - 5}) ▼
              </Link>
            )}
          </div>
        )}

        {/* ─── SECTION: Chat History ─── */}
        <div className="sidebar-section-label" style={{ marginTop: '16px' }}>CHAT HISTORY</div>

        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="skeleton" style={{ height: '34px', margin: '4px 4px' }} />
          ))
        ) : sessions.length === 0 ? (
          <div style={{
            padding: '12px',
            fontSize: '12.5px',
            color: 'var(--on-surface-variant)',
            textAlign: 'center',
          }}>
            No conversations yet.
          </div>
        ) : (
          <div>
            {(showAllChats ? sessions : sessions.slice(0, 5)).map(session => {
              const active = session.id === currentSessionId;
              return (
                <div
                  key={session.id}
                  onMouseEnter={() => setHoveredId(session.id)}
                  onMouseLeave={() => setHoveredId(null)}
                  style={{ position: 'relative' }}
                >
                  <Link
                    href={`/chat/${session.id}`}
                    className={`sidebar-nav-item ${active ? 'sidebar-nav-item--active' : ''}`}
                    style={{ paddingRight: '28px' }}
                  >
                    <Icon path={ICONS.chat} size={14} />
                    <div style={{ overflow: 'hidden', flex: 1 }}>
                      <div style={{
                        fontWeight: active ? 600 : 400,
                        fontSize: '13px',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}>
                        {session.title || 'New Conversation'}
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--on-surface-variant)', opacity: 0.8 }}>
                        {formatRelativeTime(session.updated_at)}
                      </div>
                    </div>
                  </Link>

                  {(hoveredId === session.id || active) && (
                    <button
                      onClick={e => handleDelete(e, session.id)}
                      className="btn-icon"
                      title="Delete conversation"
                      style={{
                        position: 'absolute',
                        right: '4px', top: '50%',
                        transform: 'translateY(-50%)',
                        width: '24px', height: '24px',
                        color: 'var(--error)',
                      }}
                    >
                      <Icon path={ICONS.trash} size={13} />
                    </button>
                  )}
                </div>
              );
            })}
            {sessions.length > 5 && (
              <button
                onClick={() => setShowAllChats(prev => !prev)}
                style={{
                  width: '100%',
                  padding: '4px',
                  fontSize: '11.5px',
                  color: 'var(--primary)',
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  textAlign: 'center',
                  fontWeight: 600,
                  fontFamily: 'var(--font-label)',
                }}
              >
                {showAllChats ? 'Collapse ▲' : `View more (${sessions.length - 5}) ▼`}
              </button>
            )}
          </div>
        )}
      </div>

      {/* ─── Footer: user info + Upgrade + Logout ─── */}
      <div style={{
        flexShrink: 0,
        borderTop: '1px solid var(--outline-variant)',
        padding: '10px 8px',
      }}>
        {/* Upgrade Pro button */}
        <button className="upgrade-btn" style={{ marginBottom: '8px' }}>
          <Icon path={ICONS.zap} size={14} />
          Upgrade Pro
        </button>

        {/* User row + logout */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 8px',
          borderRadius: 'var(--radius-sm)',
          cursor: 'default',
        }}>
          <div style={{
            width: '28px', height: '28px', borderRadius: '50%',
            background: 'var(--primary-container)',
            color: 'var(--on-primary)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '12px', fontWeight: 700, flexShrink: 0,
          }}>
            {user?.email?.[0]?.toUpperCase() ?? 'U'}
          </div>
          <div style={{ flex: 1, overflow: 'hidden' }}>
            <div style={{
              fontSize: '12.5px', fontWeight: 500,
              whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
              color: 'var(--on-surface)',
            }}>
              {user?.email ?? '—'}
            </div>
          </div>
          <button
            id="logout-btn"
            onClick={onLogout}
            className="btn-icon"
            title="Logout"
            style={{ flexShrink: 0 }}
          >
            <Icon path={ICONS.logout} size={15} />
          </button>
        </div>
      </div>
    </aside>
  );
}
