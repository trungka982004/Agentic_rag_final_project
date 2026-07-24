'use client';

import { memo } from 'react';
import type { ActiveNode } from '@/types';
import { getNodeInfo } from '@/lib/utils';

interface AgentThoughtBarProps {
  nodes: ActiveNode[];
  isStreaming: boolean;
}

const AgentThoughtBar = memo(function AgentThoughtBar({ nodes, isStreaming }: AgentThoughtBarProps) {
  if (nodes.length === 0 && !isStreaming) return null;

  return (
    <div style={{
      display: 'flex',
      flexWrap: 'wrap',
      gap: '6px',
      marginBottom: '10px',
      padding: '8px 12px',
      background: 'var(--bg-overlay)',
      borderRadius: 'var(--radius-sm)',
      border: '1px solid var(--border-subtle)',
    }}>
      <span style={{
        fontSize: '0.7em',
        color: 'var(--text-muted)',
        textTransform: 'uppercase',
        letterSpacing: '0.08em',
        marginRight: '4px',
        alignSelf: 'center',
      }}>
        Workflow:
      </span>
      {nodes.map((n, idx) => {
        const { label, cssClass } = getNodeInfo(n.name);
        return (
          <span
            key={`${n.name}-${idx}`}
            className={cssClass}
            style={{
              fontSize: '0.72em',
              padding: '2px 9px',
              borderRadius: '99px',
              border: '1px solid',
              fontWeight: 500,
              letterSpacing: '0.02em',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            {label}
            {n.status === 'running' && isStreaming && (
              <span style={{
                width: '5px',
                height: '5px',
                borderRadius: '50%',
                background: 'currentColor',
                animation: 'pulse-dot 1s infinite',
                display: 'inline-block',
              }} />
            )}
          </span>
        );
      })}
    </div>
  );
});

export default AgentThoughtBar;
