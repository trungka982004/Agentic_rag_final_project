'use client';

import React, { useState } from 'react';
import { useStudioStore } from '@/lib/studioStore';
import {
  Download,
  FileText,
  Archive,
  BookOpen,
  X,
  Check,
  Loader2,
  ExternalLink,
  Sparkles
} from 'lucide-react';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ExportModal: React.FC<ExportModalProps> = ({ isOpen, onClose }) => {
  const { currentProject } = useStudioStore();
  const [downloadingType, setDownloadingType] = useState<string | null>(null);

  if (!isOpen) return null;

  const projectId = currentProject?.id || 'demo-proj-001';
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

  const handleDownloadPdf = async () => {
    try {
      setDownloadingType('pdf');
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : '';
      const response = await fetch(`${baseUrl}/api/projects/${projectId}/compile`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) throw new Error('Compilation failed');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `paper_${projectId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('PDF download error:', err);
      alert('Could not compile PDF preprint. Check backend connection.');
    } finally {
      setDownloadingType(null);
    }
  };

  const handleDownloadOverleaf = () => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : '';
    window.open(`${baseUrl}/api/projects/${projectId}/export/overleaf`, '_blank');
  };

  const handleDownloadBibtex = () => {
    window.open(`${baseUrl}/api/projects/${projectId}/export/bibtex`, '_blank');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-neutral-900 border border-neutral-800 rounded-2xl w-full max-w-md shadow-2xl overflow-hidden text-neutral-200">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-neutral-800 bg-neutral-950/60">
          <div className="flex items-center gap-2">
            <span className="p-1 rounded bg-purple-600/20 text-purple-400 border border-purple-500/30">
              <Download className="w-4 h-4" />
            </span>
            <h3 className="text-sm font-semibold text-white">Export & Compile Paper</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-neutral-800 rounded-lg text-neutral-400 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Export Options */}
        <div className="p-6 space-y-3">
          <button
            onClick={handleDownloadPdf}
            disabled={downloadingType === 'pdf'}
            className="w-full flex items-center gap-3 p-3.5 rounded-xl bg-purple-600/10 hover:bg-purple-600/20 border border-purple-500/30 text-left transition-colors group"
          >
            <div className="p-2 rounded-lg bg-purple-600 text-white">
              {downloadingType === 'pdf' ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <FileText className="w-5 h-5" />
              )}
            </div>
            <div className="flex-1">
              <div className="text-xs font-semibold text-white group-hover:text-purple-300 transition-colors">
                Compile Camera-Ready PDF
              </div>
              <div className="text-[11px] text-neutral-400">
                In-app autonomous compilation with two-column layout & citations
              </div>
            </div>
          </button>

          <button
            onClick={handleDownloadOverleaf}
            className="w-full flex items-center gap-3 p-3.5 rounded-xl bg-neutral-950/80 hover:bg-neutral-800 border border-neutral-800 text-left transition-colors group"
          >
            <div className="p-2 rounded-lg bg-emerald-600 text-white">
              <Archive className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <div className="text-xs font-semibold text-white group-hover:text-emerald-300 transition-colors">
                Overleaf Project Bundle (.ZIP)
              </div>
              <div className="text-[11px] text-neutral-400">
                Includes main.tex, references.bib, and IEEEtran conference styles
              </div>
            </div>
          </button>

          <button
            onClick={handleDownloadBibtex}
            className="w-full flex items-center gap-3 p-3.5 rounded-xl bg-neutral-950/80 hover:bg-neutral-800 border border-neutral-800 text-left transition-colors group"
          >
            <div className="p-2 rounded-lg bg-amber-600 text-white">
              <BookOpen className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <div className="text-xs font-semibold text-white group-hover:text-amber-300 transition-colors">
                BibTeX Bibliography (.bib)
              </div>
              <div className="text-[11px] text-neutral-400">
                Clean bibliography file with all validated paper references
              </div>
            </div>
          </button>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-neutral-950/60 border-t border-neutral-800 flex items-center justify-between text-[11px] text-neutral-500">
          <span>Zero external third-party dependencies required</span>
          <button
            onClick={onClose}
            className="px-3 py-1 rounded bg-neutral-800 hover:bg-neutral-700 text-neutral-300 font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

