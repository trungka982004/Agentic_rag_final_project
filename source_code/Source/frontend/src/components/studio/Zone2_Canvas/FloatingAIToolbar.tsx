'use client';

import React from 'react';
import { Sparkles, Search, Scissors, BookOpen, Check, Loader2 } from 'lucide-react';

interface FloatingAIToolbarProps {
  isVisible: boolean;
  position: { top: number; left: number };
  selectedText: string;
  onApplyPrompt: (promptType: 'polish' | 'evidence' | 'condense' | 'expand') => void;
  isLoading?: boolean;
}

export const FloatingAIToolbar: React.FC<FloatingAIToolbarProps> = ({
  isVisible,
  position,
  selectedText,
  onApplyPrompt,
  isLoading = false,
}) => {
  if (!isVisible || !selectedText.trim()) return null;

  return (
    <div
      className="fixed z-50 flex items-center gap-1 bg-neutral-900/95 border border-purple-500/30 rounded-full shadow-2xl px-2 py-1.5 backdrop-blur-md animate-in fade-in zoom-in-95 duration-150"
      style={{
        top: `${Math.max(10, position.top - 46)}px`,
        left: `${Math.max(10, position.left)}px`,
      }}
      onMouseDown={(e) => e.preventDefault()}
    >
      <div className="flex items-center gap-1 pr-1 border-r border-neutral-700/60">
        <Sparkles className="w-3.5 h-3.5 text-purple-400 animate-pulse ml-1" />
        <span className="text-[11px] font-semibold text-purple-300 mr-1">AI Copilot</span>
      </div>

      {isLoading ? (
        <div className="flex items-center gap-1.5 px-3 py-1 text-xs text-neutral-300">
          <Loader2 className="w-3.5 h-3.5 animate-spin text-purple-400" />
          <span>Refining with LLM...</span>
        </div>
      ) : (
        <>
          <button
            onClick={() => onApplyPrompt('polish')}
            className="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium text-neutral-200 hover:text-white hover:bg-neutral-800 transition-colors"
            title="Rewrite in formal IEEE/ACM academic style"
          >
            <Sparkles className="w-3 h-3 text-amber-400" />
            <span>Polish Tone</span>
          </button>

          <button
            onClick={() => onApplyPrompt('evidence')}
            className="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium text-neutral-200 hover:text-white hover:bg-neutral-800 transition-colors"
            title="Retrieve grounded spans and suggest \cite{} from 618 papers"
          >
            <Search className="w-3 h-3 text-cyan-400" />
            <span>Find Evidence</span>
          </button>

          <button
            onClick={() => onApplyPrompt('condense')}
            className="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium text-neutral-200 hover:text-white hover:bg-neutral-800 transition-colors"
            title="Make concise and reduce word count"
          >
            <Scissors className="w-3 h-3 text-rose-400" />
            <span>Condense</span>
          </button>

          <button
            onClick={() => onApplyPrompt('expand')}
            className="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium text-neutral-200 hover:text-white hover:bg-neutral-800 transition-colors"
            title="Elaborate methodology and equations"
          >
            <BookOpen className="w-3 h-3 text-emerald-400" />
            <span>Expand</span>
          </button>
        </>
      )}
    </div>
  );
};

