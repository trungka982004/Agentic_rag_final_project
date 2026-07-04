'use client';

import { useState, useEffect } from 'react';
import { apiListDocuments, apiUploadDocument, type DocumentInfo } from '@/services/api';

const AI_STATUS = {
  done:     { label: 'Đã phân tích', bg: 'var(--success-container)', color: 'var(--success)' },
  indexing: { label: 'Đang phân tích...', bg: 'var(--warning-container)', color: 'var(--warning)' },
  pending:  { label: 'Chờ phân tích', bg: 'var(--surface-container)', color: 'var(--on-surface-variant)' },
};

const EllipsisIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M12 5h.01M12 12h.01M12 19h.01" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export default function DocumentLibraryPage() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [search, setSearch] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('it');
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDocs = async () => {
    try {
      setLoading(true);
      const data = await apiListDocuments();
      setDocuments(data);
      setError(null);
    } catch (err: any) {
      console.error(err);
      setError('Không thể tải danh sách tài liệu.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    setError(null);
    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (!file.name.endsWith('.pdf')) {
          alert('Chỉ hỗ trợ tệp định dạng PDF.');
          continue;
        }
        await apiUploadDocument(file, selectedDomain);
      }
      alert('Tải lên thành công! AI đang tiến hành phân tích tài liệu mới trong nền.');
      fetchDocs();
    } catch (err: any) {
      console.error(err);
      setError('Tải lên tài liệu thất bại.');
    } finally {
      setUploading(false);
    }
  };

  const filtered = documents.filter(d =>
    d.name.toLowerCase().includes(search.toLowerCase()) ||
    d.author.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div style={{ maxWidth: '960px' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 700, color: 'var(--on-surface)' }}>
          Thư viện tài liệu
        </h1>
        <p style={{ color: 'var(--on-surface-variant)', fontSize: '14px', marginTop: '4px' }}>
          Quản lý kho tài nguyên nghiên cứu khoa học và trạng thái phân tích AI của dự án.
        </p>
      </div>

      {error && (
        <div style={{
          padding: '12px 16px',
          background: 'var(--error-container)',
          color: 'var(--error)',
          borderRadius: 'var(--radius-sm)',
          fontSize: '13.5px',
          marginBottom: '16px',
          fontFamily: 'var(--font-body)',
        }}>
          ⚠️ {error}
        </div>
      )}

      {/* Search + Upload row */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '16px', flexWrap: 'wrap' }}>
        <input
          id="doc-search"
          className="input input-search"
          style={{ flex: 1, minWidth: '240px', maxWidth: '300px' }}
          placeholder="Tìm kiếm tài liệu..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />

        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <label style={{ fontSize: '13px', fontWeight: 500, color: 'var(--on-surface-variant)', fontFamily: 'var(--font-label)' }}>Chủ đề:</label>
          <select
            value={selectedDomain}
            onChange={e => setSelectedDomain(e.target.value)}
            style={{
              padding: '8px 12px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--outline-variant)',
              background: 'var(--surface-container-low)',
              color: 'var(--on-surface)',
              fontSize: '13.5px',
              fontFamily: 'var(--font-body)',
              outline: 'none',
              cursor: 'pointer',
            }}
          >
            <option value="it">CNTT</option>
            <option value="math">Toán học</option>
            <option value="physics">Vật lý</option>
            <option value="electronics">Điện tử</option>
          </select>
        </div>

        <div style={{
          flex: 2,
          minWidth: '280px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          border: '1.5px dashed var(--outline-variant)',
          borderRadius: 'var(--radius-sm)',
          padding: '8px 16px',
          fontSize: '13px',
          color: uploading ? 'var(--warning)' : 'var(--primary-container)',
          cursor: uploading ? 'not-allowed' : 'pointer',
          gap: '8px',
          fontFamily: 'var(--font-label)',
          fontWeight: 500,
          transition: 'background 0.15s',
          opacity: uploading ? 0.7 : 1,
        }}
          onClick={() => {
            if (!uploading) {
              document.getElementById('doc-library-file-input')?.click();
            }
          }}
          onMouseEnter={e => { if (!uploading) e.currentTarget.style.background = 'var(--primary-fixed)'; }}
          onMouseLeave={e => { if (!uploading) e.currentTarget.style.background = ''; }}
        >
          {uploading ? (
            <>
              <div className="spinner" style={{ width: '16px', height: '16px', border: '2px solid var(--warning)', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
              Đang tải lên và phân tích tài liệu...
            </>
          ) : (
            <>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Kéo thả PDF vào đây hoặc{' '}
              <span style={{ textDecoration: 'underline', textUnderlineOffset: '2px' }}>Chọn tập từ máy tính</span>
            </>
          )}
          <input
            id="doc-library-file-input"
            type="file"
            multiple
            accept=".pdf"
            style={{ display: 'none' }}
            onChange={e => handleFileUpload(e.target.files)}
            disabled={uploading}
          />
        </div>
      </div>

      {/* Table */}
      <div style={{
        background: 'var(--surface-container-lowest)',
        border: '1px solid var(--outline-variant)',
        borderRadius: 'var(--radius-md)',
        overflow: 'hidden',
      }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: 'var(--surface-container-low)' }}>
              {['TÊN TÀI LIỆU', 'CHỦ ĐỀ', 'NĂM', 'NGÀY THÊM', 'KÍCH THƯỚC', 'TRẠNG THÁI AI', 'THAO TÁC'].map(h => (
                <th key={h} style={{
                  padding: '10px 14px',
                  textAlign: 'left',
                  fontFamily: 'var(--font-label)',
                  fontSize: '11px',
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
                <td colSpan={7} style={{ padding: '32px', textAlign: 'center', color: 'var(--on-surface-variant)', fontSize: '14px' }}>
                  <div style={{ display: 'inline-block', width: '24px', height: '24px', border: '3px solid var(--primary)', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite', marginBottom: '8px' }} />
                  <div>Đang tải tài nguyên nghiên cứu...</div>
                </td>
              </tr>
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ padding: '32px', textAlign: 'center', color: 'var(--on-surface-variant)', fontSize: '13.5px' }}>
                  Không tìm thấy tài liệu nào trong thư viện.
                </td>
              </tr>
            ) : (
              filtered.map((doc, i) => {
                const st = AI_STATUS[doc.status] || AI_STATUS.pending;
                return (
                  <tr key={`${doc.id}-${i}`} style={{
                    borderBottom: i < filtered.length - 1 ? '1px solid var(--surface-container-high)' : 'none',
                    transition: 'background 0.12s',
                  }}
                    onMouseEnter={e => (e.currentTarget.style.background = 'var(--surface-container-low)')}
                    onMouseLeave={e => (e.currentTarget.style.background = '')}
                  >
                    <td style={{ padding: '12px 14px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
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
                        <span style={{ fontSize: '13px', fontWeight: 500, color: 'var(--on-surface)' }}>
                          {doc.name.length > 40 ? doc.name.slice(0, 40) + '...' : doc.name}
                        </span>
                      </div>
                    </td>
                    <td style={{ padding: '12px 14px', fontSize: '12.5px', color: 'var(--on-surface-variant)' }}>
                      <span style={{
                        padding: '2px 6px',
                        borderRadius: 'var(--radius-xs)',
                        background: 'var(--secondary-container)',
                        color: 'var(--secondary)',
                        fontSize: '11px',
                        fontWeight: 600,
                        textTransform: 'uppercase',
                      }}>
                        {doc.author}
                      </span>
                    </td>
                    <td style={{ padding: '12px 14px', fontSize: '12.5px', color: 'var(--on-surface-variant)' }}>
                      {doc.year}
                    </td>
                    <td style={{ padding: '12px 14px', fontSize: '12.5px', color: 'var(--on-surface-variant)' }}>
                      {doc.date}
                    </td>
                    <td style={{ padding: '12px 14px', fontSize: '12.5px', color: 'var(--on-surface-variant)' }}>
                      {doc.size}
                    </td>
                    <td style={{ padding: '12px 14px' }}>
                      <span style={{
                        display: 'inline-flex', alignItems: 'center', gap: '4px',
                        padding: '3px 9px',
                        background: st.bg, color: st.color,
                        borderRadius: '99px',
                        fontSize: '11.5px', fontFamily: 'var(--font-label)', fontWeight: 600,
                      }}>
                        {doc.status === 'done' && '✓ '}{st.label}
                      </span>
                    </td>
                    <td style={{ padding: '12px 14px' }}>
                      <button className="btn-icon" title="Thao tác" id={`doc-action-${doc.id}`}>
                        <EllipsisIcon />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>

        {/* Pagination row */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '10px 14px',
          borderTop: '1px solid var(--outline-variant)',
          fontSize: '12.5px',
          color: 'var(--on-surface-variant)',
        }}>
          <span>Hiển thị <strong>{filtered.length}</strong> tài liệu</span>
          <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
            <span>Tổng số: <strong>{filtered.length}</strong></span>
          </div>
        </div>
      </div>
    </div>
  );
}
