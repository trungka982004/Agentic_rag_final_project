'use client';

import React, { useState } from 'react';
import { useStudioStore } from '@/lib/studioStore';
import { apiCreateSection } from '@/services/api';
import {
  FileText,
  Plus,
  BookOpen,
  ChevronRight,
  FolderOpen,
  Settings,
  Layers,
  GraduationCap
} from 'lucide-react';

export const ProjectSidebar: React.FC = () => {
  const {
    currentProject,
    sections,
    activeSectionId,
    setActiveSectionId,
    references,
    setZone3View,
    zone1Width,
  } = useStudioStore();

  const [newSectionTitle, setNewSectionTitle] = useState('');
  const [isAddingSection, setIsAddingSection] = useState(false);

  const handleAddSection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSectionTitle.trim() || !currentProject) return;

    try {
      const order = sections.length;
      const res = await apiCreateSection(currentProject.id, {
        title: newSectionTitle.trim(),
        order_index: order,
        content_markdown: `## ${newSectionTitle.trim()}\n\nWrite content here...`,
      });
      // In practice, store will be refreshed or we update directly
      setActiveSectionId(res.id);
      setNewSectionTitle('');
      setIsAddingSection(false);
    } catch (err) {
      console.error('Failed to create section:', err);
    }
  };

  const totalWords = sections.reduce((acc, s) => acc + (s.word_count || 0), 0);

  return (
    <aside className="h-full bg-neutral-900 border-r border-neutral-800 flex flex-col select-none text-neutral-300 flex-shrink-0" style={{ width: `${zone1Width}px` }}>
      {/* Project Title Header */}
      <div className="p-4 border-b border-neutral-800">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-purple-400 mb-1">
          <GraduationCap className="w-4 h-4" />
          <span>Academic Studio</span>
        </div>
        <h1 className="text-sm font-semibold text-white truncate" title={currentProject?.title}>
          {currentProject?.title || 'Untitled Academic Paper'}
        </h1>
        <div className="flex items-center gap-2 mt-2">
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-neutral-800 text-neutral-400 border border-neutral-700 font-mono">
            {currentProject?.template_type || 'IEEE Conf'}
          </span>
          <span className="text-[10px] text-neutral-500 font-mono">
            {totalWords.toLocaleString()} total words
          </span>
        </div>
      </div>

      {/* Sections Outline */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        <div className="flex items-center justify-between px-2 mb-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-neutral-400">
            Paper Sections
          </span>
          <button
            onClick={() => setIsAddingSection(true)}
            className="p-1 hover:bg-neutral-800 rounded text-neutral-400 hover:text-white transition-colors"
            title="Add new section"
          >
            <Plus className="w-3.5 h-3.5" />
          </button>
        </div>

        {sections.map((section, idx) => {
          const isActive = section.id === activeSectionId;
          return (
            <button
              key={section.id}
              onClick={() => setActiveSectionId(section.id)}
              className={`w-full flex items-center justify-between px-2.5 py-2 rounded-lg text-xs font-medium transition-colors text-left group ${
                isActive
                  ? 'bg-purple-600/20 text-purple-200 border border-purple-500/30'
                  : 'hover:bg-neutral-800/70 text-neutral-400 hover:text-neutral-200'
              }`}
            >
              <div className="flex items-center gap-2 truncate">
                <FileText className={`w-3.5 h-3.5 flex-shrink-0 ${isActive ? 'text-purple-400' : 'text-neutral-500'}`} />
                <span className="truncate">{section.title}</span>
              </div>
              <span className="text-[10px] font-mono text-neutral-500 group-hover:text-neutral-400 ml-1">
                {section.word_count || 0}w
              </span>
            </button>
          );
        })}

        {isAddingSection && (
          <form onSubmit={handleAddSection} className="mt-2 p-1.5 bg-neutral-800/80 rounded-lg border border-neutral-700">
            <input
              type="text"
              value={newSectionTitle}
              onChange={(e) => setNewSectionTitle(e.target.value)}
              placeholder="e.g., 5. Discussion"
              className="w-full bg-neutral-900 text-xs px-2 py-1.5 rounded text-white border border-neutral-700 focus:outline-none focus:border-purple-500"
              autoFocus
            />
            <div className="flex justify-end gap-1 mt-1.5">
              <button
                type="button"
                onClick={() => setIsAddingSection(false)}
                className="px-2 py-0.5 text-[10px] text-neutral-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-2.5 py-0.5 text-[10px] bg-purple-600 hover:bg-purple-500 text-white rounded font-medium"
              >
                Add
              </button>
            </div>
          </form>
        )}
      </div>

      {/* Bibliography & References Tab Button */}
      <div className="p-3 border-t border-neutral-800 space-y-1">
        <button
          onClick={() => setZone3View('references')}
          className="w-full flex items-center justify-between px-2.5 py-2 rounded-lg text-xs font-medium text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors"
        >
          <div className="flex items-center gap-2">
            <BookOpen className="w-3.5 h-3.5 text-amber-400" />
            <span>Bibliography ({references.length})</span>
          </div>
          <ChevronRight className="w-3.5 h-3.5 text-neutral-600" />
        </button>
      </div>
    </aside>
  );
};
