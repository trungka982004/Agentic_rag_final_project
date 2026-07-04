'use client';

// Stitch screen: "Scientific Citations"
// Table: # | Tác giả | Tiêu đề | Tạp chí | Năm | Được trích dẫn | Thao tác
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

  const toggleSelect = (id: number) =>
    setSelected(s => s.includes(id) ? s.filter(x => x !== id) : [...s, id]);

  const filtered = CITATIONS.filter(c =>
    !search ||
    c.title.toLowerCase().includes(search.toLowerCase()) ||
    c.authors.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div style={{ maxWidth: '960px' }}>
      {/* Header */}
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
        marginBottom: '24px',
      }}>
        <div>
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 700, color: 'var(--on-surface)' }}>
            Trích dẫn khoa học
          </h1>
          <p style={{ color: 'var(--on-surface-variant)', fontSize: '14px', marginTop: '4px' }}>
            Quản lý danh sách tài liệu tham khảo và xuất danh mục trích dẫn theo tiêu chuẩn học thuật.
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
          <button className="btn btn-primary" id="citations-export-btn" style={{ gap: '6px', fontSize: '13px' }}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            Xuất danh mục
          </button>
        </div>
      </div>

      {/* Search */}
      <input
        id="citations-search"
        className="input input-search"
        placeholder="Tìm kiếm tác giả hoặc tiêu đề..."
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
                  checked={selected.length === CITATIONS.length}
                />
              </th>
              {['#', 'TÁC GIẢ', 'TIÊU ĐỀ', 'TẠP CHÍ', 'NĂM', 'ĐƯỢC TRÍCH DẪN', ''].map((h, i) => (
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
                    <button className="btn-icon" title="Sao chép trích dẫn" id={`cite-copy-${c.id}`}>
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M8 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2M8 4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2H8z" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </button>
                    <button className="btn-icon" title="Xoá" id={`cite-delete-${c.id}`} style={{ color: 'var(--error)' }}>
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
          <span>Đã chọn <strong>{selected.length}</strong> trích dẫn</span>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button className="btn btn-secondary" style={{ fontSize: '12px', padding: '5px 12px' }}>
              Sao chép {format}
            </button>
            <button className="btn btn-primary" style={{ fontSize: '12px', padding: '5px 12px' }}>
              Xuất lựa chọn
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
          }}
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M8 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2M8 4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2H8z" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Sao chép toàn bộ
        </button>
        <button
          className="btn btn-secondary"
          id="citations-export-bibtex-btn"
          style={{ fontSize: '12.5px', gap: '6px' }}
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Xuất file BibTeX
        </button>
        <button
          className="btn btn-secondary"
          id="citations-export-ris-btn"
          style={{ fontSize: '12.5px', gap: '6px' }}
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Xuất file EndNote (RIS)
        </button>
        <button
          className="btn btn-primary"
          id="citations-save-btn"
          style={{ fontSize: '12.5px', gap: '6px', marginLeft: 'auto' }}
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" strokeLinecap="round" strokeLinejoin="round" />
            <polyline points="17 21 17 13 7 13 7 21" />
            <polyline points="7 3 7 8 15 8" />
          </svg>
          Lưu danh mục
        </button>
      </div>
    </div>
  );
}
