import { create } from 'zustand';
import { Project, PaperSection, ProjectReference, ActiveCitation } from '@/types';

interface StudioState {
  // Active Project & Sections
  currentProject: Project | null;
  activeSectionId: string | null;
  sections: PaperSection[];
  references: ProjectReference[];

  // Auto-save & Status
  isSaving: boolean;
  lastSavedAt: string | null;
  saveError: string | null;

  // Active Citation & Grounding
  activeCitation: ActiveCitation | null;

  // Split-Screen Layout & Resizable Panel Widths
  zone3View: 'verifier' | 'copilot' | 'references';
  isZone3Open: boolean;
  zone1Width: number;
  zone3Width: number;

  // Actions
  setProject: (project: Project) => void;
  setActiveSectionId: (sectionId: string) => void;
  updateSectionContent: (sectionId: string, markdown: string) => void;
  setSaving: (saving: boolean) => void;
  setLastSaved: (timestamp: string) => void;
  setSaveError: (error: string | null) => void;
  setActiveCitation: (citation: ActiveCitation | null) => void;
  setZone3View: (view: 'verifier' | 'copilot' | 'references') => void;
  toggleZone3: (open?: boolean) => void;
  setZone1Width: (width: number) => void;
  setZone3Width: (width: number) => void;
  addReference: (ref: ProjectReference) => void;
}

export const useStudioStore = create<StudioState>((set) => ({
  currentProject: null,
  activeSectionId: null,
  sections: [],
  references: [],

  isSaving: false,
  lastSavedAt: null,
  saveError: null,

  activeCitation: null,
  zone3View: 'verifier',
  isZone3Open: true,
  zone1Width: 260,
  zone3Width: 460,

  setProject: (project) => {
    const sortedSections = project.sections
      ? [...project.sections].sort((a, b) => a.order_index - b.order_index)
      : [];
    set({
      currentProject: project,
      sections: sortedSections,
      references: project.references || [],
      activeSectionId: sortedSections.length > 0 ? sortedSections[0].id : null,
    });
  },

  setActiveSectionId: (sectionId) => set({ activeSectionId: sectionId }),

  updateSectionContent: (sectionId, markdown) => {
    set((state) => ({
      sections: state.sections.map((sec) =>
        sec.id === sectionId
          ? {
              ...sec,
              content_markdown: markdown,
              word_count: markdown.trim().split(/\s+/).filter(Boolean).length,
              updated_at: new Date().toISOString(),
            }
          : sec
      ),
    }));
  },

  setSaving: (saving) => set({ isSaving: saving }),
  setLastSaved: (timestamp) => set({ lastSavedAt: timestamp, saveError: null }),
  setSaveError: (error) => set({ saveError: error }),

  setActiveCitation: (citation) => {
    set({
      activeCitation: citation,
      isZone3Open: true,
      zone3View: 'verifier',
    });
  },

  setZone3View: (view) => set({ zone3View: view, isZone3Open: true }),
  toggleZone3: (open) =>
    set((state) => ({
      isZone3Open: open !== undefined ? open : !state.isZone3Open,
    })),

  setZone1Width: (width) => set({ zone1Width: Math.max(200, Math.min(420, width)) }),
  setZone3Width: (width) => set({ zone3Width: Math.max(340, Math.min(700, width)) }),

  addReference: (ref) =>
    set((state) => ({
      references: [...state.references, ref],
    })),
}));
