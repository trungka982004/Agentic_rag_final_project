'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

// Stitch screen: "Saved Snippets"
// Card grid with: quoted text (reading-serif), source, tags, "View full context" link, copy/delete actions
// Top: search bar + filter chips (All, Self-Attention, Transformer, LLM, NLP)
// Bottom: "Add new snippet" empty card + "Open Document Library" button

const FILTER_CHIPS = ['All', 'Self-Attention', 'Transformer', 'LLM', 'NLP'];

const SAMPLE_SNIPPETS = [
  {
    id: 1,
    source: 'Attention Is All You Need.pdf',
    author: 'Vaswani et al. (2017)',
    quote: '"The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely."',
    note: 'This is a key thesis on the importance of the pure self-attention mechanism in the Transformer architecture, showing clear performance gains in parallel training over sequence learning.',
    tags: ['Self-Attention', 'Architecture'],
  },
  {
    id: 2,
    source: 'BERT: Pre-training of Deep Bidirectional Transformers.pdf',
    author: 'Devlin et al. (2018)',
    quote: '"Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers. As a result, the pre-trained BERT model can be fine-tuned with just one additional output layer."',
    note: 'The key distinction from previous models is the deep bidirectional representations rather than unidirectional ones, allowing BERT to jointly condition on both left and right contexts.',
    tags: ['Bidirectional', 'Pre-training'],
  },
];

export default function SavedSnippetsPage() {
  const router = useRouter();
  const [search, setSearch] = useState('');
  const [activeFilter, setActiveFilter] = useState('All');

  const [showToast, setShowToast] = useState('');

  const showNotification = (msg: string) => {
    setShowToast(msg);
    setTimeout(() => setShowToast(''), 3000);
  };

  const filtered = SAMPLE_SNIPPETS.filter(s =>
    activeFilter === 'All' || s.tags.includes(activeFilter)
  ).filter(s =>
    !search || s.quote.toLowerCase().includes(search.toLowerCase()) ||
    s.source.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div style={{
      maxWidth: '960px',
      margin: '0 auto',
      width: '100%',
      position: 'relative'
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
            Saved Snippets
          </h1>
          <p style={{ color: 'var(--on-surface-variant)', fontSize: '14px', marginTop: '4px' }}>
            Manage and organize important snippets from your research papers.
          </p>
        </div>
        <button 
          className="btn btn-secondary" 
          id="snippets-export-btn" 
          style={{ gap: '6px' }}
          onClick={() => showNotification('Successfully exported all snippet data')}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Export Data
        </button>
      </div>

      {/* Search + filter chips */}
      <div style={{ marginBottom: '20px' }}>
        <input
          id="snippets-search"
          className="input input-search"
          placeholder="Search in snippets..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ maxWidth: '400px', marginBottom: '12px' }}
        />
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {FILTER_CHIPS.map(chip => (
            <button
              key={chip}
              onClick={() => setActiveFilter(chip)}
              style={{
                padding: '4px 14px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid',
                fontSize: '13px',
                fontFamily: 'var(--font-label)',
                fontWeight: 500,
                cursor: 'pointer',
                transition: 'all 0.15s',
                background: activeFilter === chip ? 'var(--primary-container)' : 'var(--surface-container-lowest)',
                color: activeFilter === chip ? 'var(--on-primary)' : 'var(--on-surface-variant)',
                borderColor: activeFilter === chip ? 'var(--primary-container)' : 'var(--outline-variant)',
              }}
            >
              {chip}
            </button>
          ))}
        </div>
      </div>

      {/* Snippet cards grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
        {filtered.map(snippet => (
          <div key={snippet.id} className="card">
            {/* Actions */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '4px', marginBottom: '10px' }}>
              <button 
                className="btn-icon" 
                title="Copy" 
                id={`snippet-copy-${snippet.id}`}
                onClick={() => {
                  navigator.clipboard?.writeText(snippet.quote);
                  showNotification('Snippet content copied to clipboard');
                }}
              >
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M8 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2M8 4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2H8z" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
              <button 
                className="btn-icon" 
                title="Delete" 
                id={`snippet-delete-${snippet.id}`}
                style={{ color: 'var(--error)' }}
                onClick={() => showNotification('Snippet removed from library')}
              >
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
            </div>

            {/* Source */}
            <div style={{ fontSize: '11.5px', color: 'var(--on-surface-variant)', marginBottom: '8px' }}>
              📄 {snippet.source} · {snippet.author}
            </div>

            {/* Quote — reading-serif Stitch spec */}
            <blockquote style={{
              fontFamily: 'var(--font-serif)',
              fontSize: '13.5px',
              lineHeight: '1.7',
              color: 'var(--on-surface)',
              borderLeft: '3px solid var(--primary-container)',
              paddingLeft: '12px',
              marginBottom: '10px',
              fontStyle: 'italic',
            }}>
              {snippet.quote}
            </blockquote>

            {/* Note */}
            {snippet.note && (
              <div style={{
                background: 'var(--surface-container-low)',
                borderRadius: 'var(--radius-sm)',
                padding: '8px 10px',
                marginBottom: '10px',
              }}>
                <div style={{ fontSize: '10.5px', fontFamily: 'var(--font-label)', fontWeight: 600, color: 'var(--primary-container)', marginBottom: '3px' }}>
                  RESEARCHER NOTE
                </div>
                <div style={{ fontSize: '12px', color: 'var(--on-surface-variant)', lineHeight: '1.5' }}>
                  {snippet.note}
                </div>
              </div>
            )}

            {/* Tags + "View context" */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
                {snippet.tags.map(tag => (
                  <span key={tag} className="chip">{tag}</span>
                ))}
              </div>
              <button 
                style={{
                  background: 'none', border: 'none',
                  color: 'var(--primary-container)',
                  fontSize: '12px', cursor: 'pointer',
                  fontFamily: 'var(--font-label)', fontWeight: 500,
                  textDecoration: 'underline', textUnderlineOffset: '2px',
                  whiteSpace: 'nowrap',
                }}
                onClick={() => router.push(`/settings/library?highlight_doc=${encodeURIComponent(snippet.source)}`)}
              >
                View full context ›
              </button>
            </div>
          </div>
        ))}

        {/* "Add new snippet" card */}
        <div style={{
          border: '1.5px dashed var(--outline-variant)',
          borderRadius: 'var(--radius-md)',
          padding: '24px',
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
          textAlign: 'center',
          gap: '12px',
          background: 'var(--surface-container-low)',
          cursor: 'pointer',
          transition: 'border-color 0.15s, background 0.15s',
        }}
          onMouseEnter={e => {
            (e.currentTarget as HTMLElement).style.borderColor = 'var(--primary-container)';
            (e.currentTarget as HTMLElement).style.background = 'var(--primary-fixed)';
          }}
          onMouseLeave={e => {
            (e.currentTarget as HTMLElement).style.borderColor = 'var(--outline-variant)';
            (e.currentTarget as HTMLElement).style.background = 'var(--surface-container-low)';
          }}
        >
          <div style={{
            width: '36px', height: '36px',
            borderRadius: '50%',
            border: '2px solid var(--outline-variant)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'var(--on-surface-variant)', fontSize: '20px',
          }}>+</div>
          <div>
            <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--on-surface)', marginBottom: '4px' }}>
              Add new snippet
            </div>
            <div style={{ fontSize: '12.5px', color: 'var(--on-surface-variant)' }}>
              You can drag and select text while reading documents to add them here.
            </div>
          </div>
          <button 
            className="btn btn-primary" 
            id="snippets-open-library-btn"
            onClick={() => router.push('/settings/library?action=add_snippet')}
          >
            Open Document Library
          </button>
        </div>
      </div>
    </div>
  );
}
