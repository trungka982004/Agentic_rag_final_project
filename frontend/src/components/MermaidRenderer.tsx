'use client';

import { useEffect, useRef, useState } from 'react';

interface MermaidRendererProps {
  chart: string;
}

let mermaidInitialized = false;

export default function MermaidRenderer({ chart }: MermaidRendererProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const idRef = useRef(`mermaid-${Math.random().toString(36).slice(2)}`);

  useEffect(() => {
    let cancelled = false;

    async function render() {
      setIsLoading(true);
      setError(null);

      try {
        const mermaid = (await import('mermaid')).default;

        if (!mermaidInitialized) {
          mermaid.initialize({
            startOnLoad: false,
            theme: 'dark',
            themeVariables: {
              background: '#0f1318',
              primaryColor: '#1e3a5f',
              primaryTextColor: '#e8edf5',
              primaryBorderColor: '#3b82f6',
              lineColor: '#4a5568',
              secondaryColor: '#1a2333',
              tertiaryColor: '#151c26',
              edgeLabelBackground: '#0f1318',
              clusterBkg: '#151c26',
              titleColor: '#93c5fd',
              nodeTextColor: '#e8edf5',
            },
            flowchart: { htmlLabels: true, curve: 'linear' },
            sequence: { useMaxWidth: true },
          });
          mermaidInitialized = true;
        }

        // Validate first
        const { svg: renderedSvg } = await mermaid.render(idRef.current, chart.trim());

        if (!cancelled) {
          setSvg(renderedSvg);
          setIsLoading(false);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Không thể render sơ đồ');
          setIsLoading(false);
        }
      }
    }

    render();
    return () => { cancelled = true; };
  }, [chart]);

  if (isLoading) {
    return (
      <div className="mermaid-loading">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--text-muted)', fontSize: '0.85em' }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
            style={{ animation: 'spin 1s linear infinite' }}>
            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
          </svg>
          Đang render sơ đồ...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mermaid-error" style={{
        background: 'rgba(239,68,68,0.08)',
        border: '1px solid rgba(239,68,68,0.25)',
        borderRadius: 'var(--radius-md)',
        padding: '12px 16px',
        marginTop: '8px',
      }}>
        <p style={{ color: '#fca5a5', fontSize: '0.8em', fontFamily: 'JetBrains Mono, monospace', margin: 0 }}>
          ⚠️ Lỗi render Mermaid: {error}
        </p>
        <pre style={{
          marginTop: '8px',
          fontSize: '0.75em',
          color: 'var(--text-muted)',
          overflow: 'auto',
          maxHeight: '120px',
          whiteSpace: 'pre-wrap',
        }}>
          {chart}
        </pre>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="mermaid-container"
      style={{
        background: 'rgba(15,19,24,0.8)',
        border: '1px solid var(--border-muted)',
        borderRadius: 'var(--radius-md)',
        padding: '20px',
        margin: '8px 0',
        overflowX: 'auto',
        textAlign: 'center',
      }}
      dangerouslySetInnerHTML={{ __html: svg ?? '' }}
    />
  );
}
