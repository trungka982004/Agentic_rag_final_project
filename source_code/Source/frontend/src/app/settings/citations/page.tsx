'use client';

// Stitch screen: "Scientific Citations"
// Table: # | Author | Title | Journal | Year | Cited by | Actions
// Search + filter chips + pagination

import { useState } from 'react';

const CITATIONS = [
  { id: 1, authors: 'Vaswani, A. et al.', title: 'Attention Is All You Need', journal: 'NeurIPS', year: 2017, cited: 72849 },
  { id: 2, authors: 'Devlin, J. et al.', title: 'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding', journal: 'NAACL', year: 2019, cited: 52341 },
  { id: 3, authors: 'Lewis, P. et al.', title: 'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks', journal: 'NeurIPS', year: 2020, cited: 8512 },
  { id: 4, authors: 'Brown, T. et al.', title: 'Language Models are Few-Shot Learners (GPT-3)', journal: 'NeurIPS', year: 2020, cited: 24890 },
  { id: 5, authors: 'OpenAI', title: 'GPT-4 Technical Report', journal: 'ArXiv', year: 2023, cited: 11203 },
];

const CITE_FORMATS = ['APA', 'MLA', 'Chicago', 'BibTeX'];

export default function ScientificCitationsPage() {
  const [search, setSearch] = useState('');
  const [format, setFormat] = useState('APA');
  const [selected, setSelected] = useState<number[]>([]);
  
  const [showToast, setShowToast] = useState('');

  const showNotification = (msg: string) => {
    setShowToast(msg);
    setTimeout(() => setShowToast(''), 3000);
  };

  const toggleSelect = (id: number) =>
    setSelected(s => s.includes(id) ? s.filter(x => x !== id) : [...s, id]);

  const filtered = CITATIONS.filter(c =>
    !search ||
    c.title.toLowerCase().includes(search.toLowerCase()) ||
    c.authors.toLowerCase().includes(search.toLowerCase())
  );

  const downloadFile = (content: string, filename: string, type: string) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleExport = (exportFormat: string, items = filtered) => {
    if (items.length === 0) {
      showNotification('No data to export');
      return;
    }

    let content = '';
    let filename = '';
    const type = 'text/plain';

    if (exportFormat === 'BibTeX') {
      content = items.map(c => `@article{ref${c.id},
  title={${c.title}},
  author={${c.authors}},
  journal={${c.journal}},
  year={${c.year}}
}`).join('\n\n');
      filename = 'citations.bib';
    } else if (exportFormat === 'RIS') {
      content = items.map(c => `TY  - JOUR\nTI  - ${c.title}\nAU  - ${c.authors}\nJO  - ${c.journal}\nPY  - ${c.year}\nER  - `).join('\n\n');
      filename = 'citations.ris';
    } else {
      content = items.map(c => `[${c.id}] ${c.authors} (${c.year}). ${c.title}. ${c.journal}.`).join('\n');
      filename = `citations_${exportFormat.toLowerCase()}.txt`;
    }

    downloadFile(content, filename, type);
    showNotification(`Downloaded ${filename}`);
  };

  return (
    <div style={{
      maxWidth: '960px',
      margin: '0 auto',
      width: '100%',
      position: 'relative',
    }}>
      {/* Toast Notification */}
      {showToast && (
        <div style={{
          position: 'fixed', bottom: '24px', left: '50%', transform: 'translateX(-50%)',
          background: 'var(--success-container)', color: 'var(--success)',
          padding: '12px 24px', borderRadius: 'var(--radius-md)',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          display: 'flex', alignItems: 'center', gap: '8px', zIndex: 100,
          fontWeight: 600, fontSize: '14px', fontFamily: 'var(--font-display)'
        }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <polyline points="20 6 9 17 4 12" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          {showToast}
        </div>
      )}

      {/* Header */}
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
        marginBottom: '24px',
      }}>
        <div>
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 700, color: 'var(--on-surface)' }}>
            Scientific Citations
          </h1>
          <p style={{ color: 'var(--on-surface-variant)', fontSize: '14px', marginTop: '4px' }}>
            Manage your reference list and export citations bibliography according to academic standards.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {/* Format selector */}
          <div style={{ display: 'flex', gap: '3px' }}>
            {CITE_FORMATS.map(f => (
              <button key={f} onClick={() => setFormat(f)} style={{
                padding: '5px 10px',
                border: '1px solid var(--outline-variant)',
                borderRadius: 'var(--radius-sm)',
                background: format === f ? 'var(--primary-container)' : 'transparent',
                color: format === f ? 'var(--on-primary)' : 'var(--on-surface-variant)',
                fontSize: '12.5px', fontFamily: 'var(--font-label)', fontWeight: 500,
                cursor: 'pointer',
              }}>
                {f}
              </button>
            ))}
          </div>
          <button 
            className="btn btn-primary" 
            id="citations-export-btn" 
            style={{ gap: '6px', fontSize: '13px' }}
            onClick={() => handleExport(format, filtered)}
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            Export Bibliography
          </button>
        </div>
      </div>

      {/* Search */}
      <input
        id="citations-search"
        className="input input-search"
        placeholder="Search author or title..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        style={{ maxWidth: '400px', marginBottom: '16px' }}
      />

      {/* Table */}
      <div style={{
        background: 'var(--surface-container-lowest)',
        border: '1px solid var(--outline-variant)',
        borderRadius: 'var(--radius-md)',
        overflow: 'hidden',
        marginBottom: '12px',
      }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: 'var(--surface-container-low)' }}>
              <th style={{ width: '36px', padding: '10px 12px', textAlign: 'center' }}>
                <input type="checkbox"
                  onChange={e => setSelected(e.target.checked ? CITATIONS.map(c => c.id) : [])}
                  checked={selected.length === CITATIONS.length && CITATIONS.length > 0}
                />
              </th>
              {['#', 'AUTHOR', 'TITLE', 'JOURNAL', 'YEAR', 'CITED BY', ''].map((h, i) => (
                <th key={i} style={{
                  padding: '10px 14px', textAlign: 'left',
                  fontFamily: 'var(--font-label)', fontSize: '11px', fontWeight: 600,
                  color: 'var(--on-surface-variant)', letterSpacing: '0.06em',
                  borderBottom: '1px solid var(--outline-variant)',
                  whiteSpace: 'nowrap',
                }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((c, i) => (
              <tr key={c.id} style={{
                borderBottom: i < filtered.length - 1 ? '1px solid var(--surface-container-high)' : 'none',
                background: selected.includes(c.id) ? 'var(--primary-fixed)' : 'transparent',
                transition: 'background 0.12s',
              }}
                onMouseEnter={e => !selected.includes(c.id) && ((e.currentTarget as HTMLElement).style.background = 'var(--surface-container-low)')}
                onMouseLeave={e => !selected.includes(c.id) && ((e.currentTarget as HTMLElement).style.background = '')}
              >
                <td style={{ padding: '10px 12px', textAlign: 'center' }}>
                  <input type="checkbox"
                    checked={selected.includes(c.id)}
                    onChange={() => toggleSelect(c.id)}
                  />
                </td>
                <td style={{ padding: '10px 14px', fontSize: '12.5px', color: 'var(--on-surface-variant)', fontWeight: 500 }}>
                  [{c.id}]
                </td>
                <td style={{ padding: '10px 14px', fontSize: '12.5px', color: 'var(--on-surface-variant)' }}>
                  {c.authors}
                </td>
                <td style={{ padding: '10px 14px' }}>
                  <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--on-surface)', lineHeight: '1.4' }}>
                    {c.title}
                  </div>
                </td>
                <td style={{ padding: '10px 14px' }}>
                  <span className="chip">{c.journal}</span>
                </td>
                <td style={{ padding: '10px 14px', fontSize: '12.5px', color: 'var(--on-surface-variant)' }}>
                  {c.year}
                </td>
                <td style={{ padding: '10px 14px', fontSize: '12.5px', fontWeight: 600, color: 'var(--primary-container)' }}>
                  {c.cited.toLocaleString()}
                </td>
                <td style={{ padding: '10px 8px' }}>
                  <div style={{ display: 'flex', gap: '2px' }}>
                    <button 
                      className="btn-icon" 
                      title="Copy Citation" 
                      id={`cite-copy-${c.id}`}
                      onClick={() => {
                        const text = `[${c.id}] ${c.authors} (${c.year}). ${c.title}. ${c.journal}.`;
                        navigator.clipboard?.writeText(text);
                        showNotification(`Copied citation [${c.id}]`);
                      }}
                    >
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M8 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2M8 4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2H8z" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </button>
                    <button 
                      className="btn-icon" 
                      title="Delete" 
                      id={`cite-delete-${c.id}`} 
                      style={{ color: 'var(--error)' }}
                      onClick={() => showNotification(`Deleted citation [${c.id}]`)}
                    >
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Selection info */}
      {selected.length > 0 && (
        <div style={{
          background: 'var(--primary-fixed)',
          border: '1px solid var(--primary-fixed-dim)',
          borderRadius: 'var(--radius-sm)',
          padding: '10px 14px',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          fontSize: '13px', color: 'var(--primary-container)',
          marginBottom: '12px',
        }}>
          <span>Selected <strong>{selected.length}</strong> citations</span>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button 
              className="btn btn-secondary" 
              style={{ fontSize: '12px', padding: '5px 12px' }}
              onClick={() => {
                const selectedItems = CITATIONS.filter(c => selected.includes(c.id));
                const text = selectedItems.map(c => `[${c.id}] ${c.authors} (${c.year}). ${c.title}. ${c.journal}.`).join('\n');
                navigator.clipboard?.writeText(text);
                showNotification(`Copied ${selected.length} citations in ${format} format`);
              }}
            >
              Copy {format}
            </button>
            <button 
              className="btn btn-primary" 
              style={{ fontSize: '12px', padding: '5px 12px' }}
              onClick={() => {
                const selectedItems = CITATIONS.filter(c => selected.includes(c.id));
                handleExport(format, selectedItems);
              }}
            >
              Export Selection
            </button>
          </div>
        </div>
      )}

      {/* Bottom action bar — matches Stitch design */}
      <div style={{
        display: 'flex', gap: '8px', flexWrap: 'wrap',
        paddingTop: '14px',
        borderTop: '1px solid var(--outline-variant)',
      }}>
        <button
          className="btn btn-secondary"
          id="citations-copy-all-btn"
          style={{ fontSize: '12.5px', gap: '6px' }}
          onClick={() => {
            const text = filtered.map(c =>
              `[${c.id}] ${c.authors} (${c.year}). ${c.title}. ${c.journal}.`
            ).join('\n');
            navigator.clipboard?.writeText(text);
            showNotification(`Copied all ${filtered.length} citations`);
          }}
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M8 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2M8 4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2H8z" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Copy All
        </button>
        <button
          className="btn btn-secondary"
          id="citations-export-bibtex-btn"
          style={{ fontSize: '12.5px', gap: '6px' }}
          onClick={() => handleExport('BibTeX')}
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Export BibTeX
        </button>
        <button
          className="btn btn-secondary"
          id="citations-export-ris-btn"
          style={{ fontSize: '12.5px', gap: '6px' }}
          onClick={() => handleExport('RIS')}
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Export EndNote (RIS)
        </button>
        <button
          className="btn btn-primary"
          id="citations-save-btn"
          style={{ fontSize: '12.5px', gap: '6px', marginLeft: 'auto' }}
          onClick={() => showNotification('Saved bibliography to system')}
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" strokeLinecap="round" strokeLinejoin="round" />
            <polyline points="17 21 17 13 7 13 7 21" />
            <polyline points="7 3 7 8 15 8" />
          </svg>
          Save Bibliography
        </button>
      </div>
    </div>
  );
}
