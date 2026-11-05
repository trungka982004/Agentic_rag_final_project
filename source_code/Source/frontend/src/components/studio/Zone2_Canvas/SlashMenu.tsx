'use client';

import React from 'react';
import { Sigma, Table as TableIcon, Bookmark, Code, FileText } from 'lucide-react';

interface SlashItem {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  action: () => void;
}

interface SlashMenuProps {
  isOpen: boolean;
  position: { top: number; left: number };
  onClose: () => void;
  onInsertMath: () => void;
  onInsertTable: () => void;
  onInsertCitation: () => void;
  onInsertAlgorithm: () => void;
}

export const SlashMenu: React.FC<SlashMenuProps> = ({
  isOpen,
  position,
  onClose,
  onInsertMath,
  onInsertTable,
  onInsertCitation,
  onInsertAlgorithm,
}) => {
  if (!isOpen) return null;

  const items: SlashItem[] = [
    {
      id: 'math',
      title: 'KaTeX Math Equation',
      description: 'Insert LaTeX formulation or display equation block',
      icon: <Sigma className="w-4 h-4 text-purple-400" />,
      action: onInsertMath,
    },
    {
      id: 'table',
      title: 'Academic Comparison Table',
      description: 'Insert Markdown benchmark or ablation table',
      icon: <TableIcon className="w-4 h-4 text-emerald-400" />,
      action: onInsertTable,
    },
    {
      id: 'cite',
      title: 'Cite Literature (\\cite{})',
      description: 'Insert grounded reference link from 618 indexed papers',
      icon: <Bookmark className="w-4 h-4 text-amber-400" />,
      action: onInsertCitation,
    },
    {
      id: 'algo',
      title: 'Algorithm / Pseudocode',
      description: 'Insert structured algorithm formulation',
      icon: <Code className="w-4 h-4 text-blue-400" />,
      action: onInsertAlgorithm,
    },
  ];

  return (
    <div
      className="fixed z-50 w-72 bg-neutral-900 border border-neutral-700/80 rounded-xl shadow-2xl p-1.5 backdrop-blur-md animate-in fade-in zoom-in-95 duration-150"
      style={{ top: `${position.top}px`, left: `${position.left}px` }}
      onMouseDown={(e) => e.preventDefault()}
    >
      <div className="px-2.5 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-neutral-400 border-b border-neutral-800 mb-1">
        Insert Academic Block
      </div>
      <div className="space-y-0.5">
        {items.map((item) => (
          <button
            key={item.id}
            onClick={() => {
              item.action();
              onClose();
            }}
            className="w-full flex items-start gap-2.5 px-2.5 py-2 rounded-lg text-left hover:bg-neutral-800 transition-colors group"
          >
            <div className="p-1 rounded bg-neutral-800/80 group-hover:bg-neutral-700 mt-0.5 text-neutral-300">
              {item.icon}
            </div>
            <div>
              <div className="text-xs font-medium text-neutral-200 group-hover:text-white">
                {item.title}
              </div>
              <div className="text-[11px] text-neutral-400 leading-tight">
                {item.description}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

