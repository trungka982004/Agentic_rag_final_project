'use client';

import { useEffect, useRef, useState } from 'react';

interface MermaidRendererProps {
  chart: string;
}

// Global promise chain to serialize all Mermaid rendering calls.
// This prevents concurrent renders from corrupting Mermaid's shared state/DOM.
let globalRenderQueue: Promise<void> = Promise.resolve();
let mermaidInitialized = false;

export default function MermaidRenderer({ chart }: MermaidRendererProps) {
  const [svg, setSvg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Generate a random stable ID for this render session.
  // Mermaid IDs must start with a letter and contain only alphanumeric characters.
  const idRef = useRef(`m${Math.random().toString(36).slice(2, 11)}`);

  useEffect(() => {
    let cancelled = false;

    async function queueRender() {
      setIsLoading(true);
      setError(null);

      // Append this render task to the global queue
      globalRenderQueue = globalRenderQueue.then(async () => {
        if (cancelled) return;

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

          const cleanChart = chart.trim();

          // Render without passing a hidden container parameter.
          // Mermaid calculates element widths and heights using SVG getBBox(),
          // which requires the rendering node to be visible in the DOM.
          // By default, mermaid.render will insert a temporary container, render, and return the SVG.
          const { svg: renderedSvg } = await mermaid.render(idRef.current, cleanChart);

          if (!cancelled) {
            setSvg(renderedSvg);
            setIsLoading(false);
          }
        } catch (err) {
          // Cleanup any stray elements created by Mermaid on failure.
          // Mermaid often appends a container with the target ID or "d" + target ID.
          const stray = document.getElementById(idRef.current);
          if (stray) stray.remove();
          const strayBind = document.getElementById(`d${idRef.current}`);
          if (strayBind) strayBind.remove();

          if (!cancelled) {
            const msg = err instanceof Error ? err.message : String(err);
            const firstLine = msg.split('\n').find(l => l.trim()) ?? msg;
            setError(firstLine.length > 200 ? firstLine.slice(0, 200) + '…' : firstLine);
            setIsLoading(false);
          }
        }
      });
    }

    queueRender();

    return () => {
      cancelled = true;
      // Cleanup DOM on unmount
      const stray = document.getElementById(idRef.current);
      if (stray) stray.remove();
      const strayBind = document.getElementById(`d${idRef.current}`);
      if (strayBind) strayBind.remove();
    };
  }, [chart]);

  return (
    <>
      {isLoading && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '10px',
          color: 'var(--text-muted)', fontSize: '0.85em',
          padding: '12px 0',
        }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2"
            style={{ animation: 'spin 1s linear infinite', flexShrink: 0 }}>
            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
          </svg>
          Đang render sơ đồ...
        </div>
      )}

      {!isLoading && error && (
        <div style={{
          background: 'rgba(239,68,68,0.08)',
          border: '1px solid rgba(239,68,68,0.25)',
          borderRadius: 'var(--radius-md)',
          padding: '12px 16px',
          marginTop: '8px',
        }}>
          <p style={{
            color: '#fca5a5', fontSize: '0.8em',
            fontFamily: 'JetBrains Mono, monospace',
            margin: '0 0 8px',
          }}>
            ⚠️ Mermaid parse error
          </p>
          <p style={{ color: '#f87171', fontSize: '0.75em', margin: '0 0 8px', fontFamily: 'monospace' }}>
            {error}
          </p>
          <details>
            <summary style={{ color: 'var(--text-muted)', fontSize: '0.75em', cursor: 'pointer' }}>
              Xem source
            </summary>
            <pre style={{
              marginTop: '6px', fontSize: '0.72em',
              color: 'var(--text-muted)',
              overflow: 'auto', maxHeight: '120px',
              whiteSpace: 'pre-wrap',
            }}>
              {chart}
            </pre>
          </details>
        </div>
      )}

      {!isLoading && !error && svg && (
        <div
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
          dangerouslySetInnerHTML={{ __html: svg }}
        />
      )}
    </>
  );
}
