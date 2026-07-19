'use client';

import { useState, useEffect } from 'react';
import { 
  apiListDocuments, 
  apiUploadDocument, 
  apiDeleteDocumentsBulk, 
  apiReassignDocument,
  type DocumentInfo 
} from '@/services/api';

const AI_STATUS = {
  done:     { label: 'Analyzed', bg: 'var(--success-container)', color: 'var(--success)' },
  indexing: { label: 'Analyzing...', bg: 'var(--warning-container)', color: 'var(--warning)' },
  pending:  { label: 'Pending analysis', bg: 'var(--surface-container)', color: 'var(--on-surface-variant)' },
};

const DOMAINS = [
  { id: 'it', label: 'CS', icon: 'CodeIcon', desc: 'Computer Science & IT' },
  { id: 'math', label: 'Mathematics', icon: 'CalculatorIcon', desc: 'Theoretical & Applied Mathematics' },
  { id: 'physics', label: 'Physics', icon: 'AtomIcon', desc: 'Physics & High Energy' },
  { id: 'electronics', label: 'Electronics', icon: 'CpuIcon', desc: 'Electronics & Microcircuits' },
];

// Custom SVGs for modern design
const CodeIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="16 18 22 12 16 6" />
    <polyline points="8 6 2 12 8 18" />
  </svg>
);

const CalculatorIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="4" y="2" width="16" height="20" rx="2" ry="2" />
    <line x1="9" y1="22" x2="9" y2="16" />
    <line x1="8" y1="6" x2="16" y2="6" />
    <circle cx="16" cy="14" r="1.5" fill="currentColor" />
    <circle cx="12" cy="14" r="1.5" fill="currentColor" />
    <circle cx="8" cy="14" r="1.5" fill="currentColor" />
    <circle cx="16" cy="18" r="1.5" fill="currentColor" />
    <circle cx="12" cy="18" r="1.5" fill="currentColor" />
    <circle cx="8" cy="18" r="1.5" fill="currentColor" />
    <line x1="12" y1="10" x2="16" y2="10" />
    <circle cx="8" cy="10" r="1.5" fill="currentColor" />
  </svg>
);

const AtomIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <ellipse cx="12" cy="12" rx="3" ry="9" transform="rotate(45 12 12)" />
    <ellipse cx="12" cy="12" rx="3" ry="9" transform="rotate(-45 12 12)" />
    <circle cx="12" cy="12" r="2" fill="currentColor" />
  </svg>
);

const CpuIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="4" y="4" width="16" height="16" rx="2" />
    <rect x="9" y="9" width="6" height="6" />
    <line x1="9" y1="1" x2="9" y2="4" />
    <line x1="15" y1="1" x2="15" y2="4" />
    <line x1="9" y1="20" x2="9" y2="23" />
    <line x1="15" y1="20" x2="15" y2="23" />
    <line x1="20" y1="9" x2="23" y2="9" />
    <line x1="20" y1="15" x2="23" y2="15" />
    <line x1="1" y1="9" x2="4" y2="9" />
    <line x1="1" y1="15" x2="4" y2="15" />
  </svg>
);

const BookOpenIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
  </svg>
);

const CloudUploadIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="17 8 12 3 7 8" />
    <line x1="12" y1="3" x2="12" y2="15" />
  </svg>
);

const TrashIcon = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="3 6 5 6 21 6" />
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
    <line x1="10" y1="11" x2="10" y2="17" />
    <line x1="14" y1="11" x2="14" y2="17" />
  </svg>
);

const EyeIcon = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
    <circle cx="12" cy="12" r="3"></circle>
  </svg>
);

interface CustomDomain {
  id: string;
  label: string;
  icon: string;
  desc: string;
}

export default function DocumentLibraryPage() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [search, setSearch] = useState('');
  const [selectedDomain, setSelectedDomain] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('active_domain') || 'it';
    }
    return 'it';
  });
  const [filterDomain, setFilterDomain] = useState('all');
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  
  // Custom domains added dynamically by the user
  const [customDomains, setCustomDomains] = useState<CustomDomain[]>([]);
  const [newDomainName, setNewDomainName] = useState('');

  // Selected checkboxes for batch delete
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  
  // Drag & drop state
  const [isDragging, setIsDragging] = useState(false);
  // Upload status queue
  const [uploadQueue, setUploadQueue] = useState<{ name: string; size: string; status: 'uploading' | 'success' | 'error'; error?: string }[]>([]);

  // Drag and Drop active states for target subject cards
  const [dragOverDomain, setDragOverDomain] = useState<string | null>(null);

  // Custom Deletion Confirmation Modal state
  const [deleteModal, setDeleteModal] = useState<{
    isOpen: boolean;
    type: 'single' | 'bulk';
    docId?: string;
    filename?: string;
  }>({
    isOpen: false,
    type: 'single',
  });

  // Simulated PDF Viewer Modal
  const [viewModal, setViewModal] = useState<{
    isOpen: boolean;
    docName?: string;
  }>({
    isOpen: false,
  });

  // Sync selectedDomain to localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('active_domain', selectedDomain);
    }
  }, [selectedDomain]);

  // Load custom domains from localStorage on initial render
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('custom_domains');
      if (saved) {
        setCustomDomains(JSON.parse(saved));
      }
    }
  }, []);

  const fetchDocs = async () => {
    try {
      setLoading(true);
      const data = await apiListDocuments();
      setDocuments(data);
      
      // Auto-discover domains present in documents but missing from local categories
      const detectedCustoms: CustomDomain[] = [];
      data.forEach(doc => {
        const domainId = doc.author.toLowerCase();
        const isDefault = DOMAINS.some(d => d.id === domainId);
        const isAlreadyCustom = customDomains.some(d => d.id === domainId) || detectedCustoms.some(d => d.id === domainId);
        
        if (!isDefault && !isAlreadyCustom) {
          const rawLabel = doc.author;
          let label = rawLabel.charAt(0) + rawLabel.slice(1).toLowerCase();
          label = label.replace(/_/g, ' ');
          detectedCustoms.push({
            id: domainId,
            label,
            icon: 'BookOpenIcon',
            desc: `Custom Category: ${label}`,
          });
        }
      });
      
      if (detectedCustoms.length > 0) {
        setCustomDomains(prev => {
          const combined = [...prev];
          detectedCustoms.forEach(dc => {
            if (!combined.some(c => c.id === dc.id)) {
              combined.push(dc);
            }
          });
          if (typeof window !== 'undefined') {
            localStorage.setItem('custom_domains', JSON.stringify(combined));
          }
          return combined;
        });
      }

      setError(null);
    } catch (err: any) {
      console.error(err);
      setError('Failed to load documents list.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
    window.addEventListener('document-uploaded', fetchDocs);
    return () => {
      window.removeEventListener('document-uploaded', fetchDocs);
    };
  }, []);

  // Simulate snippet flow from Settings
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const action = params.get('action');
      const highlightDoc = params.get('highlight_doc');

      if (action === 'add_snippet') {
        setSuccessMsg('New snippet mode: Drag and select any text in the PDF to save it as a snippet.');
        window.history.replaceState({}, document.title, window.location.pathname);
      } else if (highlightDoc) {
        setSuccessMsg(`Showing full context for document "${highlightDoc}". Snippets have been highlighted.`);
        setSearch(highlightDoc.replace('.pdf', '')); // Filter list for simulated context
        window.history.replaceState({}, document.title, window.location.pathname);
      }
    }
  }, []);

  // Clear checkboxes when filters or search change
  useEffect(() => {
    setSelectedDocIds([]);
  }, [filterDomain, search]);

  const slugify = (text: string) => {
    return text
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[đĐ]/g, 'd')
      .replace(/[^a-z0-9\s-]/g, '')
      .trim()
      .replace(/\s+/g, '_');
  };

  const handleAddDomain = () => {
    if (!newDomainName.trim()) return;
    const id = slugify(newDomainName);
    
    if (DOMAINS.some(d => d.id === id) || customDomains.some(d => d.id === id)) {
      alert('This category already exists!');
      return;
    }
    
    const newDomain: CustomDomain = {
      id,
      label: newDomainName.trim(),
      icon: 'BookOpenIcon',
      desc: `Custom Category: ${newDomainName.trim()}`,
    };
    
    const updated = [...customDomains, newDomain];
    setCustomDomains(updated);
    if (typeof window !== 'undefined') {
      localStorage.setItem('custom_domains', JSON.stringify(updated));
    }
    setSelectedDomain(id);
    setNewDomainName('');
  };

  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    setError(null);
    setSuccessMsg(null);

    const newQueue = Array.from(files).map(file => ({
      name: file.name,
      size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
      status: 'uploading' as const
    }));
    setUploadQueue(newQueue);

    try {
      let successCount = 0;
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (!file.name.endsWith('.pdf')) {
          setUploadQueue(prev => prev.map((item, idx) => idx === i ? { ...item, status: 'error', error: 'Only PDF is supported' } : item));
          continue;
        }
        
        try {
          await apiUploadDocument(file, selectedDomain);
          setUploadQueue(prev => prev.map((item, idx) => idx === i ? { ...item, status: 'success' } : item));
          successCount++;
        } catch (err: any) {
          console.error(err);
          setUploadQueue(prev => prev.map((item, idx) => idx === i ? { ...item, status: 'error', error: 'Server error' } : item));
        }
      }
      
      if (successCount > 0) {
        setSuccessMsg(`Successfully uploaded ${successCount} documents! AI is analyzing new documents in the background.`);
        fetchDocs();
      } else {
        setError('Failed to upload document.');
      }
    } catch (err: any) {
      console.error(err);
      setError('Failed to upload document.');
    } finally {
      setUploading(false);
      setTimeout(() => {
        setSuccessMsg(null);
        setUploadQueue([]);
      }, 6000);
    }
  };

  const handleSingleDelete = (docId: string, filename: string) => {
    setDeleteModal({
      isOpen: true,
      type: 'single',
      docId,
      filename,
    });
  };

  const handleBulkDelete = () => {
    if (selectedDocIds.length === 0) return;
    setDeleteModal({
      isOpen: true,
      type: 'bulk',
    });
  };

  const handleConfirmDelete = async () => {
    const { type, docId, filename } = deleteModal;
    setDeleteModal(prev => ({ ...prev, isOpen: false }));
    
    try {
      setLoading(true);
      setError(null);
      setSuccessMsg(null);
      if (type === 'single' && docId) {
        await apiDeleteDocumentsBulk([docId]);
        setSuccessMsg(`Document "${filename}" deleted successfully.`);
      } else if (type === 'bulk') {
        await apiDeleteDocumentsBulk(selectedDocIds);
        setSuccessMsg(`Deleted ${selectedDocIds.length} documents successfully.`);
        setSelectedDocIds([]);
      }
      await fetchDocs();
    } catch (err: any) {
      console.error(err);
      setError(type === 'single' ? 'Error deleting document.' : 'Error deleting documents in bulk.');
    } finally {
      setLoading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!uploading) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (uploading) return;

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      await handleFileUpload(files);
    }
  };

  // Combine default and custom domains for rendering
  const allDomains = [...DOMAINS, ...customDomains];

  // 1. Double filter by search text and by selected tab domain
  const filtered = documents.filter(d => {
    const matchesSearch = d.name.toLowerCase().includes(search.toLowerCase()) ||
                          d.author.toLowerCase().includes(search.toLowerCase());
    const matchesDomain = filterDomain === 'all' || d.author.toLowerCase() === filterDomain.toLowerCase();
    return matchesSearch && matchesDomain;
  });

  // 2. Default Sort logic: Newest Time (date) first, then Smallest Size (size_bytes) first
  const sortedAndFiltered = [...filtered].sort((a, b) => {
    const parseDate = (dStr: string) => {
      const parts = dStr.split('/');
      if (parts.length === 3) {
        return new Date(parseInt(parts[2]), parseInt(parts[1]) - 1, parseInt(parts[0])).getTime();
      }
      return 0;
    };
    const dateA = parseDate(a.date);
    const dateB = parseDate(b.date);
    if (dateB !== dateA) {
      return dateB - dateA; // newest first
    }
    // Smallest size first
    const sizeA = a.size_bytes ?? 0;
    const sizeB = b.size_bytes ?? 0;
    return sizeA - sizeB;
  });

  return (
    <div style={{ width: '100%', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 700, color: 'var(--on-surface)' }}>
          Document Library
        </h1>
        <p style={{ color: 'var(--on-surface-variant)', fontSize: '14px', marginTop: '4px' }}>
          Manage scientific research resources and configure knowledge bases for the RAG Workflow.
        </p>
      </div>

      {/* Notifications */}
      {error && (
        <div style={{
          padding: '12px 16px',
          background: 'var(--error-container)',
          color: 'var(--error)',
          borderRadius: 'var(--radius-md)',
          fontSize: '13.5px',
          marginBottom: '16px',
          fontFamily: 'var(--font-body)',
          border: '1px solid rgba(186, 26, 26, 0.2)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}>
          <span>⚠️</span> {error}
        </div>
      )}

      {successMsg && (
        <div style={{
          padding: '12px 16px',
          background: 'var(--success-container)',
          color: 'var(--success)',
          borderRadius: 'var(--radius-md)',
          fontSize: '13.5px',
          marginBottom: '16px',
          fontFamily: 'var(--font-body)',
          border: '1px solid rgba(27, 109, 58, 0.2)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}>
          <span>✅</span> {successMsg}
        </div>
      )}

      {/* 2 Large Columns Grid Layout */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '380px 1fr',
        gap: '28px',
        alignItems: 'start',
      }}>
        
        {/* LEFT COLUMN: Subject Selection + Upload Control */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '24px',
        }}>
          
          {/* Domain Selection Section */}
          <div style={{
            background: 'var(--surface-container-lowest)',
            border: '1px solid var(--outline-variant)',
            borderRadius: 'var(--radius-lg)',
            padding: '18px',
            boxShadow: 'var(--shadow-1)',
          }}>
            <h2 style={{ 
              fontFamily: 'var(--font-display)', 
              fontSize: '13.5px', 
              fontWeight: 600, 
              color: 'var(--on-surface)', 
              marginBottom: '14px',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              1. Select Category for Upload
            </h2>
            <div style={{ 
              display: 'flex',
              flexDirection: 'column', 
              gap: '10px',
              maxHeight: '340px',
              overflowY: 'auto',
              paddingRight: '4px'
            }}>
              {allDomains.map(domain => {
                const count = documents.filter(d => d.author.toLowerCase() === domain.id).length;
                const isActive = selectedDomain === domain.id;
                const isDragOver = dragOverDomain === domain.id;
                
                return (
                  <div
                    key={domain.id}
                    onClick={() => setSelectedDomain(domain.id)}
                    onDragOver={e => {
                      e.preventDefault();
                      if (!isActive) {
                        setDragOverDomain(domain.id);
                      }
                    }}
                    onDragLeave={() => {
                      setDragOverDomain(null);
                    }}
                    onDrop={async e => {
                      e.preventDefault();
                      setDragOverDomain(null);
                      const docId = e.dataTransfer.getData('text/plain');
                      const docName = e.dataTransfer.getData('docName') || 'document';
                      if (!docId) return;
                      const sourceDomain = docId.split('::')[0];
                      if (sourceDomain.toLowerCase() === domain.id.toLowerCase()) return;
                      
                      try {
                        setLoading(true);
                        setError(null);
                        setSuccessMsg(null);
                        await apiReassignDocument(docId, domain.id);
                        setSuccessMsg(`Successfully moved document "${docName}" to category "${domain.label}".`);
                        await fetchDocs();
                      } catch (err: any) {
                        console.error(err);
                        setError('Error moving document to another category.');
                      } finally {
                        setLoading(false);
                      }
                    }}
                    style={{
                      padding: '12px 14px',
                      background: isActive 
                        ? 'var(--primary-fixed)' 
                        : isDragOver 
                        ? 'rgba(0, 85, 212, 0.15)' 
                        : 'transparent',
                      border: isActive 
                        ? '2px solid var(--primary-container)' 
                        : isDragOver 
                        ? '2px dashed var(--primary)' 
                        : '1px solid var(--outline-variant)',
                      borderRadius: 'var(--radius-md)',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      position: 'relative',
                    }}
                    onMouseEnter={e => {
                      if (!isActive && !isDragOver) {
                        e.currentTarget.style.borderColor = 'var(--outline)';
                        e.currentTarget.style.background = 'var(--surface-container-low)';
                      }
                    }}
                    onMouseLeave={e => {
                      if (!isActive && !isDragOver) {
                        e.currentTarget.style.borderColor = 'var(--outline-variant)';
                        e.currentTarget.style.background = 'transparent';
                      }
                    }}
                  >
                    {/* Domain Icon */}
                    <div style={{
                      width: '34px',
                      height: '34px',
                      borderRadius: 'var(--radius-sm)',
                      background: isActive ? 'var(--surface-container-lowest)' : 'var(--surface-container-low)',
                      color: isActive ? 'var(--primary-container)' : 'var(--on-surface-variant)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                    }}>
                      {domain.icon === 'CodeIcon' && <CodeIcon />}
                      {domain.icon === 'CalculatorIcon' && <CalculatorIcon />}
                      {domain.icon === 'AtomIcon' && <AtomIcon />}
                      {domain.icon === 'CpuIcon' && <CpuIcon />}
                      {domain.icon === 'BookOpenIcon' && <BookOpenIcon />}
                    </div>

                    {/* Domain Texts */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{
                        fontSize: '13.5px',
                        fontWeight: 600,
                        color: isActive ? 'var(--primary-container)' : 'var(--on-surface)',
                        fontFamily: 'var(--font-display)',
                      }}>
                        {domain.label}
                      </div>
                      <div style={{
                        fontSize: '11px',
                        color: 'var(--on-surface-variant)',
                        marginTop: '1px',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}>
                        {domain.desc}
                      </div>
                    </div>

                    {/* Badge count */}
                    <span style={{
                      fontSize: '10px',
                      fontWeight: 600,
                      padding: '2px 8px',
                      borderRadius: '99px',
                      background: isActive ? 'var(--primary-container)' : 'var(--surface-container-high)',
                      color: isActive ? 'var(--on-primary)' : 'var(--on-surface-variant)',
                      fontFamily: 'var(--font-label)',
                      flexShrink: 0,
                    }}>
                      {count} {count === 1 ? 'file' : 'files'}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Custom domain input */}
            <div style={{ 
              marginTop: '16px', 
              paddingTop: '16px', 
              borderTop: '1px solid var(--outline-variant)' 
            }}>
              <div style={{ display: 'flex', gap: '8px' }}>
                <input
                  type="text"
                  placeholder="Add new category..."
                  value={newDomainName}
                  onChange={e => setNewDomainName(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter') {
                      handleAddDomain();
                    }
                  }}
                  style={{
                    flex: 1,
                    padding: '8px 12px',
                    fontSize: '13px',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--outline-variant)',
                    background: 'var(--surface-container-lowest)',
                    color: 'var(--on-surface)',
                    fontFamily: 'var(--font-body)',
                  }}
                />
                <button
                  onClick={handleAddDomain}
                  style={{
                    padding: '8px 14px',
                    fontSize: '12.5px',
                    fontWeight: 600,
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--primary-container)',
                    color: 'var(--on-primary)',
                    border: 'none',
                    cursor: 'pointer',
                    fontFamily: 'var(--font-display)',
                    transition: 'all 0.15s ease',
                  }}
                  onMouseEnter={e => e.currentTarget.style.filter = 'brightness(0.95)'}
                  onMouseLeave={e => e.currentTarget.style.filter = ''}
                >
                  + Add
                </button>
              </div>
            </div>
          </div>

          {/* Upload Area Section */}
          <div style={{
            background: 'var(--surface-container-lowest)',
            border: '1px solid var(--outline-variant)',
            borderRadius: 'var(--radius-lg)',
            padding: '18px',
            boxShadow: 'var(--shadow-1)',
          }}>
            <h2 style={{ 
              fontFamily: 'var(--font-display)', 
              fontSize: '13.5px', 
              fontWeight: 600, 
              color: 'var(--on-surface)', 
              marginBottom: '12px',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              2. Upload to Category:{' '}
              <span style={{ color: 'var(--primary-container)', fontWeight: 700 }}>
                {allDomains.find(d => d.id === selectedDomain)?.label}
              </span>
            </h2>

            <div
              onDragOver={handleDragOver}
              onDragEnter={handleDragEnter}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => {
                if (!uploading) {
                  document.getElementById('doc-library-file-input')?.click();
                }
              }}
              style={{
                border: isDragging ? '2px dashed var(--primary-container)' : '2px dashed var(--outline-variant)',
                borderRadius: 'var(--radius-md)',
                padding: '20px 16px',
                textAlign: 'center',
                background: isDragging 
                  ? 'var(--primary-fixed)' 
                  : uploading 
                  ? 'var(--surface-container-low)' 
                  : 'var(--surface-container-lowest)',
                cursor: uploading ? 'not-allowed' : 'pointer',
                transition: 'all 0.15s ease',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '10px',
                height: '140px',
              }}
              onMouseEnter={e => {
                if (!uploading && !isDragging) {
                  e.currentTarget.style.borderColor = 'var(--primary-container)';
                  e.currentTarget.style.background = 'var(--surface-container-low)';
                }
              }}
              onMouseLeave={e => {
                if (!uploading && !isDragging) {
                  e.currentTarget.style.borderColor = 'var(--outline-variant)';
                  e.currentTarget.style.background = 'var(--surface-container-lowest)';
                }
              }}
            >
              <input
                id="doc-library-file-input"
                type="file"
                multiple
                accept=".pdf"
                style={{ display: 'none' }}
                onChange={e => handleFileUpload(e.target.files)}
                disabled={uploading}
              />

              <div style={{
                width: '38px',
                height: '38px',
                borderRadius: '50%',
                background: isDragging ? 'var(--primary-container)' : 'var(--primary-fixed)',
                color: isDragging ? 'var(--on-primary)' : 'var(--primary-container)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.15s',
              }}>
                {uploading ? (
                  <div className="spinner" style={{ width: '14px', height: '14px', border: '2px solid var(--primary-container)', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                ) : (
                  <CloudUploadIcon />
                )}
              </div>

              <div>
                <div style={{
                  fontSize: '13px',
                  fontWeight: 600,
                  color: 'var(--on-surface)',
                  fontFamily: 'var(--font-display)',
                }}>
                  {uploading 
                    ? 'Processing...' 
                    : 'Drag & Drop PDF or click to browse'}
                </div>
                <div style={{
                  fontSize: '11px',
                  color: 'var(--on-surface-variant)',
                  marginTop: '2px',
                }}>
                  Supports PDF, up to 50MB
                </div>
              </div>
            </div>
          </div>

          {/* Upload Queue list inside left column */}
          {uploadQueue.length > 0 && (
            <div style={{
              background: 'var(--surface-container-low)',
              border: '1px solid var(--outline-variant)',
              borderRadius: 'var(--radius-md)',
              padding: '12px',
            }}>
              <div style={{
                fontSize: '10.5px',
                fontWeight: 600,
                color: 'var(--on-surface-variant)',
                marginBottom: '8px',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                fontFamily: 'var(--font-label)',
              }}>
                Upload Progress
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {uploadQueue.map((item, idx) => (
                  <div key={idx} style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    background: 'var(--surface-container-lowest)',
                    padding: '6px 10px',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--outline-variant)',
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', overflow: 'hidden', flex: 1 }}>
                      <div style={{
                        width: '18px', height: '18px',
                        background: item.status === 'success' ? 'var(--success-container)' : item.status === 'error' ? 'var(--error-container)' : 'var(--primary-fixed)',
                        borderRadius: '2px',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '7.5px', fontWeight: 700,
                        color: item.status === 'success' ? 'var(--success)' : item.status === 'error' ? 'var(--error)' : 'var(--primary-container)',
                        flexShrink: 0,
                      }}>PDF</div>
                      <span style={{ fontSize: '11.5px', color: 'var(--on-surface)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '140px' }}>
                        {item.name}
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', flexShrink: 0 }}>
                      {item.status === 'uploading' && (
                        <>
                          <div className="spinner" style={{ width: '8px', height: '8px', border: '1.5px solid var(--primary-container)', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                          <span style={{ color: 'var(--primary-container)' }}>Uploading...</span>
                        </>
                      )}
                      {item.status === 'success' && (
                        <span style={{ color: 'var(--success)' }}>Success</span>
                      )}
                      {item.status === 'error' && (
                        <span style={{ color: 'var(--error)' }} title={item.error}>Failed</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* RIGHT COLUMN: Document Library List Dashboard */}
        <div style={{
          background: 'var(--surface-container-lowest)',
          border: '1px solid var(--outline-variant)',
          borderRadius: 'var(--radius-lg)',
          overflow: 'hidden',
          boxShadow: 'var(--shadow-1)',
        }}>
          {/* Table Header Bar with Search, Bulk Actions, Filters */}
          <div style={{
            padding: '16px 20px',
            borderBottom: '1px solid var(--outline-variant)',
            background: 'var(--surface-container-low)',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '12px',
            }}>
              {selectedDocIds.length > 0 ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                  <span style={{ fontSize: '13.5px', color: 'var(--on-surface)', fontWeight: 600 }}>
                    Selected <strong style={{ color: 'var(--primary-container)' }}>{selectedDocIds.length}</strong> documents
                  </span>
                  <button
                    onClick={handleBulkDelete}
                    style={{
                      padding: '6px 14px',
                      fontSize: '12.5px',
                      fontWeight: 600,
                      background: 'var(--error-container)',
                      color: 'var(--error)',
                      border: '1px solid rgba(186, 26, 26, 0.2)',
                      borderRadius: 'var(--radius-sm)',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      fontFamily: 'var(--font-display)',
                    }}
                  >
                    <TrashIcon size={13} />
                    Delete selected files
                  </button>
                </div>
              ) : (
                <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '15px', fontWeight: 600, color: 'var(--on-surface)' }}>
                  Research Resource Repository
                </h2>
              )}
              
              <input
                id="doc-search"
                className="input input-search"
                style={{ width: '240px' }}
                placeholder="Search documents..."
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>

            {/* Segmented Filter Tab Pills */}
            <div style={{
              display: 'flex',
              gap: '6px',
              overflowX: 'auto',
              paddingBottom: '2px',
            }}>
              {[
                { id: 'all', label: 'All', count: documents.length },
                ...allDomains.map(d => ({
                  id: d.id,
                  label: d.label,
                  count: documents.filter(doc => doc.author.toLowerCase() === d.id).length
                }))
              ].map(tab => {
                const isTabActive = filterDomain === tab.id;
                
                return (
                  <button
                    key={tab.id}
                    onClick={() => setFilterDomain(tab.id)}
                    style={{
                      padding: '5px 12px',
                      borderRadius: '99px',
                      border: isTabActive ? 'none' : '1px solid var(--outline-variant)',
                      background: isTabActive ? 'var(--primary-container)' : 'var(--surface-container-lowest)',
                      color: isTabActive ? 'var(--on-primary)' : 'var(--on-surface-variant)',
                      fontSize: '11.5px',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '5px',
                      whiteSpace: 'nowrap',
                      transition: 'all 0.15s ease',
                    }}
                    onMouseEnter={e => {
                      if (!isTabActive) {
                        e.currentTarget.style.background = 'var(--surface-container-high)';
                        e.currentTarget.style.color = 'var(--on-surface)';
                      }
                    }}
                    onMouseLeave={e => {
                      if (!isTabActive) {
                        e.currentTarget.style.background = 'var(--surface-container-lowest)';
                        e.currentTarget.style.color = 'var(--on-surface-variant)';
                      }
                    }}
                  >
                    {tab.label}
                    <span style={{
                      fontSize: '9px',
                      background: isTabActive ? 'rgba(255,255,255,0.2)' : 'var(--surface-container-high)',
                      color: isTabActive ? 'var(--on-primary)' : 'var(--on-surface-variant)',
                      padding: '1px 5px',
                      borderRadius: '99px',
                      fontWeight: 700,
                    }}>
                      {tab.count}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Table itself */}
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '600px' }}>
              <thead>
                <tr style={{ background: 'var(--surface-container-low)' }}>
                  {/* Select All Checkbox */}
                  <th style={{
                    width: '40px',
                    padding: '10px 14px',
                    borderBottom: '1px solid var(--outline-variant)',
                    textAlign: 'center'
                  }}>
                    <input
                      type="checkbox"
                      checked={sortedAndFiltered.length > 0 && selectedDocIds.length === sortedAndFiltered.length}
                      onChange={e => {
                        if (e.target.checked) {
                          setSelectedDocIds(sortedAndFiltered.map(d => d.id));
                        } else {
                          setSelectedDocIds([]);
                        }
                      }}
                      style={{ cursor: 'pointer' }}
                    />
                  </th>
                  {['DOCUMENT TITLE', 'CATEGORY', 'YEAR', 'DATE ADDED', 'SIZE', 'AI STATUS', 'ACTIONS'].map(h => (
                    <th key={h} style={{
                      padding: '10px 14px',
                      textAlign: 'left',
                      fontFamily: 'var(--font-label)',
                      fontSize: '10.5px',
                      fontWeight: 600,
                      color: 'var(--on-surface-variant)',
                      letterSpacing: '0.06em',
                      borderBottom: '1px solid var(--outline-variant)',
                      whiteSpace: 'nowrap',
                    }}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={8} style={{ padding: '32px', textAlign: 'center', color: 'var(--on-surface-variant)', fontSize: '14px' }}>
                      <div style={{ display: 'inline-block', width: '20px', height: '20px', border: '3px solid var(--primary)', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite', marginBottom: '8px' }} />
                      <div>Loading research resources...</div>
                    </td>
                  </tr>
                ) : sortedAndFiltered.length === 0 ? (
                  <tr>
                    <td colSpan={8} style={{ padding: '32px', textAlign: 'center', color: 'var(--on-surface-variant)', fontSize: '13px' }}>
                      No matching documents found in library.
                    </td>
                  </tr>
                ) : (
                  sortedAndFiltered.map((doc, i) => {
                    const st = AI_STATUS[doc.status] || AI_STATUS.pending;
                    const isSelected = selectedDocIds.includes(doc.id);
                    return (
                      <tr 
                        key={`${doc.id}-${i}`} 
                        draggable
                        onDragStart={e => {
                          e.dataTransfer.setData('text/plain', doc.id);
                          e.dataTransfer.setData('docName', doc.name);
                          e.dataTransfer.effectAllowed = 'move';
                        }}
                        style={{
                          borderBottom: i < sortedAndFiltered.length - 1 ? '1px solid var(--surface-container-high)' : 'none',
                          transition: 'background 0.12s',
                          background: isSelected ? 'rgba(var(--primary-rgb), 0.05)' : '',
                          cursor: 'grab'
                        }}
                        onMouseEnter={e => (e.currentTarget.style.background = isSelected ? 'rgba(var(--primary-rgb), 0.08)' : 'var(--surface-container-low)')}
                        onMouseLeave={e => (e.currentTarget.style.background = isSelected ? 'rgba(var(--primary-rgb), 0.05)' : '')}
                      >
                        {/* Select row checkbox */}
                        <td style={{
                          padding: '10px 14px',
                          textAlign: 'center',
                          borderBottom: i < sortedAndFiltered.length - 1 ? '1px solid var(--surface-container-high)' : 'none'
                        }}>
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={e => {
                              if (e.target.checked) {
                                setSelectedDocIds(prev => [...prev, doc.id]);
                              } else {
                                setSelectedDocIds(prev => prev.filter(id => id !== doc.id));
                              }
                            }}
                            style={{ cursor: 'pointer' }}
                          />
                        </td>
                        <td style={{ padding: '10px 14px' }}>
                          <div 
                            style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}
                            onClick={() => setViewModal({ isOpen: true, docName: doc.name })}
                          >
                            <div style={{
                              width: '24px', height: '24px',
                              background: 'var(--error-container)',
                              borderRadius: '3px',
                              display: 'flex', alignItems: 'center', justifyContent: 'center',
                              fontSize: '9px', fontWeight: 700,
                              color: 'var(--error)',
                              flexShrink: 0,
                              fontFamily: 'var(--font-label)',
                            }}>PDF</div>
                            <span style={{ fontSize: '12.5px', fontWeight: 500, color: 'var(--primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '220px', textDecoration: 'underline', textUnderlineOffset: '2px' }} title={doc.name}>
                              {doc.name}
                            </span>
                          </div>
                        </td>
                        <td style={{ padding: '10px 14px', fontSize: '12px', color: 'var(--on-surface-variant)' }}>
                          <span style={{
                            padding: '2px 6px',
                            borderRadius: 'var(--radius-xs)',
                            background: 'var(--secondary-container)',
                            color: 'var(--secondary)',
                            fontSize: '10.5px',
                            fontWeight: 600,
                            textTransform: 'uppercase',
                          }}>
                            {doc.author}
                          </span>
                        </td>
                        <td style={{ padding: '10px 14px', fontSize: '12px', color: 'var(--on-surface-variant)' }}>
                          {doc.year}
                        </td>
                        <td style={{ padding: '10px 14px', fontSize: '12px', color: 'var(--on-surface-variant)' }}>
                          {doc.date}
                        </td>
                        <td style={{ padding: '10px 14px', fontSize: '12px', color: 'var(--on-surface-variant)' }}>
                          {doc.size}
                        </td>
                        <td style={{ padding: '10px 14px' }}>
                          <span style={{
                            display: 'inline-flex', alignItems: 'center', gap: '4px',
                            padding: '2px 8px',
                            background: st.bg, color: st.color,
                            borderRadius: '99px',
                            fontSize: '11px', fontFamily: 'var(--font-label)', fontWeight: 600,
                          }}>
                            {doc.status === 'done' && '✓ '}{st.label}
                          </span>
                        </td>
                        <td style={{ padding: '10px 14px' }}>
                          <div style={{ display: 'flex', gap: '4px' }}>
                            <button 
                              onClick={() => setViewModal({ isOpen: true, docName: doc.name })}
                              style={{
                                background: 'transparent',
                                border: 'none',
                                color: 'var(--primary)',
                                cursor: 'pointer',
                                padding: '4px',
                                borderRadius: '4px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                transition: 'background 0.15s',
                              }}
                              onMouseEnter={e => e.currentTarget.style.background = 'var(--primary-container)'}
                              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                              title="View Document"
                            >
                              <EyeIcon size={14} />
                            </button>
                            <button 
                              onClick={() => handleSingleDelete(doc.id, doc.name)}
                              style={{
                                background: 'transparent',
                                border: 'none',
                                color: 'var(--error)',
                                cursor: 'pointer',
                                padding: '4px',
                                borderRadius: '4px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                transition: 'background 0.15s',
                              }}
                              onMouseEnter={e => e.currentTarget.style.background = 'var(--error-container)'}
                              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                              title="Delete Document"
                            >
                              <TrashIcon size={14} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination/Status row */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '12px 14px',
            borderTop: '1px solid var(--outline-variant)',
            fontSize: '12px',
            color: 'var(--on-surface-variant)',
            background: 'var(--surface-container-low)',
          }}>
            <span>Showing <strong>{sortedAndFiltered.length}</strong> documents</span>
            <div>
              <span>Total: <strong>{sortedAndFiltered.length}</strong></span>
            </div>
          </div>
        </div>

      </div>

      {/* Premium Deletion Confirmation Modal */}
      {deleteModal.isOpen && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.4)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          animation: 'fadeIn 0.2s ease',
        }}>
          <div style={{
            background: 'var(--surface-container-lowest)',
            border: '1px solid var(--outline-variant)',
            borderRadius: 'var(--radius-lg)',
            width: '420px',
            maxWidth: '90%',
            padding: '24px',
            boxShadow: 'var(--shadow-3)',
            animation: 'scaleIn 0.2s ease',
          }}>
            <h3 style={{
              fontFamily: 'var(--font-display)',
              fontSize: '18px',
              fontWeight: 700,
              color: 'var(--error)',
              margin: '0 0 12px 0',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}>
              <span>⚠️</span> Confirm Document Deletion
            </h3>
            <p style={{
              fontSize: '14.5px',
              color: 'var(--on-surface)',
              lineHeight: '1.5',
              margin: '0 0 20px 0',
            }}>
              {deleteModal.type === 'single' ? (
                <>Are you sure you want to permanently delete document <strong>"{deleteModal.filename}"</strong>? This action cannot be undone.</>
              ) : (
                <>Are you sure you want to permanently delete <strong>{selectedDocIds.length}</strong> selected documents? This action cannot be undone.</>
              )}
            </p>
            <div style={{
              display: 'flex',
              justifyContent: 'flex-end',
              gap: '10px',
            }}>
              <button
                id="cancel-delete-btn"
                onClick={() => setDeleteModal({ isOpen: false, type: 'single' })}
                style={{
                  padding: '8px 16px',
                  fontSize: '13.5px',
                  fontWeight: 600,
                  borderRadius: 'var(--radius-sm)',
                  background: 'var(--surface-container-high)',
                  color: 'var(--on-surface-variant)',
                  border: '1px solid var(--outline-variant)',
                  cursor: 'pointer',
                  fontFamily: 'var(--font-display)',
                  transition: 'background 0.15s',
                }}
                onMouseEnter={e => e.currentTarget.style.background = 'var(--surface-container-highest)'}
                onMouseLeave={e => e.currentTarget.style.background = 'var(--surface-container-high)'}
              >
                Cancel
              </button>
              <button
                id="confirm-delete-btn"
                onClick={handleConfirmDelete}
                style={{
                  padding: '8px 16px',
                  fontSize: '13.5px',
                  fontWeight: 600,
                  borderRadius: 'var(--radius-sm)',
                  background: 'var(--error)',
                  color: 'var(--on-error)',
                  border: 'none',
                  cursor: 'pointer',
                  fontFamily: 'var(--font-display)',
                  transition: 'background 0.15s',
                }}
                onMouseEnter={e => e.currentTarget.style.background = 'var(--error-hover, #a61c1c)'}
                onMouseLeave={e => e.currentTarget.style.background = 'var(--error)'}
              >
                Confirm Delete
              </button>
            </div>
          </div>
        </div>
      )}
      {/* Simulated PDF Viewer Modal */}
      {viewModal.isOpen && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.6)',
          backdropFilter: 'blur(6px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10000,
          animation: 'fadeIn 0.2s ease',
        }}>
          <div style={{
            background: 'var(--surface-container-lowest)',
            border: '1px solid var(--outline-variant)',
            borderRadius: 'var(--radius-lg)',
            width: '900px',
            maxWidth: '95%',
            height: '80vh',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: 'var(--shadow-4)',
            animation: 'scaleIn 0.2s ease',
            overflow: 'hidden',
          }}>
            {/* Modal Header */}
            <div style={{
              padding: '16px 24px',
              borderBottom: '1px solid var(--outline-variant)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              background: 'var(--surface-container-low)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{
                  width: '28px', height: '28px',
                  background: 'var(--error-container)',
                  borderRadius: '4px',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '10px', fontWeight: 700,
                  color: 'var(--error)',
                  fontFamily: 'var(--font-label)',
                }}>PDF</div>
                <h3 style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '16px',
                  fontWeight: 600,
                  color: 'var(--on-surface)',
                  margin: 0,
                }}>
                  {viewModal.docName}
                </h3>
              </div>
              <button
                onClick={() => setViewModal({ isOpen: false })}
                style={{
                  background: 'transparent',
                  border: 'none',
                  fontSize: '24px',
                  lineHeight: 1,
                  color: 'var(--on-surface-variant)',
                  cursor: 'pointer',
                }}
              >
                &times;
              </button>
            </div>

            {/* Modal Body: Fake PDF Content & Selection Simulation */}
            <div style={{
              flex: 1,
              padding: '32px 64px',
              overflowY: 'auto',
              background: '#f8f9fa',
              display: 'flex',
              flexDirection: 'column',
              gap: '24px',
              fontFamily: 'var(--font-serif)',
              color: '#333',
              lineHeight: 1.8,
              fontSize: '15px'
            }}>
              <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '28px', marginBottom: '8px' }}>Simulated Document Content</h1>
                <p style={{ color: '#666', fontStyle: 'italic' }}>Drag and select text below to create a snippet</p>
              </div>

              <p>
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
              </p>

              <div style={{
                position: 'relative',
                background: 'rgba(255, 235, 59, 0.3)',
                padding: '4px 8px',
                borderRadius: '4px',
                borderLeft: '3px solid var(--primary)',
                cursor: 'text'
              }}>
                <strong>Highlighted text snippet (simulating user mouse selection).</strong> Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
                
                {/* Simulated Context Menu for Snippet Saving */}
                <div style={{
                  position: 'absolute',
                  top: '-40px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  background: 'var(--surface-container-highest)',
                  padding: '6px 12px',
                  borderRadius: '8px',
                  boxShadow: 'var(--shadow-2)',
                  display: 'flex',
                  gap: '8px',
                  zIndex: 10,
                }}>
                  <button 
                    onClick={() => {
                      setSuccessMsg('Snippet successfully saved to "Saved Snippets"!');
                      setViewModal({ isOpen: false });
                    }}
                    style={{
                      background: 'var(--primary)',
                      color: 'var(--on-primary)',
                      border: 'none',
                      padding: '4px 12px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" strokeLinecap="round" strokeLinejoin="round" />
                      <polyline points="17 21 17 13 7 13 7 21" />
                      <polyline points="7 3 7 8 15 8" />
                    </svg>
                    Save Snippet
                  </button>
                </div>
              </div>

              <p>
                Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.
              </p>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
