'use client';

import React from 'react';
import { useStudioStore } from '@/lib/studioStore';
import { SplitPDFViewer } from './SplitPDFViewer';
import {
  FileCheck2,
  Sparkles,
  BookOpen,
  X,
  ExternalLink,
  ChevronRight,
  Search,
  Quote,
  ShieldCheck,
  CheckCircle2,
  Copy
} from 'lucide-react';

export const Zone3Pane: React.FC = () => {
  const {
    zone3View,
    setZone3View,
    activeCitation,
    references,
    isZone3Open,
    toggleZone3,
    zone3Width,
  } = useStudioStore();

  if (!isZone3Open) return null;

  return (
    <section className="h-full bg-neutral-900 border-l border-neutral-800 flex flex-col select-none text-neutral-300 flex-shrink-0" style={{ width: `${zone3Width}px` }}>
      {/* Top View Selector Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-neutral-800 bg-neutral-900/90 z-10 flex-shrink-0">
        <div className="flex items-center gap-1 bg-neutral-800/80 p-0.5 rounded-lg border border-neutral-700/60">
          <button
            onClick={() => setZone3View('verifier')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-colors ${
              zone3View === 'verifier'
                ? 'bg-neutral-700 text-white shadow-sm'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
            <span>PDF Verifier</span>
          </button>
          <button
            onClick={() => setZone3View('copilot')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-colors ${
              zone3View === 'copilot'
                ? 'bg-neutral-700 text-white shadow-sm'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            <span>AI Copilot</span>
          </button>
          <button
            onClick={() => setZone3View('references')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-colors ${
              zone3View === 'references'
                ? 'bg-neutral-700 text-white shadow-sm'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5 text-amber-400" />
            <span>BibTeX</span>
          </button>
        </div>

        <button
          onClick={() => toggleZone3(false)}
          className="p-1 hover:bg-neutral-800 rounded text-neutral-500 hover:text-white transition-colors"
          title="Close panel"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Pane Content based on active tab */}
      <div className="flex-1 overflow-hidden flex flex-col">
        {zone3View === 'verifier' && <SplitPDFViewer />}

        {zone3View === 'copilot' && (
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-neutral-400 flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-purple-400" />
                Academic AI Copilot
              </span>
            </div>
            <div className="p-3.5 rounded-xl bg-neutral-950/80 border border-neutral-800 text-xs text-neutral-300 leading-relaxed">
              Ask questions across the 618 literature corpus, request methodology formulations, or ask the agent to synthesize literature matrices directly into your active section.
            </div>
            <div className="space-y-2">
              <input
                type="text"
                placeholder="Ask paper corpus (e.g. Compare ResNet vs ViT)..."
                className="w-full bg-neutral-950 border border-neutral-700 text-xs px-3 py-2 rounded-lg text-white placeholder:text-neutral-500 focus:outline-none focus:border-purple-500"
              />
            </div>
          </div>
        )}

        {zone3View === 'references' && (
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-neutral-400 flex items-center gap-1.5">
                <BookOpen className="w-4 h-4 text-amber-400" />
                Project Bibliography ({references.length})
              </span>
            </div>

            {references.length === 0 ? (
              <div className="py-12 text-center text-neutral-500 text-xs">
                No references attached yet. Use <code className="text-amber-400">/cite</code> in the editor or search papers in Copilot.
              </div>
            ) : (
              <div className="space-y-2">
                {references.map((ref) => (
                  <div
                    key={ref.id}
                    className="p-3 rounded-lg bg-neutral-950 border border-neutral-800 text-xs space-y-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-purple-400 font-semibold">@{ref.bibtex_key}</span>
                      <button
                        onClick={() => navigator.clipboard.writeText(ref.bibtex_raw)}
                        className="p-1 hover:bg-neutral-800 rounded text-neutral-500 hover:text-neutral-300"
                        title="Copy BibTeX"
                      >
                        <Copy className="w-3 h-3" />
                      </button>
                    </div>
                    <div className="text-neutral-200 font-medium">{ref.title}</div>
                    <div className="text-neutral-500 text-[11px]">
                      {ref.authors} ({ref.year || 'n.d.'}) · {ref.venue || 'ArXiv'}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
};
