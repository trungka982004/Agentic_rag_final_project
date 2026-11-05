'use client';

import React from 'react';
import { useStudioStore } from '@/lib/studioStore';
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
  CheckCircle2
} from 'lucide-react';

export const Zone3Pane: React.FC = () => {
  const {
    zone3View,
    setZone3View,
    activeCitation,
    references,
    isZone3Open,
    toggleZone3,
  } = useStudioStore();

  if (!isZone3Open) return null;

  return (
    <section className="w-96 lg:w-[440px] h-full bg-neutral-900 border-l border-neutral-800 flex flex-col select-none text-neutral-300">
      {/* Top View Selector Header */}
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-neutral-800 bg-neutral-900/80">
        <div className="flex items-center gap-1 bg-neutral-800/80 p-0.5 rounded-lg border border-neutral-700/60">
          <button
            onClick={() => setZone3View('verifier')}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${
              zone3View === 'verifier'
                ? 'bg-neutral-700 text-white shadow-sm'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
            <span>Verifier</span>
          </button>
          <button
            onClick={() => setZone3View('copilot')}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${
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
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${
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
      <div className="flex-1 overflow-y-auto p-4">
        {zone3View === 'verifier' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-neutral-400 flex items-center gap-1.5">
                <FileCheck2 className="w-4 h-4 text-cyan-400" />
                Grounding Verification
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800/60 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" />
                618 Indexed PDFs
              </span>
            </div>

            {activeCitation ? (
              <div className="space-y-3">
                <div className="p-3.5 rounded-xl bg-neutral-950/70 border border-neutral-800 space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-mono text-purple-400 font-semibold">
                      \{'{'}{activeCitation.bibtexKey}{'}'}
                    </span>
                    <span className="text-[11px] text-neutral-500">
                      Domain: {activeCitation.domain?.toUpperCase() || 'IT'}
                    </span>
                  </div>
                  <h4 className="text-xs font-medium text-neutral-200 leading-snug">
                    {activeCitation.paperTitle ||
                      'Attention Is All You Need / Transformer Empirical Grounding'}
                  </h4>
                </div>

                <div className="p-3.5 rounded-xl bg-purple-950/20 border border-purple-800/40 space-y-2">
                  <div className="flex items-center gap-1.5 text-xs font-medium text-purple-300">
                    <Quote className="w-3.5 h-3.5 text-purple-400" />
                    <span>Matched Source Span (Page {activeCitation.page || 1}):</span>
                  </div>
                  <p className="text-xs text-neutral-300 italic leading-relaxed border-l-2 border-purple-500 pl-2.5 font-serif">
                    {activeCitation.rawText ||
                      '"The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. We propose a new simple network architecture, the Transformer..."'}
                  </p>
                </div>

                {/* PDF Viewer Mock / Stage Container for Phase 3 */}
                <div className="p-4 rounded-xl bg-neutral-950 border border-neutral-800 text-center space-y-2">
                  <div className="text-xs text-neutral-400">
                    PDF Split-Screen Verifier (Ready for Phase 3)
                  </div>
                  <div className="h-48 rounded-lg bg-neutral-900 border border-dashed border-neutral-800 flex flex-col items-center justify-center p-4">
                    <ShieldCheck className="w-8 h-8 text-cyan-400 mb-2 opacity-80" />
                    <p className="text-[11px] text-neutral-400 max-w-xs">
                      Bounding Box Overlay active on coordinates: [0.74, 0.06, 0.91, 0.07]
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-16 text-center text-neutral-500 space-y-3">
                <FileCheck2 className="w-10 h-10 mx-auto text-neutral-700" />
                <p className="text-xs max-w-xs mx-auto">
                  Click on any citation tag like <code className="text-purple-400">\cite&#123;...&#125;</code> in
                  your paper canvas to verify its exact source sentence and bounding box in the original PDF.
                </p>
              </div>
            )}
          </div>
        )}

        {zone3View === 'copilot' && (
          <div className="space-y-4">
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
                placeholder="Ask paper corpus..."
                className="w-full bg-neutral-950 border border-neutral-700 text-xs px-3 py-2 rounded-lg text-white placeholder:text-neutral-500 focus:outline-none focus:border-purple-500"
              />
            </div>
          </div>
        )}

        {zone3View === 'references' && (
          <div className="space-y-4">
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
                    className="p-3 rounded-lg bg-neutral-950 border border-neutral-800 text-xs space-y-1"
                  >
                    <div className="font-mono text-purple-400 font-semibold">@{ref.bibtex_key}</div>
                    <div className="text-neutral-200 font-medium">{ref.title}</div>
                    <div className="text-neutral-500 text-[11px]">
                      {ref.authors} ({ref.year || 'n.d.'})
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
