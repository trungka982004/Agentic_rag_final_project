'use client';

import React, { useEffect, useState } from 'react';
import { useStudioStore } from '@/lib/studioStore';
import { apiListProjects, apiCreateProject, apiGetProject } from '@/services/api';
import { ProjectSidebar } from '@/components/studio/Zone1_Outline/ProjectSidebar';
import { AcademicEditor } from '@/components/studio/Zone2_Canvas/AcademicEditor';
import { Zone3Pane } from '@/components/studio/Zone3_Verifier/Zone3Pane';
import { Loader2, Sparkles, BookOpen, Download, PanelsTopLeft } from 'lucide-react';
import Link from 'next/link';

export default function StudioPage() {
  const { currentProject, setProject } = useStudioStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function initProject() {
      try {
        setLoading(true);
        const projects = await apiListProjects();
        if (projects && projects.length > 0) {
          const full = await apiGetProject(projects[0].id);
          setProject(full);
        } else {
          // Initialize a starter paper project
          const created = await apiCreateProject({
            title: 'Empirical Evaluation of Tri-Tier Agentic RAG for Scientific Discovery',
            template_type: 'ieee_conference',
            target_venue: 'IEEE Transactions on Software Engineering',
            primary_domain: 'it',
            abstract_text: 'Recent advances in retrieval-augmented generation have enabled AI agents to autonomously query multi-domain corpora...',
            keywords: ['Agentic RAG', 'Retrieval-Augmented Generation', 'Academic Writing', 'Verification'],
          });
          const full = await apiGetProject(created.id);
          setProject(full);
        }
      } catch (err) {
        console.warn('Backend not ready or auth required, creating local mock project:', err);
        // Fallback local mock to guarantee UI runs even in preview/unauthenticated state
        setProject({
          id: 'demo-proj-001',
          user_id: 'user-001',
          title: 'Empirical Evaluation of Tri-Tier Agentic RAG for Scientific Discovery',
          template_type: 'ieee_conference',
          target_venue: 'IEEE Transactions on Software Engineering',
          primary_domain: 'it',
          keywords: ['Agentic RAG', 'Empirical Study'],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          sections: [
            {
              id: 'sec-1',
              project_id: 'demo-proj-001',
              title: 'Abstract',
              slug: 'abstract',
              order_index: 0,
              content_markdown: '## Abstract\n\nRetrieval-Augmented Generation (RAG) paradigms frequently struggle with grounded multi-tier retrieval when operating over vast academic corpora. In this paper, we present an end-to-end tri-tier Agentic RAG architecture that unites deterministic vector similarity, BM25 keyword matching, and iterative agent self-correction. Through extensive benchmarking over 618 computer science, medicine, and economics papers, our approach achieves 94.8% retrieval precision and decreases citation hallucination to under 2.1%.',
              word_count: 73,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            },
            {
              id: 'sec-2',
              project_id: 'demo-proj-001',
              title: '1. Introduction',
              slug: 'introduction',
              order_index: 1,
              content_markdown: '## 1. Introduction\n\nWriting peer-reviewed literature demands stringent factual grounding, accurate bibliographical indexing, and rigorous mathematical formulations. Traditional LLM-based writing assistants routinely hallucinate references and lack spatial page grounding.\n\nAs established by \\cite{vaswani2017attention}, self-attention mechanisms allow cross-modal representation. However, spatial text extraction using PyMuPDF and bounding-box validation is critical for reproducible academic work.',
              word_count: 52,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            },
            {
              id: 'sec-3',
              project_id: 'demo-proj-001',
              title: '2. Related Work',
              slug: 'related-work',
              order_index: 2,
              content_markdown: '## 2. Related Work\n\nDense passage retrieval and hybrid BM25 architectures have been explored extensively in prior literature \\cite{karpukhin2020dense}. Nonetheless, existing systems fail to maintain interactive bounding box coordinates across split-screen editing canvases.',
              word_count: 31,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            },
            {
              id: 'sec-4',
              project_id: 'demo-proj-001',
              title: '3. Methodology',
              slug: 'methodology',
              order_index: 3,
              content_markdown: '## 3. Methodology\n\nLet $\\mathcal{D} = \\{d_1, d_2, \\dots, d_N\\}$ be the indexed repository of 618 academic manuscripts. The objective function combines dense embedding similarity and lexical BM25 scores:\n\n$$\n\\mathcal{S}(q, d) = \\lambda \\cdot \\text{Sim}_{\\text{dense}}(q, d) + (1 - \\lambda) \\cdot \\text{Score}_{\\text{BM25}}(q, d)\n$$\n\nwhere $\\lambda \\in [0, 1]$ represents the balancing parameter.',
              word_count: 48,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            },
            {
              id: 'sec-5',
              project_id: 'demo-proj-001',
              title: '4. Experiments and Results',
              slug: 'experiments',
              order_index: 4,
              content_markdown: '## 4. Experiments and Results\n\nWe benchmark our architecture against state-of-the-art baselines across 618 multi-domain PDFs.\n\n| Model Architecture | Precision (%) | Recall (%) | F1-Score | Latency (ms) |\n| :--- | :---: | :---: | :---: | :---: |\n| Standard Chatbot | 78.4 | 74.2 | 76.2 | 1250 |\n| Tri-Tier Agentic RAG | **94.8** | **92.3** | **93.5** | **420** |\n\nEmpirical latency analysis demonstrates that pickle disk caching reduces retriever startup from 17.2s to 0.86s.',
              word_count: 62,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            },
            {
              id: 'sec-6',
              project_id: 'demo-proj-001',
              title: '5. Conclusion',
              slug: 'conclusion',
              order_index: 5,
              content_markdown: '## 5. Conclusion\n\nIn this study, we demonstrated the design and realization of an All-in-One Academic Studio IDE. By harmonizing WYSIWYG canvas editing with split-screen PDF bounding-box verification, researchers can author verifiable papers with minimal friction.',
              word_count: 36,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            },
          ],
          references: [
            {
              id: 'ref-1',
              project_id: 'demo-proj-001',
              bibtex_key: 'vaswani2017attention',
              title: 'Attention Is All You Need',
              authors: 'Vaswani et al.',
              year: 2017,
              venue: 'NeurIPS',
              bibtex_raw: '@article{vaswani2017attention, title={Attention Is All You Need}, author={Vaswani, Ashish and others}, journal={NeurIPS}, year={2017}}',
              created_at: new Date().toISOString(),
            },
            {
              id: 'ref-2',
              project_id: 'demo-proj-001',
              bibtex_key: 'karpukhin2020dense',
              title: 'Dense Passage Retrieval for Open-Domain Question Answering',
              authors: 'Karpukhin et al.',
              year: 2020,
              venue: 'EMNLP',
              bibtex_raw: '@inproceedings{karpukhin2020dense, title={Dense Passage Retrieval for Open-Domain Question Answering}, author={Karpukhin, Vladimir and others}, booktitle={EMNLP}, year={2020}}',
              created_at: new Date().toISOString(),
            },
          ],
        });
      } finally {
        setLoading(false);
      }
    }

    initProject();
  }, [setProject]);

  if (loading) {
    return (
      <div className="h-screen w-screen flex flex-col items-center justify-center bg-neutral-950 text-neutral-300">
        <Loader2 className="w-8 h-8 animate-spin text-purple-400 mb-3" />
        <p className="text-sm font-medium">Loading Academic Studio Workspace...</p>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen flex flex-col bg-neutral-950 overflow-hidden font-sans">
      {/* Studio Global Navigation Bar */}
      <header className="h-12 bg-neutral-900 border-b border-neutral-800 flex items-center justify-between px-4 z-20 flex-shrink-0">
        <div className="flex items-center gap-3">
          <Link href="/chat" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <span className="font-bold text-sm tracking-tight text-white flex items-center gap-1.5">
              <span className="p-1 rounded bg-purple-600/20 text-purple-400 border border-purple-500/30">
                <PanelsTopLeft className="w-4 h-4" />
              </span>
              SciStudio <span className="text-[10px] uppercase text-purple-400 font-mono px-1 rounded bg-purple-500/10 border border-purple-500/20">v2.0 IDE</span>
            </span>
          </Link>
          <div className="w-[1px] h-4 bg-neutral-800" />
          <div className="text-xs text-neutral-400 truncate max-w-sm font-medium">
            {currentProject?.title}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Link
            href="/chat"
            className="text-xs text-neutral-400 hover:text-white px-2.5 py-1 rounded-md hover:bg-neutral-800 transition-colors"
          >
            Chat View
          </Link>
          <button
            onClick={() => alert('PDF / LaTeX export compilation is configured in Phase 5!')}
            className="flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium bg-purple-600 hover:bg-purple-500 text-white transition-colors shadow-sm"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Paper</span>
          </button>
        </div>
      </header>

      {/* 3-Zone Academic Studio Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Zone 1: Outline Tree */}
        <ProjectSidebar />

        {/* Zone 2: WYSIWYG Academic Canvas */}
        <main className="flex-1 h-full overflow-hidden">
          <AcademicEditor />
        </main>

        {/* Zone 3: Grounded PDF Verifier & AI Copilot */}
        <Zone3Pane />
      </div>
    </div>
  );
}
