'use client';

import { useState, useEffect } from 'react';
import type { DisplayMessage, ExportLink } from '@/types';
import dynamic from 'next/dynamic';
import api from '@/services/api';
import { normalizeExportLinks } from './MessageBubble';

const MermaidRenderer = dynamic(() => import('./MermaidRenderer'), { ssr: false });

interface Props {
  selectedMessage: DisplayMessage | null;
  onUpdateMessageLinks: (messageId: string, links: ExportLink[]) => void;
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

export default function ScientificConsole({ selectedMessage, onUpdateMessageLinks }: Props) {
  const [activeTab, setActiveTab] = useState<'citations' | 'knowledge_map' | 'export'>('citations');
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  // Extract Mermaid block
  const getMermaidCode = () => {
    if (!selectedMessage?.content) return null;
    const match = selectedMessage.content.match(/```mermaid\s*([\s\S]*?)\s*```/);
    return match ? match[1].trim() : null;
  };

  const mmdCode = getMermaidCode();

  // If message has a Mermaid chart, auto-switch to knowledge_map tab on load
  useEffect(() => {
    if (mmdCode) {
      setActiveTab('knowledge_map');
    } else {
      setActiveTab('citations');
    }
  }, [selectedMessage?.id, mmdCode]);

  if (!selectedMessage) {
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
          Chưa chọn câu trả lời nào để hiển thị dữ liệu khoa học chuyên sâu.
        </div>
      </div>
    );
  }

  // Parse citations
  const citationsList: string[] = [];
  if (selectedMessage.content) {
    // extract blockquotes
    const lines = selectedMessage.content.split('\n');
    lines.forEach(line => {
      if (line.startsWith('>') || line.startsWith('»')) {
        citationsList.push(line.replace(/^[>»]\s*/, '').trim());
      }
      // search for citation brackets like [1], [2], or author names
      const citationMatches = line.match(/\[\d+\]|Vaswani|Devlin|Lewis|Attention/gi);
      if (citationMatches && line.length > 20 && !line.startsWith('>') && !line.startsWith('»') && !line.includes('```')) {
        citationsList.push(line.trim());
      }
    });
  }

  const exportLinks = normalizeExportLinks(
    selectedMessage.isStreaming ? selectedMessage.exportLinks : selectedMessage.export_links
  );

  const handleExport = async () => {
    if (isExporting || !selectedMessage.id) return;
    setIsExporting(true);
    setExportError(null);

    try {
      // POST message export endpoint
      const res = await api.post(`/api/ws/messages/${selectedMessage.id}/export`);
      const links = normalizeExportLinks(res.data.export_links);
      onUpdateMessageLinks(selectedMessage.id, links);
      setActiveTab('export');
    } catch (err: any) {
      console.error(err);
      setExportError(err.response?.data?.detail || 'Không thể xuất tài liệu. Vui lòng kiểm tra cấu hình credentials.json.');
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
          Trích dẫn ({citationsList.length})
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
          Bản đồ {mmdCode ? '✓' : ''}
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
          Xuất bản {exportLinks.length > 0 ? '✓' : ''}
        </button>
      </div>

      {/* Tab content body */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
        {activeTab === 'citations' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--on-surface)', fontFamily: 'var(--font-display)' }}>
              Trích Dẫn Gốc & Nguồn Tài Liệu
            </h4>
            {citationsList.length === 0 ? (
              <p style={{ fontSize: '12.5px', color: 'var(--on-surface-variant)', fontStyle: 'italic' }}>
                Không tìm thấy trích dẫn trực tiếp nào trong câu trả lời này.
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
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', height: '100%' }}>
            <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--on-surface)', fontFamily: 'var(--font-display)' }}>
              Sơ Đồ Tư Duy & Kiến Trúc
            </h4>
            {mmdCode ? (
              <div style={{
                background: 'var(--inverse-surface)',
                border: '1px solid var(--outline-variant)',
                borderRadius: 'var(--radius-sm)',
                padding: '12px',
                overflowX: 'auto',
                boxShadow: 'inset 0 1px 4px rgba(0,0,0,0.1)'
              }}>
                <MermaidRenderer chart={mmdCode} />
              </div>
            ) : (
              <div style={{
                textAlign: 'center',
                padding: '32px 16px',
                color: 'var(--on-surface-variant)',
                fontSize: '12.5px',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
                alignItems: 'center',
              }}>
                <Icon path={ICONS.map} size={24} />
                <span>Câu trả lời này không bao gồm mã sơ đồ Mermaid. Hãy yêu cầu Agent vẽ sơ đồ nếu cần!</span>
              </div>
            )}
          </div>
        )}

        {activeTab === 'export' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--on-surface)', fontFamily: 'var(--font-display)' }}>
              Xuất Bản Sang Google Workspace
            </h4>
            <p style={{ fontSize: '12.5px', color: 'var(--on-surface-variant)', lineHeight: '1.5' }}>
              Xuất báo cáo chi tiết kèm hình ảnh sơ đồ Mermaid đã sinh ra thẳng sang tài liệu Google Docs hoặc Google Sheets của bạn.
            </p>

            {/* Status & Action Button */}
            {exportLinks.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '4px' }}>
                <div style={{
                  display: 'flex', alignItems: 'center', gap: '6px',
                  color: 'var(--success)', fontSize: '12.5px', fontWeight: 600
                }}>
                  <Icon path={ICONS.check} size={14} />
                  Đã liên kết xuất bản thành công!
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
                    <span style={{ fontSize: '11px', opacity: 0.8 }}>Mở ›</span>
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
                  Xuất lại tài liệu mới
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
                      Đang liên kết Google Docs & Sheets...
                    </>
                  ) : (
                    <>
                      <Icon path={ICONS.export} size={14} />
                      Xuất sang Google Docs & Sheets
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
