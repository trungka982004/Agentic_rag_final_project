'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import type { DisplayMessage, ExportLink } from '@/types';
import dynamic from 'next/dynamic';

const MermaidRenderer = dynamic(() => import('./MermaidRenderer'), { ssr: false });

const Icon = ({ path, size = 14 }: { path: string; size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d={path} />
  </svg>
);

const ICONS = {
  brain: 'M9.5 2a6 6 0 0 1 5.5 8.5M9.5 2A6 6 0 0 0 4 8.5c0 3.1 2 5.7 4.8 6.5M9.5 2v3M15 10.5A6 6 0 0 1 9.5 17M15 10.5A6 6 0 0 0 21 8.5c0-3.3-2.7-6-6-6M15 10.5v3M9.5 17v5M9.5 17H5m4.5 5H5m9.5-7v5m0-5h4m-4 5h4',
  user: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8',
  copy: 'M8 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2M8 4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2H8zM12 11v6M9 14h6',
  external: 'M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3',
};

export function normalizeExportLinks(rawLinks: any): ExportLink[] {
  if (!rawLinks) return [];
  if (Array.isArray(rawLinks)) {
    return rawLinks.map(link => ({
      type: link.type || (link.title?.toLowerCase().includes('sheet') ? 'google_sheets' : 'google_docs'),
      url: link.url || (typeof link === 'string' ? link : ''),
      title: link.title || (link.title?.toLowerCase().includes('sheet') ? 'Google Sheets' : 'Google Docs'),
    }));
  }
  if (typeof rawLinks === 'object') {
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
    return list;
  }
  return [];
}

interface Props { 
  message: DisplayMessage; 
  isSelected?: boolean;
  onSelect?: () => void;
}

export default function MessageBubble({ message, isSelected, onSelect }: Props) {
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'flex-end',
        margin: '6px 0',
      }}>
        <div style={{
          maxWidth: '72%',
          background: 'var(--primary-container)',
          color: 'var(--on-primary)',
          borderRadius: 'var(--radius-md) var(--radius-md) var(--radius-sm) var(--radius-md)',
          padding: '10px 14px',
          fontSize: '14px',
          lineHeight: '1.6',
          fontFamily: 'var(--font-body)',
          wordBreak: 'break-word',
        }}>
          {message.content}
        </div>
      </div>
    );
  }

  /* ─── Agent response ─── */
  return (
    <div 
      onClick={onSelect}
      style={{
        display: 'flex',
        gap: '10px',
        margin: '6px 0',
        alignItems: 'flex-start',
        cursor: onSelect ? 'pointer' : 'default',
      }}
    >
      {/* Agent avatar */}
      <div style={{
        width: '28px', height: '28px',
        background: 'var(--primary-fixed)',
        border: '1px solid var(--primary-fixed-dim)',
        borderRadius: 'var(--radius-sm)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        color: 'var(--primary-container)',
        flexShrink: 0,
        marginTop: '2px',
      }}>
        <Icon path={ICONS.brain} size={14} />
      </div>

      {/* Content bubble */}
      <div style={{
        flex: 1,
        background: 'var(--surface-container-lowest)',
        border: isSelected 
          ? '1.5px solid var(--primary)' 
          : '1px solid var(--outline-variant)',
        borderRadius: 'var(--radius-sm) var(--radius-md) var(--radius-md) var(--radius-md)',
        padding: '12px 16px',
        minWidth: 0,
        boxShadow: isSelected ? '0 2px 8px rgba(34, 139, 34, 0.08)' : 'none',
        transition: 'border 0.2s, box-shadow 0.2s',
      }}>
        {/* Streaming indicator */}
        {message.isStreaming && (
          <div style={{ display: 'flex', gap: '4px', marginBottom: '8px' }}>
            {[0, 1, 2].map(i => (
              <span key={i} className="typing-dot" style={{ animationDelay: `${i * 0.2}s` }} />
            ))}
          </div>
        )}

        {/* Markdown content */}
        <div className="prose" style={{ fontSize: '14px' }}>
          <ReactMarkdown
            remarkPlugins={[remarkGfm, remarkMath]}
            rehypePlugins={[rehypeKatex]}
            components={{
              code({ node, className, children, ...props }) {
                const lang = className?.replace('language-', '') ?? '';
                const code = String(children).replace(/\n$/, '');
                const isBlock = !!className || code.includes('\n');

                if (isBlock && lang === 'mermaid') {
                  return <MermaidRenderer chart={code} />;
                }

                if (isBlock) {
                  return (
                    <div style={{ position: 'relative', margin: '8px 0' }}>
                      {lang && (
                        <div style={{
                          background: 'var(--surface-container)',
                          borderBottom: '1px solid var(--outline-variant)',
                          padding: '4px 14px',
                          fontSize: '11px',
                          fontFamily: 'var(--font-label)',
                          color: 'var(--on-surface-variant)',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          borderRadius: 'var(--radius-sm) var(--radius-sm) 0 0',
                        }}>
                          <span>{lang}</span>
                          <button
                            onClick={(e) => { e.stopPropagation(); navigator.clipboard.writeText(code); }}
                            className="btn-icon"
                            style={{ width: '20px', height: '20px' }}
                            title="Sao chép"
                          >
                            <Icon path={ICONS.copy} size={12} />
                          </button>
                        </div>
                      )}
                      <pre style={{
                        background: 'var(--inverse-surface)',
                        borderRadius: lang
                          ? '0 0 var(--radius-sm) var(--radius-sm)'
                          : 'var(--radius-sm)',
                        padding: '14px 16px',
                        overflowX: 'auto',
                        margin: 0,
                        border: '1px solid var(--outline-variant)',
                        borderTop: lang ? 'none' : undefined,
                      }}>
                        <code style={{
                          fontFamily: "'Fira Code', 'Fira Mono', monospace",
                          fontSize: '13px',
                          color: 'var(--inverse-on-surface)',
                          lineHeight: '1.6',
                        }}>
                          {code}
                        </code>
                      </pre>
                    </div>
                  );
                }

                return (
                  <code style={{
                    background: 'var(--surface-container)',
                    border: '1px solid var(--outline-variant)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '1px 5px',
                    fontFamily: "'Fira Code', monospace",
                    fontSize: '0.88em',
                  }}>
                    {children}
                  </code>
                );
              },
              blockquote({ children }) {
                return (
                  <div className="citation">
                    {children}
                  </div>
                );
              },
              pre({ children }) {
                return <>{children}</>;
              },
            }}
          >
            {message.content || ''}
          </ReactMarkdown>
        </div>

        {/* Export links (Google Docs/Sheets) */}
        {(() => {
          const rawLinks = message.isStreaming ? message.exportLinks : message.export_links;
          const links = normalizeExportLinks(rawLinks);
          if (links.length === 0) return null;
          return (
            <div style={{
              marginTop: '12px',
              paddingTop: '12px',
              borderTop: '1px solid var(--surface-container-high)',
              display: 'flex',
              gap: '8px',
              flexWrap: 'wrap',
            }}>
              {links.map((link, i) => (
                <a
                  key={i}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn"
                  style={{ 
                    fontSize: '12.5px', 
                    padding: '6px 12px', 
                    gap: '6px',
                    display: 'inline-flex',
                    alignItems: 'center',
                    background: link.type === 'google_docs' ? 'var(--primary-container)' : 'var(--success-container)',
                    color: link.type === 'google_docs' ? 'var(--on-primary-container)' : 'var(--success)',
                    border: 'none',
                    borderRadius: 'var(--radius-sm)',
                    fontWeight: 600,
                  }}
                  onClick={(e) => e.stopPropagation()}
                >
                  <Icon path={ICONS.external} size={13} />
                  {link.title}
                </a>
              ))}
            </div>
          );
        })()}
      </div>
    </div>
  );
}
