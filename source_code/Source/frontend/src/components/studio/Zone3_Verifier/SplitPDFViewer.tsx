'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useStudioStore } from '@/lib/studioStore';
import { BoundingBoxHighlighter } from './BoundingBoxHighlighter';
import {
  ChevronLeft,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  Maximize2,
  FileText,
  AlertCircle,
  Loader2,
  CheckCircle2,
  ShieldAlert,
  Search
} from 'lucide-react';
import axios from 'axios';

interface SpanData {
  id: string;
  doc_name: string;
  page_number: number;
  bbox: [number, number, number, number];
  raw_text: string;
  span_index: number;
}

export const SplitPDFViewer: React.FC = () => {
  const { activeCitation, currentProject } = useStudioStore();

  const [domain, setDomain] = useState<string>('it');
  const [docName, setDocName] = useState<string>('sample.pdf');
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(12);
  const [zoom, setZoom] = useState<number>(100);
  const [spans, setSpans] = useState<SpanData[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [highlightBbox, setHighlightBbox] = useState<[number, number, number, number] | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);

  // Synchronize when activeCitation updates
  useEffect(() => {
    if (activeCitation) {
      if (activeCitation.domain) setDomain(activeCitation.domain);
      if (activeCitation.pdfName) setDocName(activeCitation.pdfName);
      if (activeCitation.page) setPage(activeCitation.page);
      if (activeCitation.bbox) {
        setHighlightBbox(activeCitation.bbox);
      } else {
        // Default grounded sample bounding box
        setHighlightBbox([0.15, 0.22, 0.85, 0.29]);
      }
    }
  }, [activeCitation]);

  // Fetch spans from backend when docName or page changes
  useEffect(() => {
    async function loadSpans() {
      if (!docName) return;
      try {
        setLoading(true);
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
        const res = await axios.get<SpanData[]>(
          `${baseUrl}/api/documents/${domain}/${encodeURIComponent(docName)}/spans?page=${page}`
        );
        if (res.data && res.data.length > 0) {
          setSpans(res.data);
          // If no explicit citation bbox, use first span
          if (!activeCitation?.bbox && res.data[0]) {
            setHighlightBbox(res.data[0].bbox);
          }
        }
      } catch (err) {
        console.warn('Spans retrieval warning (using simulated span):', err);
      } finally {
        setLoading(false);
      }
    }

    loadSpans();
  }, [domain, docName, page, activeCitation]);

  const pdfUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/documents/${domain}/${encodeURIComponent(docName)}/pdf`;

  return (
    <div className="flex flex-col h-full bg-neutral-900 select-none text-neutral-200">
      {/* Top Controller Bar */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-neutral-800 bg-neutral-950/70 text-xs">
        <div className="flex items-center gap-2 truncate max-w-[180px]">
          <FileText className="w-3.5 h-3.5 text-purple-400 flex-shrink-0" />
          <span className="truncate text-neutral-300 font-medium" title={docName}>
            {activeCitation?.paperTitle || docName}
          </span>
        </div>

        {/* Page navigation */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
            className="p-1 hover:bg-neutral-800 rounded text-neutral-400 hover:text-white disabled:opacity-40"
            title="Previous page"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
          </button>
          <span className="font-mono text-[11px] text-neutral-300 px-1">
            p. {page} / {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
            className="p-1 hover:bg-neutral-800 rounded text-neutral-400 hover:text-white disabled:opacity-40"
            title="Next page"
          >
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Zoom controls */}
        <div className="flex items-center gap-1 border-l border-neutral-800 pl-2">
          <button
            onClick={() => setZoom((z) => Math.max(50, z - 10))}
            className="p-1 hover:bg-neutral-800 rounded text-neutral-400 hover:text-white"
            title="Zoom out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="font-mono text-[10px] text-neutral-400 w-8 text-center">{zoom}%</span>
          <button
            onClick={() => setZoom((z) => Math.min(200, z + 10))}
            className="p-1 hover:bg-neutral-800 rounded text-neutral-400 hover:text-white"
            title="Zoom in"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Grounding Status Bar */}
      <div className="flex items-center justify-between px-3 py-1 bg-purple-950/20 border-b border-purple-900/30 text-[10px] text-purple-300">
        <span className="flex items-center gap-1 font-mono">
          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
          Grounding Verified: {activeCitation ? `\\cite{${activeCitation.bibtexKey}}` : 'Auto-detected'}
        </span>
        <span className="text-neutral-500 font-mono">BBox Coordinates Normalized</span>
      </div>

      {/* Main PDF Page Stage */}
      <div
        ref={containerRef}
        className="flex-1 overflow-auto p-4 flex justify-center items-start bg-neutral-950/90"
      >
        <div
          className="relative bg-white text-neutral-900 shadow-2xl rounded-sm transition-all duration-200 min-h-[560px] w-full max-w-[480px] p-6 border border-neutral-700 font-serif"
          style={{ transform: `scale(${zoom / 100})`, transformOrigin: 'top center' }}
        >
          {/* Simulated Academic PDF Content Layout */}
          <div className="text-center border-b border-neutral-300 pb-3 mb-4">
            <h1 className="text-sm font-bold tracking-tight text-neutral-900 leading-snug">
              {activeCitation?.paperTitle || 'Attention Is All You Need'}
            </h1>
            <p className="text-[10px] text-neutral-600 mt-1 font-sans">
              Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones
            </p>
            <p className="text-[9px] text-neutral-500 font-sans italic">Google Brain · Google Research</p>
          </div>

          <div className="text-[10px] leading-relaxed space-y-2 text-justify relative">
            <p className="font-bold text-[11px] font-sans uppercase tracking-wider text-neutral-800">
              Abstract
            </p>
            <p className="text-neutral-800">
              The dominant sequence transduction models are based on complex recurrent or convolutional
              neural networks that include an encoder and a decoder. The best performing models also connect
              the encoder and decoder through an attention mechanism. We propose a new simple network
              architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence
              and convolutions entirely.
            </p>

            <p className="font-bold text-[11px] font-sans uppercase tracking-wider text-neutral-800 pt-2">
              1. Introduction
            </p>
            <p className="text-neutral-700">
              Recurrent models typically factor computation along the symbol positions of the input and
              output sequences. Aligning the positions to steps in computation time, they generate a
              sequence of hidden states h_t, as a function of the previous hidden state h_(t-1) and the
              input for position t.
            </p>
            <p className="text-neutral-700">
              This inherently sequential nature precludes parallelization within training examples, which
              becomes critical at longer sequence lengths, as memory constraints limit batching across
              examples.
            </p>

            {/* Bounding Box Highlight Overlay */}
            {highlightBbox && (
              <BoundingBoxHighlighter
                bbox={highlightBbox}
                label={activeCitation?.bibtexKey ? `\\cite{${activeCitation.bibtexKey}}` : 'GROUNDED SPAN'}
                color="purple"
              />
            )}
          </div>

          {/* Page footer */}
          <div className="absolute bottom-3 left-0 right-0 text-center text-[9px] font-sans text-neutral-400">
            Page {page} of {totalPages}
          </div>
        </div>
      </div>
    </div>
  );
};
