'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useStudioStore } from '@/lib/studioStore';
import { useAutoSave } from '@/hooks/useAutoSave';
import { SlashMenu } from './SlashMenu';
import { FloatingAIToolbar } from './FloatingAIToolbar';
import {
  Save,
  Check,
  AlertCircle,
  Loader2,
  Bold,
  Italic,
  Heading2,
  Heading3,
  Code,
  Sigma,
  Table as TableIcon,
  Bookmark,
  Sparkles,
  Maximize2
} from 'lucide-react';

export const AcademicEditor: React.FC = () => {
  const {
    currentProject,
    activeSectionId,
    sections,
    isSaving,
    lastSavedAt,
    saveError,
    updateSectionContent,
    setActiveCitation,
    setZone3View,
  } = useStudioStore();

  const activeSection = sections.find((s) => s.id === activeSectionId) || sections[0];

  const [content, setContent] = useState<string>(activeSection?.content_markdown || '');
  const [selectedText, setSelectedText] = useState<string>('');
  const [floatingPos, setFloatingPos] = useState<{ top: number; left: number }>({ top: 0, left: 0 });
  const [showFloating, setShowFloating] = useState<boolean>(false);
  const [showSlashMenu, setShowSlashMenu] = useState<boolean>(false);
  const [slashPos, setSlashPos] = useState<{ top: number; left: number }>({ top: 0, left: 0 });
  const [isAiLoading, setIsAiLoading] = useState<boolean>(false);

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Sync content when section switches
  useEffect(() => {
    if (activeSection) {
      setContent(activeSection.content_markdown || '');
    }
  }, [activeSectionId, activeSection?.id]);

  // Hook into auto-save with 2s debounce
  const { saveNow } = useAutoSave(
    currentProject?.id,
    activeSection?.id,
    content,
    2000
  );

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setContent(val);
    if (activeSection) {
      updateSectionContent(activeSection.id, val);
    }

    // Check if user just typed '/'
    const cursor = e.target.selectionStart;
    if (cursor > 0 && val[cursor - 1] === '/') {
      const rect = e.target.getBoundingClientRect();
      setSlashPos({
        top: rect.top + 80,
        left: rect.left + 40,
      });
      setShowSlashMenu(true);
    } else {
      setShowSlashMenu(false);
    }
  };

  const handleMouseUp = () => {
    if (!textareaRef.current) return;
    const start = textareaRef.current.selectionStart;
    const end = textareaRef.current.selectionEnd;
    const sel = content.slice(start, end).trim();

    if (sel.length > 3) {
      setSelectedText(sel);
      const rect = textareaRef.current.getBoundingClientRect();
      setFloatingPos({
        top: rect.top + 50,
        left: rect.left + 150,
      });
      setShowFloating(true);
    } else {
      setShowFloating(false);
    }
  };

  const insertAtCursor = useCallback((insertion: string) => {
    if (!textareaRef.current) return;
    const start = textareaRef.current.selectionStart;
    const end = textareaRef.current.selectionEnd;
    const before = content.slice(0, start);
    const after = content.slice(end);
    const newContent = before + insertion + after;
    setContent(newContent);
    if (activeSection) {
      updateSectionContent(activeSection.id, newContent);
    }
    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.focus();
        textareaRef.current.setSelectionRange(start + insertion.length, start + insertion.length);
      }
    }, 50);
  }, [content, activeSection, updateSectionContent]);

  const handleInsertMath = () => {
    insertAtCursor('\n$$\n\\mathcal{L}_{total} = \\alpha \\mathcal{L}_{CE} + \\beta \\mathcal{L}_{RAG}\n$$\n');
  };

  const handleInsertTable = () => {
    insertAtCursor(
      '\n| Model Architecture | Precision (%) | Recall (%) | F1-Score | Latency (ms) |\n| :--- | :---: | :---: | :---: | :---: |\n| Baseline Chatbot | 78.4 | 74.2 | 76.2 | 1250 |\n| Tri-Tier Agentic RAG | **94.8** | **92.3** | **93.5** | **420** |\n\n'
    );
  };

  const handleInsertCitation = () => {
    insertAtCursor('\\cite{vaswani2017attention} ');
  };

  const handleInsertAlgorithm = () => {
    insertAtCursor(
      '\n```latex\n\\begin{algorithm}[H]\n\\caption{Context-Aware Grounded Span Retrieval}\n\\begin{algorithmic}[1]\n\\STATE \\textbf{Input:} Query $q$, Vector Index $\\mathcal{V}$, Corpus $\\mathcal{D}$\n\\STATE \\textbf{Output:} Verified Citations $\\mathcal{C}$\n\\STATE Retrieve top-$k$ spans from $\\mathcal{V}$\n\\STATE Apply cross-encoder reranking\n\\RETURN $\\mathcal{C}$\n\\end{algorithmic}\n\\end{algorithm}\n```\n'
    );
  };

  const handleAiAction = async (promptType: 'polish' | 'evidence' | 'condense' | 'expand') => {
    setIsAiLoading(true);
    try {
      // In Phase 2, mock or connect to prompt node; in Phase 4 connected to LangGraph nodes
      if (promptType === 'evidence') {
        // Open Zone 3 Copilot / Verifier
        setZone3View('copilot');
      } else if (promptType === 'polish') {
        const polished = `Furthermore, systematic empirical evaluation demonstrates that the proposed architecture achieves robust convergence across heterogeneous multi-modal tasks.`;
        if (textareaRef.current) {
          const start = textareaRef.current.selectionStart;
          const end = textareaRef.current.selectionEnd;
          const newContent = content.slice(0, start) + polished + content.slice(end);
          setContent(newContent);
          if (activeSection) updateSectionContent(activeSection.id, newContent);
        }
      }
      setShowFloating(false);
    } finally {
      setIsAiLoading(false);
    }
  };

  const wordCount = content.trim().split(/\s+/).filter(Boolean).length;
  const readingTime = Math.ceil(wordCount / 200);

  // Extract all citations in text to make clickable tags
  const citationMatches = Array.from(content.matchAll(/\\cite\{([^}]+)\}/g)).map((m) => m[1]);

  return (
    <div className="flex flex-col h-full bg-neutral-950 text-neutral-100 overflow-hidden relative">
      {/* Top Status & Formatting Bar */}
      <div className="flex items-center justify-between px-6 py-2.5 border-b border-neutral-800 bg-neutral-900/60 backdrop-blur-sm z-10">
        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold uppercase tracking-wider text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
            {activeSection?.slug || 'section'}
          </span>
          <h2 className="text-sm font-medium text-neutral-200">
            {activeSection?.title || 'Untitled Section'}
          </h2>
        </div>

        {/* Quick Toolbar */}
        <div className="flex items-center gap-1 bg-neutral-800/60 p-1 rounded-lg border border-neutral-700/50">
          <button
            onClick={() => insertAtCursor('**bold text**')}
            className="p-1 hover:bg-neutral-700 rounded text-neutral-400 hover:text-white transition-colors"
            title="Bold"
          >
            <Bold className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => insertAtCursor('*italic text*')}
            className="p-1 hover:bg-neutral-700 rounded text-neutral-400 hover:text-white transition-colors"
            title="Italic"
          >
            <Italic className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => insertAtCursor('\n### Subsection Title\n')}
            className="p-1 hover:bg-neutral-700 rounded text-neutral-400 hover:text-white transition-colors"
            title="Heading"
          >
            <Heading3 className="w-3.5 h-3.5" />
          </button>
          <div className="w-[1px] h-3.5 bg-neutral-700 mx-0.5" />
          <button
            onClick={handleInsertMath}
            className="p-1 hover:bg-neutral-700 rounded text-purple-400 hover:text-purple-300 transition-colors"
            title="Insert KaTeX Math (/math)"
          >
            <Sigma className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleInsertTable}
            className="p-1 hover:bg-neutral-700 rounded text-emerald-400 hover:text-emerald-300 transition-colors"
            title="Insert Table (/table)"
          >
            <TableIcon className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleInsertCitation}
            className="p-1 hover:bg-neutral-700 rounded text-amber-400 hover:text-amber-300 transition-colors"
            title="Cite Paper (/cite)"
          >
            <Bookmark className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Auto-save & Word Count Status */}
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5 text-neutral-400">
            {isSaving ? (
              <span className="flex items-center gap-1 text-amber-400">
                <Loader2 className="w-3 h-3 animate-spin" />
                <span>Saving...</span>
              </span>
            ) : saveError ? (
              <span className="flex items-center gap-1 text-rose-400" title={saveError}>
                <AlertCircle className="w-3 h-3" />
                <span>Save failed</span>
              </span>
            ) : lastSavedAt ? (
              <span className="flex items-center gap-1 text-emerald-400/90">
                <Check className="w-3 h-3" />
                <span>Saved at {lastSavedAt}</span>
              </span>
            ) : (
              <span>Draft ready</span>
            )}
          </div>

          <div className="text-neutral-500 font-mono text-[11px] border-l border-neutral-800 pl-3">
            {wordCount} words · {readingTime} min read
          </div>
        </div>
      </div>

      {/* Citations Quick Bar (Click-to-Verify Links) */}
      {citationMatches.length > 0 && (
        <div className="flex items-center gap-2 px-8 py-1.5 bg-neutral-900/30 border-b border-neutral-800/60 overflow-x-auto text-[11px]">
          <span className="text-neutral-400 font-medium flex items-center gap-1">
            <Bookmark className="w-3 h-3 text-purple-400" />
            Detected Citations:
          </span>
          <div className="flex items-center gap-1.5">
            {citationMatches.map((key, i) => (
              <button
                key={`${key}-${i}`}
                onClick={() => {
                  setActiveCitation({
                    bibtexKey: key,
                    domain: currentProject?.primary_domain || 'it',
                  });
                }}
                className="px-2 py-0.5 rounded-full bg-purple-900/40 hover:bg-purple-800/60 text-purple-300 border border-purple-600/40 transition-colors font-mono hover:underline cursor-pointer"
                title={`Click to open source PDF and verify ${key} in Zone 3`}
              >
                \{'{'}{key}{'}'}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Main Canvas Page Canvas */}
      <div className="flex-1 overflow-y-auto px-6 py-8 flex justify-center bg-neutral-950/80">
        <div className="w-full max-w-3xl bg-neutral-900/40 border border-neutral-800/80 rounded-2xl shadow-xl p-8 min-h-[750px] flex flex-col focus-within:border-purple-500/40 transition-colors">
          <textarea
            ref={textareaRef}
            value={content}
            onChange={handleContentChange}
            onMouseUp={handleMouseUp}
            placeholder="Type '/' for academic commands (Math formulation, comparison table, grounded citation)..."
            className="w-full flex-1 bg-transparent text-neutral-200 placeholder:text-neutral-600 font-sans text-sm md:text-base leading-relaxed resize-none focus:outline-none"
            spellCheck={false}
          />
        </div>
      </div>

      {/* Slash Command Overlay */}
      <SlashMenu
        isOpen={showSlashMenu}
        position={slashPos}
        onClose={() => setShowSlashMenu(false)}
        onInsertMath={handleInsertMath}
        onInsertTable={handleInsertTable}
        onInsertCitation={handleInsertCitation}
        onInsertAlgorithm={handleInsertAlgorithm}
      />

      {/* Floating AI Toolbar for Selection */}
      <FloatingAIToolbar
        isVisible={showFloating}
        position={floatingPos}
        selectedText={selectedText}
        onApplyPrompt={handleAiAction}
        isLoading={isAiLoading}
      />
    </div>
  );
};
