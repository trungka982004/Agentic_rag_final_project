'use client';

import { useState, useEffect, useCallback } from 'react';
import type { DisplayMessage, ExportLink } from '@/types';
import dynamic from 'next/dynamic';
import api from '@/services/api';
import { normalizeExportLinks } from './MessageBubble';

const MermaidRenderer = dynamic(() => import('./MermaidRenderer'), { ssr: false });

interface Props {
  selectedMessage: DisplayMessage | null;
  onUpdateMessageLinks: (messageId: string, links: ExportLink[]) => void;
  allMessages?: DisplayMessage[];   // ← NEW: all messages in the current chat session
}

const Icon = ({ path, size = 16 }: { path: string; size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d={path} />
  </svg>
);

const ICONS = {
  quote: 'M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1zM15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z',
  map: 'M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5',
  export: 'M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8M16 6l-4-4-4 4M12 2v16',
  docs: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M16 13H8M16 17H8M10 9H8',
  sheets: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M16 13H8M16 17H8M10 9H8',
  check: 'M20 6L9 17l-5-5',
  loader: 'M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83',
  info: 'M12 16v-4M12 8h.01M22 12A10 10 0 1 1 12 2a10 10 0 0 1 10 10z',
  external: 'M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3'
};

function extractMermaid(content: string): string | null {
  const m = content.match(/```mermaid\s*([\s\S]*?)\s*```/);
  return m ? m[1].trim() : null;
}
function extractAllMermaid(content: string): string[] {
  const re = /```mermaid\s*([\s\S]*?)\s*```/g;
  const out: string[] = [];
  let m: RegExpExecArray | null;
  while ((m = re.exec(content)) !== null) { const c = m[1].trim(); if (c) out.push(c); }
  return out;
}

// Detect diagram type from first keyword in mermaid code
const DIAGRAM_TYPES: Record<string, { label: string; color: string; bg: string }> = {
  graph:           { label: 'Flowchart',  color: '#1a6fcf', bg: '#dbeafe' },
  flowchart:       { label: 'Flowchart',  color: '#1a6fcf', bg: '#dbeafe' },
  sequencediagram: { label: 'Sequence',   color: '#6d28d9', bg: '#ede9fe' },
  classdiagram:    { label: 'Class',      color: '#0f766e', bg: '#ccfbf1' },
  erdiagram:       { label: 'ER',         color: '#b45309', bg: '#fef3c7' },
  gantt:           { label: 'Gantt',      color: '#be185d', bg: '#fce7f3' },
  statediagram:    { label: 'State',      color: '#15803d', bg: '#dcfce7' },
  pie:             { label: 'Pie',        color: '#c2410c', bg: '#ffedd5' },
  mindmap:         { label: 'Mind Map',   color: '#4338ca', bg: '#e0e7ff' },
  gitgraph:        { label: 'Git Graph',  color: '#374151', bg: '#f3f4f6' },
};
function getDiagramType(code: string) {
  const first = code.trim().split(/[\s\n(]/)[0].toLowerCase().replace(/-/g, '');
  return DIAGRAM_TYPES[first] ?? { label: 'Diagram', color: '#374151', bg: '#f3f4f6' };
}

interface DiagramEntry {
  code: string;
  messageId?: string;
  userQuestion: string;   // preceding user message content
  diagramType: { label: string; color: string; bg: string };
  timestamp?: string;     // from agent message
}

export default function ScientificConsole({ selectedMessage, onUpdateMessageLinks, allMessages = [] }: Props) {
  const [activeTab, setActiveTab] = useState<'citations' | 'knowledge_map' | 'export'>('citations');
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Build diagram list with context from preceding user message
  const allDiagrams: DiagramEntry[] = [];
  for (let i = 0; i < allMessages.length; i++) {
    const msg = allMessages[i];
    if (msg.role !== 'agent' || !msg.content) continue;
    const codes = extractAllMermaid(msg.content);
    if (codes.length === 0) continue;
    // look backward for the nearest user message
    let userQ = '';
    for (let j = i - 1; j >= 0; j--) {
      if (allMessages[j].role === 'user' && allMessages[j].content) {
        userQ = allMessages[j].content.trim();
        break;
      }
    }
    codes.forEach(code => allDiagrams.push({
      code,
      messageId: msg.id,
      userQuestion: userQ,
      diagramType: getDiagramType(code),
      timestamp: (msg as any).created_at,
    }));
  }

  const mmdCode = selectedMessage?.content ? extractMermaid(selectedMessage.content) : null;

  useEffect(() => {
    if (allDiagrams.length > 0) setActiveTab('knowledge_map');
    else if (!mmdCode) setActiveTab('citations');
    setExpandedIdx(null);
    setSearchQuery('');
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [allMessages.length]);

  const toggleExpand = useCallback((idx: number) => {
    setExpandedIdx(prev => prev === idx ? null : idx);
  }, []);

  const filteredDiagrams = searchQuery.trim()
    ? allDiagrams.filter(d =>
        d.userQuestion.toLowerCase().includes(searchQuery.toLowerCase()) ||
        d.diagramType.label.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : allDiagrams;

  // Only show empty-state if there is truly nothing to display
  if (!selectedMessage && allDiagrams.length === 0) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        padding: '24px',
        color: 'var(--on-surface-variant)',
        fontSize: '13px',
        textAlign: 'center',
        gap: '12px',
        borderLeft: '1px solid var(--outline-variant)',
      }}>
        <Icon path={ICONS.info} size={28} />
        <div>
          <div style={{ fontWeight: 600, color: 'var(--on-surface)', marginBottom: '4px' }}>
            Scientific Console
          </div>
          No response selected to display in-depth scientific data.
        </div>
      </div>
    );
  }

  // Parse citations (only if a message is selected)
  const citationsList: string[] = [];
  if (selectedMessage?.content) {
    const lines = selectedMessage.content.split('\n');
    lines.forEach(line => {
      if (line.startsWith('>') || line.startsWith('»')) {
        citationsList.push(line.replace(/^[>»]\s*/, '').trim());
      }
      const citationMatches = line.match(/\[\d+\]|Vaswani|Devlin|Lewis|Attention/gi);
      if (citationMatches && line.length > 20 && !line.startsWith('>') && !line.startsWith('»') && !line.includes('```')) {
        citationsList.push(line.trim());
      }
    });
  }

  const exportLinks = normalizeExportLinks(
    selectedMessage
      ? (selectedMessage.isStreaming
          ? (selectedMessage as any).exportLinks
          : (selectedMessage as any).export_links)
      : undefined
  );

  const handleExport = async () => {
    if (isExporting || !selectedMessage?.id) return;
    setIsExporting(true);
    setExportError(null);

    try {
      const res = await api.post(`/api/ws/messages/${selectedMessage.id}/export`);
      const links = normalizeExportLinks(res.data.export_links);
      onUpdateMessageLinks(selectedMessage.id, links);
      setActiveTab('export');
    } catch (err: any) {
      console.error(err);
      setExportError(err.response?.data?.detail || 'Could not export document. Please check the credentials.json configuration.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      borderLeft: '1px solid var(--outline-variant)',
      background: 'var(--surface-container-lowest)',
    }}>
      {/* Tab bar header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        padding: '12px 16px',
        borderBottom: '1px solid var(--outline-variant)',
        gap: '6px',
      }}>
        <button
          onClick={() => setActiveTab('citations')}
          style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            padding: '8px',
            borderRadius: 'var(--radius-sm)',
            border: 'none',
            background: activeTab === 'citations' ? 'var(--primary-container)' : 'transparent',
            color: activeTab === 'citations' ? 'var(--on-primary-container)' : 'var(--on-surface-variant)',
            fontSize: '12px',
            fontWeight: 600,
            fontFamily: 'var(--font-label)',
            cursor: 'pointer',
            transition: 'background 0.15s, color 0.15s',
          }}
        >
          <Icon path={ICONS.quote} size={13} />
          Citations ({citationsList.length})
        </button>

        <button
          onClick={() => setActiveTab('knowledge_map')}
          style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            padding: '8px',
            borderRadius: 'var(--radius-sm)',
            border: 'none',
            background: activeTab === 'knowledge_map' ? 'var(--primary-container)' : 'transparent',
            color: activeTab === 'knowledge_map' ? 'var(--on-primary-container)' : 'var(--on-surface-variant)',
            fontSize: '12px',
            fontWeight: 600,
            fontFamily: 'var(--font-label)',
            cursor: 'pointer',
            transition: 'background 0.15s, color 0.15s',
          }}
        >
          <Icon path={ICONS.map} size={13} />
          Maps {allDiagrams.length > 0 ? `(${allDiagrams.length})` : ''}
        </button>

        <button
          onClick={() => setActiveTab('export')}
          style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            padding: '8px',
            borderRadius: 'var(--radius-sm)',
            border: 'none',
            background: activeTab === 'export' ? 'var(--primary-container)' : 'transparent',
            color: activeTab === 'export' ? 'var(--on-primary-container)' : 'var(--on-surface-variant)',
            fontSize: '12px',
            fontWeight: 600,
            fontFamily: 'var(--font-label)',
            cursor: 'pointer',
            transition: 'background 0.15s, color 0.15s',
          }}
        >
          <Icon path={ICONS.export} size={13} />
          Publish {exportLinks.length > 0 ? '✓' : ''}
        </button>
      </div>

      {/* Tab content body */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
        {activeTab === 'citations' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--on-surface)', fontFamily: 'var(--font-display)' }}>
              Original Citations &amp; Document Sources
            </h4>
            {citationsList.length === 0 ? (
              <p style={{ fontSize: '12.5px', color: 'var(--on-surface-variant)', fontStyle: 'italic' }}>
                No direct citations found in this response.
              </p>
            ) : (
              citationsList.map((cite, index) => (
                <div
                  key={index}
                  style={{
                    padding: '10px 12px',
                    background: 'var(--surface-container-low)',
                    borderLeft: '3px solid var(--primary)',
                    borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
                    fontSize: '12.5px',
                    color: 'var(--on-surface)',
                    lineHeight: '1.5',
                  }}
                >
                  {cite}
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'knowledge_map' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--on-surface)', fontFamily: 'var(--font-display)', margin: 0 }}>
                Mind Maps &amp; Architecture Diagrams
              </h4>
              {allDiagrams.length > 0 && (
                <span style={{ fontSize: '11px', color: 'var(--on-surface-variant)', background: 'var(--surface-container)', padding: '2px 8px', borderRadius: '99px' }}>
                  {allDiagrams.length} diagrams
                </span>
              )}
            </div>

            {/* Search bar */}
            {allDiagrams.length > 1 && (
              <div style={{ position: 'relative' }}>
                <svg style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', opacity: 0.4 }} width={13} height={13} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
                <input
                  type="text"
                  placeholder="Search by question or diagram type..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  style={{
                    width: '100%', boxSizing: 'border-box',
                    padding: '7px 10px 7px 30px',
                    border: '1px solid var(--outline-variant)',
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--surface-container-low)',
                    color: 'var(--on-surface)', fontSize: '12px',
                    outline: 'none', fontFamily: 'var(--font-body)',
                  }}
                />
                {searchQuery && (
                  <button onClick={() => setSearchQuery('')} style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', border: 'none', background: 'none', cursor: 'pointer', color: 'var(--on-surface-variant)', fontSize: '14px', lineHeight: 1 }}>×</button>
                )}
              </div>
            )}

            {allDiagrams.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '32px 16px', color: 'var(--on-surface-variant)', fontSize: '12.5px', display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'center' }}>
                <Icon path={ICONS.map} size={24} />
                <span>No diagrams available yet. Ask the Agent to draw a diagram!</span>
              </div>
            ) : filteredDiagrams.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '20px 16px', color: 'var(--on-surface-variant)', fontSize: '12.5px' }}>
                No matching diagrams found.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {filteredDiagrams.map((diagram, idx) => {
                  const isExpanded = expandedIdx === idx;
                  const dt = diagram.diagramType;
                  const questionTitle = diagram.userQuestion
                    ? (diagram.userQuestion.length > 72 ? diagram.userQuestion.slice(0, 72) + '…' : diagram.userQuestion)
                    : `Diagram #${idx + 1}`;
                  const timeLabel = diagram.timestamp
                    ? new Date(diagram.timestamp).toLocaleString('en-US', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit' })
                    : '';
                  return (
                    <div key={idx} style={{ border: '1px solid var(--outline-variant)', borderRadius: 'var(--radius-sm)', overflow: 'hidden', background: 'var(--surface-container-low)', boxShadow: isExpanded ? '0 4px 16px rgba(0,0,0,0.12)' : 'none', transition: 'box-shadow 0.18s' }}>
                      {/* Card header — click to expand */}
                      <button
                        onClick={() => toggleExpand(idx)}
                        style={{ width: '100%', display: 'flex', alignItems: 'flex-start', gap: '8px', padding: '10px 12px', background: isExpanded ? 'var(--primary-fixed)' : 'transparent', border: 'none', borderBottom: isExpanded ? '1px solid var(--primary-fixed-dim)' : 'none', cursor: 'pointer', textAlign: 'left', transition: 'background 0.15s' }}
                        onMouseEnter={e => { if (!isExpanded) e.currentTarget.style.background = 'var(--surface-container)'; }}
                        onMouseLeave={e => { if (!isExpanded) e.currentTarget.style.background = 'transparent'; }}
                      >
                        {/* Type badge */}
                        <span style={{ flexShrink: 0, fontSize: '10px', fontWeight: 700, padding: '2px 7px', borderRadius: '99px', background: dt.bg, color: dt.color, marginTop: '1px', letterSpacing: '0.02em' }}>
                          {dt.label}
                        </span>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          {/* Question as title */}
                          <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--on-surface)', lineHeight: '1.4', wordBreak: 'break-word' }}>
                            {questionTitle}
                          </div>
                          {timeLabel && (
                            <div style={{ fontSize: '10.5px', color: 'var(--on-surface-variant)', marginTop: '3px' }}>{timeLabel}</div>
                          )}
                        </div>
                        <span style={{ fontSize: '12px', color: 'var(--on-surface-variant)', flexShrink: 0, marginTop: '2px', display: 'inline-block', transform: isExpanded ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}>▾</span>
                      </button>

                      {/* Mini thumbnail preview (collapsed) */}
                      {!isExpanded && (
                        <div onClick={() => toggleExpand(idx)} style={{ cursor: 'pointer', background: '#ffffff', overflow: 'hidden', maxHeight: '110px', position: 'relative' }}>
                          <div style={{ transform: 'scale(0.65)', transformOrigin: 'top left', pointerEvents: 'none', minWidth: '340px', padding: '8px 10px' }}>
                            <MermaidRenderer chart={diagram.code} />
                          </div>
                          <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: '36px', background: 'linear-gradient(transparent, #ffffff)' }} />
                        </div>
                      )}

                      {/* Full expanded view */}
                      {isExpanded && (
                        <div style={{ background: '#ffffff', padding: '14px 12px', overflowX: 'auto', position: 'relative' }}>
                          <MermaidRenderer chart={diagram.code} />
                          <details style={{ marginTop: '12px' }}>
                            <summary style={{ fontSize: '11px', color: 'var(--on-surface-variant)', cursor: 'pointer', userSelect: 'none' }}>View Mermaid Source</summary>
                            <pre style={{ marginTop: '6px', padding: '8px 10px', background: 'var(--surface-container-high)', borderRadius: 'var(--radius-sm)', fontSize: '10.5px', color: 'var(--on-surface)', overflowX: 'auto', whiteSpace: 'pre-wrap', wordBreak: 'break-word', fontFamily: 'monospace' }}>{diagram.code}</pre>
                          </details>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {activeTab === 'export' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--on-surface)', fontFamily: 'var(--font-display)' }}>
              Publish to Google Workspace
            </h4>
            <p style={{ fontSize: '12.5px', color: 'var(--on-surface-variant)', lineHeight: '1.5' }}>
              Export a detailed report including generated Mermaid diagrams directly to Google Docs or Google Sheets.
            </p>

            {/* Status & Action Button */}
            {exportLinks.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '4px' }}>
                <div style={{
                  display: 'flex', alignItems: 'center', gap: '6px',
                  color: 'var(--success)', fontSize: '12.5px', fontWeight: 600
                }}>
                  <Icon path={ICONS.check} size={14} />
                  Successfully linked and published!
                </div>
                {exportLinks.map((link, i) => (
                  <a
                    key={i}
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '10px 14px',
                      background: link.type === 'google_docs' ? 'var(--primary-fixed)' : 'var(--success-container)',
                      color: link.type === 'google_docs' ? 'var(--on-primary-container)' : 'var(--success)',
                      borderRadius: 'var(--radius-sm)',
                      textDecoration: 'none',
                      fontSize: '13px',
                      fontWeight: 600,
                      transition: 'opacity 0.15s',
                    }}
                    onMouseEnter={e => e.currentTarget.style.opacity = '0.85'}
                    onMouseLeave={e => e.currentTarget.style.opacity = '1'}
                  >
                    <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Icon path={ICONS.external} size={14} />
                      {link.title}
                    </span>
                    <span style={{ fontSize: '11px', opacity: 0.8 }}>Open ›</span>
                  </a>
                ))}

                <button
                  onClick={handleExport}
                  disabled={isExporting}
                  style={{
                    marginTop: '8px',
                    padding: '8px 12px',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--outline-variant)',
                    background: 'transparent',
                    color: 'var(--on-surface-variant)',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  Re-export new document
                </button>
              </div>
            ) : (
              <div style={{ marginTop: '8px' }}>
                <button
                  onClick={handleExport}
                  disabled={isExporting}
                  style={{
                    width: '100%',
                    padding: '10px 16px',
                    background: 'var(--primary-container)',
                    color: 'var(--on-primary-container)',
                    border: 'none',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '13px',
                    fontWeight: 600,
                    cursor: isExporting ? 'default' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    transition: 'background 0.15s',
                  }}
                  onMouseEnter={e => { if (!isExporting) e.currentTarget.style.background = 'var(--primary)'; }}
                  onMouseLeave={e => { if (!isExporting) e.currentTarget.style.background = 'var(--primary-container)'; }}
                >
                  {isExporting ? (
                    <>
                      <span style={{ display: 'inline-block', animation: 'spin 1s linear infinite' }}>
                        <Icon path={ICONS.loader} size={14} />
                      </span>
                      Linking Google Docs &amp; Sheets...
                    </>
                  ) : (
                    <>
                      <Icon path={ICONS.export} size={14} />
                      Export to Google Docs &amp; Sheets
                    </>
                  )}
                </button>

                {exportError && (
                  <div style={{
                    marginTop: '10px',
                    padding: '8px 12px',
                    background: 'var(--error-container)',
                    color: 'var(--error)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '12px',
                    lineHeight: '1.4',
                  }}>
                    {exportError}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
