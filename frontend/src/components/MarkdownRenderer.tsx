'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { lazy, Suspense, memo } from 'react';
import type { Components } from 'react-markdown';

const MermaidRenderer = lazy(() => import('./MermaidRenderer'));

interface MarkdownRendererProps {
  content: string;
  /** When true, animate text in as if being typed */
  streaming?: boolean;
}

const components: Components = {
  // Code blocks — detect mermaid fences
  code({ node, className, children, ...props }) {
    const lang = className?.replace('language-', '') ?? '';
    const code = String(children).replace(/\n$/, '');
    // A code block has a parent of `pre`; inline code does not
    const isBlock = node?.position
      ? String(children).includes('\n') || !!className
      : !!className;

    if (isBlock && lang === 'mermaid') {
      return (
        <Suspense fallback={
          <div style={{
            padding: '12px',
            color: 'var(--text-muted)',
            fontSize: '0.85em',
            fontStyle: 'italic'
          }}>
            Đang tải renderer...
          </div>
        }>
          <MermaidRenderer chart={code} />
        </Suspense>
      );
    }

    if (isBlock) {
      return (
        <div style={{ position: 'relative', margin: '0.75em 0' }}>
          {lang && (
            <div style={{
              position: 'absolute',
              top: '8px',
              right: '12px',
              fontSize: '0.7em',
              color: 'var(--text-muted)',
              fontFamily: 'JetBrains Mono, monospace',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              pointerEvents: 'none',
            }}>
              {lang}
            </div>
          )}
          <pre style={{
            background: '#0d1117',
            border: '1px solid var(--border-muted)',
            borderRadius: 'var(--radius-md)',
            padding: '1.25em',
            overflowX: 'auto',
            margin: 0,
          }}>
            <code
              style={{
                color: '#e6edf3',
                fontFamily: 'JetBrains Mono, Fira Code, monospace',
                fontSize: '0.875em',
                background: 'transparent',
                border: 'none',
                padding: 0,
              }}
            >
              {code}
            </code>
          </pre>
        </div>
      );
    }

    // Inline code
    return (
      <code
        style={{
          background: 'rgba(125,211,252,0.08)',
          color: 'var(--text-code)',
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: '0.85em',
          padding: '0.15em 0.4em',
          borderRadius: '4px',
          border: '1px solid rgba(125,211,252,0.15)',
        }}
        {...props}
      >
        {children}
      </code>
    );
  },

  // Links
  a({ href, children, ...props }) {
    return (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          color: 'var(--text-accent)',
          textDecoration: 'none',
          borderBottom: '1px solid rgba(147,197,253,0.35)',
        }}
        {...props}
      >
        {children}
      </a>
    );
  },

  // Tables
  table({ children, ...props }) {
    return (
      <div style={{ overflowX: 'auto', margin: '0.75em 0' }}>
        <table
          style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: '0.875em',
          }}
          {...props}
        >
          {children}
        </table>
      </div>
    );
  },
  th({ children, ...props }) {
    return (
      <th
        style={{
          background: 'var(--bg-elevated)',
          color: 'var(--text-accent)',
          padding: '0.6em 1em',
          textAlign: 'left',
          borderBottom: '1px solid var(--border-muted)',
          fontWeight: 500,
          fontSize: '0.875em',
        }}
        {...props}
      >
        {children}
      </th>
    );
  },
  td({ children, ...props }) {
    return (
      <td
        style={{
          padding: '0.5em 1em',
          borderBottom: '1px solid var(--border-subtle)',
          color: 'var(--text-secondary)',
        }}
        {...props}
      >
        {children}
      </td>
    );
  },

  // Blockquote
  blockquote({ children, ...props }) {
    return (
      <blockquote
        style={{
          borderLeft: '3px solid var(--accent-primary)',
          padding: '0.5em 1em',
          margin: '0.75em 0',
          background: 'var(--accent-primary-dim)',
          borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
          color: 'var(--text-secondary)',
        }}
        {...props}
      >
        {children}
      </blockquote>
    );
  },

  // Override pre to avoid wrapping everything in a prose styled pre tag,
  // since our custom code component already provides its own <pre> wrapping.
  pre({ children }) {
    return <>{children}</>;
  },
};

const MarkdownRenderer = memo(function MarkdownRenderer({
  content,
  streaming = false,
}: MarkdownRendererProps) {
  return (
    <div className="prose-chat" style={{ position: 'relative' }}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={components}
      >
        {content}
      </ReactMarkdown>
      {streaming && (
        <span
          style={{
            display: 'inline-block',
            width: '2px',
            height: '1em',
            background: 'var(--accent-primary)',
            marginLeft: '2px',
            verticalAlign: 'text-bottom',
            animation: 'pulse-dot 1s infinite',
          }}
        />
      )}
    </div>
  );
});

export default MarkdownRenderer;
