'use client';

import { useState } from 'react';

// Stitch screen: "Đoạn trích đã lưu — Saved Snippets"
// Card grid with: quoted text (reading-serif), source, tags, "Xem ngữ cảnh đầy đủ" link, copy/delete actions
// Top: search bar + filter chips (Tất cả, Self-Attention, Transformer, LLM, NLP)
// Bottom: "Thêm đoạn trích mới" empty card + "Mở Thư viện tài liệu" button

const FILTER_CHIPS = ['Tất cả', 'Self-Attention', 'Transformer', 'LLM', 'NLP'];

const SAMPLE_SNIPPETS = [
  {
    id: 1,
    source: 'Attention Is All You Need.pdf',
    author: 'Vaswani et al. (2017)',
    quote: '"The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely."',
    note: 'Đây là luận điểm trọng tâm về tầm quan trọng từ kiến trúc Transformer thuần túy dựa trên Attention. Chú ý về khái niệm là rõ ràng về hiệu suất học tuần tự song song.',
    tags: ['Self-Attention', 'Architecture'],
  },
  {
    id: 2,
    source: 'BERT: Pre-training of Deep Bidirectional Transformers.pdf',
    author: 'Devlin et al. (2018)',
    quote: '"Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers. As a result, the pre-trained BERT model can be fine-tuned with just one additional output layer."',
    note: 'Điểm khác biệt với các mô hình trước là "bidirectional" thay vì "unidirectional". BERT hiểu ngữ cảnh từ cả hai phía bên trái các các tác vụ ngôn ngữ.',
    tags: ['Bidirectional', 'Pre-training'],
  },
];

export default function SavedSnippetsPage() {
  const [search, setSearch] = useState('');
  const [activeFilter, setActiveFilter] = useState('Tất cả');

  const filtered = SAMPLE_SNIPPETS.filter(s =>
    activeFilter === 'Tất cả' || s.tags.includes(activeFilter)
  ).filter(s =>
    !search || s.quote.toLowerCase().includes(search.toLowerCase()) ||
    s.source.toLowerCase().includes(search.toLowerCase())
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
            Đoạn trích đã lưu
          </h1>
          <p style={{ color: 'var(--on-surface-variant)', fontSize: '14px', marginTop: '4px' }}>
            Quản lý và tổ chức các đoạn trích quan trọng từ tài liệu nghiên cứu của bạn.
          </p>
        </div>
        <button className="btn btn-secondary" id="snippets-export-btn" style={{ gap: '6px' }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Xuất dữ liệu
        </button>
      </div>

      {/* Search + filter chips */}
      <div style={{ marginBottom: '20px' }}>
        <input
          id="snippets-search"
          className="input input-search"
          placeholder="Tìm kiếm trong các đoạn trích..."
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
              <button className="btn-icon" title="Sao chép" id={`snippet-copy-${snippet.id}`}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M8 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2M8 4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2H8z" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
              <button className="btn-icon" title="Xoá" id={`snippet-delete-${snippet.id}`}
                style={{ color: 'var(--error)' }}>
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
                  GHI CHÚ CỦA NHÀ NGHIÊN CỨU
                </div>
                <div style={{ fontSize: '12px', color: 'var(--on-surface-variant)', lineHeight: '1.5' }}>
                  {snippet.note}
                </div>
              </div>
            )}

            {/* Tags + "Xem ngữ cảnh" */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
                {snippet.tags.map(tag => (
                  <span key={tag} className="chip">{tag}</span>
                ))}
              </div>
              <button style={{
                background: 'none', border: 'none',
                color: 'var(--primary-container)',
                fontSize: '12px', cursor: 'pointer',
                fontFamily: 'var(--font-label)', fontWeight: 500,
                textDecoration: 'underline', textUnderlineOffset: '2px',
                whiteSpace: 'nowrap',
              }}>
                Xem ngữ cảnh đầy đủ ›
              </button>
            </div>
          </div>
        ))}

        {/* "Thêm đoạn trích mới" card */}
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
              Thêm đoạn trích mới
            </div>
            <div style={{ fontSize: '12.5px', color: 'var(--on-surface-variant)' }}>
              Bạn có thể kéo và chọn văn bản trong quá trình đọc tài liệu để thêm tiếp vào đây.
            </div>
          </div>
          <button className="btn btn-primary" id="snippets-open-library-btn">
            Mở Thư viện tài liệu
          </button>
        </div>
      </div>
    </div>
  );
}
