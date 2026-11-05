import { useEffect, useRef } from 'react';
import { apiUpdateSection } from '@/services/api';
import { useStudioStore } from '@/lib/studioStore';

export function useAutoSave(
  projectId: string | null | undefined,
  sectionId: string | null | undefined,
  content: string,
  delay: number = 2000
) {
  const { setSaving, setLastSaved, setSaveError, updateSectionContent } = useStudioStore();
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const lastSavedContentRef = useRef<string>(content);

  useEffect(() => {
    // If not valid project or section, or content hasn't changed from last saved, skip
    if (!projectId || !sectionId || content === lastSavedContentRef.current) {
      return;
    }

    // Clear existing timer
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    setSaving(true);

    timerRef.current = setTimeout(async () => {
      try {
        await apiUpdateSection(projectId, sectionId, { content_markdown: content });
        lastSavedContentRef.current = content;
        updateSectionContent(sectionId, content);
        setSaving(false);
        setLastSaved(new Date().toLocaleTimeString());
      } catch (err: unknown) {
        console.error('Auto-save failed:', err);
        setSaving(false);
        const errorMessage = err instanceof Error ? err.message : 'Auto-save failed';
        setSaveError(errorMessage);
      }
    }, delay);

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [content, projectId, sectionId, delay, setSaving, setLastSaved, setSaveError, updateSectionContent]);

  // Provide manual save immediately
  const saveNow = async () => {
    if (!projectId || !sectionId || content === lastSavedContentRef.current) return;
    if (timerRef.current) clearTimeout(timerRef.current);
    setSaving(true);
    try {
      await apiUpdateSection(projectId, sectionId, { content_markdown: content });
      lastSavedContentRef.current = content;
      updateSectionContent(sectionId, content);
      setSaving(false);
      setLastSaved(new Date().toLocaleTimeString());
    } catch (err: unknown) {
      console.error('Manual save failed:', err);
      setSaving(false);
      const errorMessage = err instanceof Error ? err.message : 'Save failed';
      setSaveError(errorMessage);
    }
  };

  return { saveNow };
}

