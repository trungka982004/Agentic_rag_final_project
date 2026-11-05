'use client';

import React from 'react';

export interface BoundingBoxOverlayProps {
  bbox: [number, number, number, number]; // [x0, y0, x1, y1] normalized to [0, 1]
  label?: string;
  color?: 'amber' | 'purple' | 'cyan';
  pageWidth?: number;
  pageHeight?: number;
}

export const BoundingBoxHighlighter: React.FC<BoundingBoxOverlayProps> = ({
  bbox,
  label = 'Grounded Citation Source',
  color = 'amber',
}) => {
  const [x0, y0, x1, y1] = bbox;

  // Convert normalized fractions to percentages
  const left = `${Math.max(0, Math.min(100, x0 * 100))}%`;
  const top = `${Math.max(0, Math.min(100, y0 * 100))}%`;
  const width = `${Math.max(1, Math.min(100, (x1 - x0) * 100))}%`;
  const height = `${Math.max(1, Math.min(100, (y1 - y0) * 100))}%`;

  const colorStyles = {
    amber: {
      bg: 'rgba(234, 179, 8, 0.25)',
      border: 'border-yellow-400',
      shadow: 'shadow-[0_0_15px_rgba(234,179,8,0.7)]',
      badge: 'bg-yellow-500 text-black',
    },
    purple: {
      bg: 'rgba(168, 85, 247, 0.25)',
      border: 'border-purple-400',
      shadow: 'shadow-[0_0_15px_rgba(168,85,247,0.7)]',
      badge: 'bg-purple-500 text-white',
    },
    cyan: {
      bg: 'rgba(6, 182, 212, 0.25)',
      border: 'border-cyan-400',
      shadow: 'shadow-[0_0_15px_rgba(6,182,212,0.7)]',
      badge: 'bg-cyan-500 text-black',
    },
  }[color];

  return (
    <div
      className={`absolute z-30 pointer-events-none rounded transition-all duration-300 border-2 animate-pulse ${colorStyles.border} ${colorStyles.shadow}`}
      style={{
        left,
        top,
        width,
        height,
        backgroundColor: colorStyles.bg,
      }}
    >
      {label && (
        <div
          className={`absolute -top-5 left-0 px-1.5 py-0.5 rounded text-[10px] font-bold tracking-wide uppercase shadow-md flex items-center gap-1 ${colorStyles.badge}`}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-white animate-ping" />
          <span>{label}</span>
        </div>
      )}
    </div>
  );
};

