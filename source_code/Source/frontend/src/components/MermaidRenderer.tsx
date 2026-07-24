'use client';

import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';

interface MermaidRendererProps {
  chart: string;
}

// Global promise chain to serialize all Mermaid rendering calls.
// This prevents concurrent renders from corrupting Mermaid's shared state/DOM.
let globalRenderQueue: Promise<void> = Promise.resolve();
let mermaidInitialized_v2 = false;

export default function MermaidRenderer({ chart }: MermaidRendererProps) {
  const [svg, setSvg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isFullScreen, setIsFullScreen] = useState(false);

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

          if (!mermaidInitialized_v2) {
            mermaid.initialize({
              startOnLoad: false,
              theme: 'default',
              flowchart: { htmlLabels: true, curve: 'linear' },
              sequence: { useMaxWidth: true },
            });
            mermaidInitialized_v2 = true;
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
          Rendering diagram...
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
              View source
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
        <>
          <div
            className="mermaid-container"
            onClick={() => setIsFullScreen(true)}
            style={{
              background: '#ffffff',
              border: '1px solid var(--outline-variant)',
              borderRadius: 'var(--radius-md)',
              padding: '20px',
              margin: '8px 0',
              overflowX: 'auto',
              textAlign: 'center',
              cursor: 'zoom-in',
            }}
            dangerouslySetInnerHTML={{ __html: svg }}
          />

          {isFullScreen && createPortal(
            <div style={{
              position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
              backgroundColor: '#ffffff', zIndex: 99999,
              display: 'flex', flexDirection: 'column',
              overflow: 'hidden',
            }}>
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '12px 24px', borderBottom: '1px solid var(--outline-variant)',
                background: 'var(--surface-container-lowest)'
              }}>
                <h2 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--on-surface)', margin: 0 }}>
                  Fullscreen Mode
                </h2>
                <button
                  onClick={() => setIsFullScreen(false)}
                  style={{
                    background: 'var(--surface-container-high)', border: 'none',
                    borderRadius: '50%', width: '36px', height: '36px',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    cursor: 'pointer', color: 'var(--on-surface)',
                  }}
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                </button>
              </div>
              <div style={{ flex: 1, overflow: 'auto', padding: '32px', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#f8f9fa' }}>
                <div style={{ background: '#ffffff', padding: '24px', borderRadius: '8px', minWidth: '60%', textAlign: 'center', boxShadow: '0 4px 24px rgba(0,0,0,0.08)' }} dangerouslySetInnerHTML={{ __html: svg }} />
              </div>
            </div>,
            document.body
          )}
        </>
      )}
    </>
  );
}
