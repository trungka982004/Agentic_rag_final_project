'use client';

import { useState } from 'react';

const faqs = [
  {
    q: 'Làm thế nào để kết nối thư viện Zotero của tôi?',
    a: 'Truy cập Cấu hình hệ thống > Tích hợp > Chọn Zotero và nhập API Key của bạn.'
  },
  {
    q: 'Dung lượng file PDF tối đa hệ thống hỗ trợ bao nhiêu?',
    a: 'Hiện tại chúng tôi hỗ trợ các tệp lên đến 50MB mỗi tệp để đảm bảo tốc độ phân tích tối ưu.'
  },
  {
    q: 'Làm thế nào để thay đổi định dạng của trích dẫn?',
    a: 'Vào phần Trích dẫn, chọn phong cách (APA, IEEE, Harvard…) trong danh sách thả xuống phía trên bảng.'
  },
  {
    q: 'Agent AI mất bao lâu để phân tích một tài liệu?',
    a: 'Thường mất 30 giây đến 2 phút tùy kích thước tài liệu. Bạn sẽ thấy trạng thái "Đang phân tích" trong Thư viện.'
  },
  {
    q: 'Tôi có thể xuất kết quả nghiên cứu sang Google Docs không?',
    a: 'Có. Sau khi agent tạo báo cáo, nhấn nút "Xuất Google Docs" hiện ra dưới câu trả lời trong cửa sổ chat.'
  },
];

const docs = [
  { icon: '📄', title: 'Cẩm nang sử dụng', size: '2.1 MB', type: 'PDF' },
  { icon: '❓', title: 'Tài liệu trợ giúp hệ thống', size: '1.8 MB', type: 'PDF' },
];

const CATEGORIES = [
  'Lỗi đồng bộ tài liệu',
  'Lỗi kết nối API',
  'Vấn đề hiển thị',
  'Góp ý tính năng mới',
  'Khác',
];

export default function SupportPage() {
  const [openIdx, setOpenIdx] = useState<number | null>(null);
  const [category, setCategory] = useState(CATEGORIES[0]);
  const [message, setMessage] = useState('');
  const [sent, setSent] = useState(false);

  const handleSend = () => {
    if (!message.trim()) return;
    setSent(true);
    setTimeout(() => setSent(false), 3000);
    setMessage('');
  };

  return (
    <div style={{
      maxWidth: '960px',
      margin: '0 auto',
      width: '100%',
    }}>
      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 700, color: 'var(--on-surface)' }}>
          Trợ giúp &amp; Hỗ trợ
        </h1>
        <p style={{ color: 'var(--on-surface-variant)', fontSize: '14px', marginTop: '4px', maxWidth: '540px' }}>
          Tìm câu trả lời cho các thắc mắc thường gặp, tải tài liệu hướng dẫn hoặc liên hệ kỹ thuật.
        </p>
      </div>

      {/* Two-column layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>

        {/* Left: FAQ */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <div style={{
              width: '32px', height: '32px',
              background: 'var(--primary-fixed)',
              borderRadius: 'var(--radius-sm)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--primary-container)" strokeWidth="2">
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3M12 17h.01" strokeLinecap="round" strokeLinejoin="round" />
                <circle cx="12" cy="12" r="10" />
              </svg>
            </div>
            <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--on-surface)', fontFamily: 'var(--font-display)' }}>
              Câu hỏi thường gặp
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {faqs.map((faq, i) => (
              <div key={i} style={{
                border: '1px solid var(--outline-variant)',
                borderRadius: 'var(--radius-sm)',
                overflow: 'hidden',
              }}>
                <button
                  onClick={() => setOpenIdx(openIdx === i ? null : i)}
                  id={`faq-toggle-${i}`}
                  style={{
                    width: '100%', textAlign: 'left',
                    padding: '12px 14px',
                    background: 'var(--surface-container-lowest)',
                    border: 'none', cursor: 'pointer',
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    gap: '8px',
                  }}
                >
                  <span style={{ fontSize: '13.5px', fontWeight: 600, color: 'var(--on-surface)', lineHeight: '1.4' }}>
                    {faq.q}
                  </span>
                  <span style={{
                    color: 'var(--primary-container)', fontSize: '16px', flexShrink: 0,
                    transform: openIdx === i ? 'rotate(90deg)' : 'none',
                    transition: 'transform 0.15s',
                  }}>›</span>
                </button>
                {openIdx === i && (
                  <div style={{
                    padding: '10px 14px 14px',
                    fontSize: '13.5px', lineHeight: '1.7',
                    color: 'var(--on-surface-variant)',
                    background: 'var(--surface-container-low)',
                    borderTop: '1px solid var(--outline-variant)',
                  }}>
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>

          <button style={{
            marginTop: '14px',
            background: 'none', border: 'none', cursor: 'pointer',
            color: 'var(--primary-container)', fontSize: '13px',
            fontFamily: 'var(--font-body)', padding: 0,
          }}>
            Xem tất cả câu hỏi →
          </button>
        </div>

        {/* Right: Documentation */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <div style={{
              width: '32px', height: '32px',
              background: 'var(--secondary-container)',
              borderRadius: 'var(--radius-sm)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--on-secondary-container)" strokeWidth="2">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--on-surface)', fontFamily: 'var(--font-display)' }}>
              Tài liệu hướng dẫn
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px' }}>
            {docs.map((doc, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', gap: '12px',
                padding: '10px 12px',
                border: '1px solid var(--outline-variant)',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--surface-container-lowest)',
                cursor: 'pointer',
                transition: 'background 0.12s',
              }}
                onMouseEnter={e => (e.currentTarget.style.background = 'var(--surface-container-low)')}
                onMouseLeave={e => (e.currentTarget.style.background = 'var(--surface-container-lowest)')}
              >
                <div style={{
                  width: '32px', height: '32px',
                  background: 'var(--error-container)',
                  borderRadius: '4px',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '9px', fontWeight: 700, color: 'var(--error)',
                  fontFamily: 'var(--font-label)', flexShrink: 0,
                }}>PDF</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--on-surface)' }}>{doc.title}</div>
                  <div style={{ fontSize: '11.5px', color: 'var(--on-surface-variant)', marginTop: '2px' }}>{doc.size}</div>
                </div>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--primary-container)" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
            ))}
          </div>

          {/* Video tutorial placeholder */}
          <div style={{
            borderRadius: 'var(--radius-sm)',
            overflow: 'hidden',
            border: '1px solid var(--outline-variant)',
            position: 'relative',
          }}>
            <div style={{
              background: 'linear-gradient(135deg, #1e3a5f 0%, #0055d4 100%)',
              height: '100px',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexDirection: 'column', gap: '8px', cursor: 'pointer',
            }}>
              <div style={{
                width: '36px', height: '36px', borderRadius: '50%',
                background: 'rgba(255,255,255,0.2)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
                  <path d="M5 3l14 9-14 9V3z" />
                </svg>
              </div>
              <span style={{ color: 'rgba(255,255,255,0.9)', fontSize: '12px', fontWeight: 500 }}>
                Video hướng dẫn cơ bản
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Contact Support Form */}
      <div className="card">
        <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
          {/* Left: contact info */}
          <div style={{ flex: '0 0 240px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <div style={{
                width: '32px', height: '32px',
                background: 'var(--primary-fixed)',
                borderRadius: 'var(--radius-sm)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--primary-container)" strokeWidth="2">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" strokeLinecap="round" strokeLinejoin="round" />
                  <polyline points="22,6 12,13 2,6" />
                </svg>
              </div>
              <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--on-surface)', fontFamily: 'var(--font-display)' }}>
                Gửi yêu cầu hỗ trợ
              </span>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--on-surface-variant)', lineHeight: '1.6', marginBottom: '16px' }}>
              Đội ngũ kỹ thuật sẽ xem xét và phản hồi yêu cầu của bạn trong vòng 24 giờ làm việc. Vui lòng cung cấp chi tiết để được hỗ trợ tốt nhất.
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: 'var(--on-surface-variant)' }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" strokeLinecap="round" />
                  <polyline points="22,6 12,13 2,6" />
                </svg>
                support@intelligentagent.edu.vn
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: 'var(--on-surface-variant)' }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 13a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3.6 2.18h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z" strokeLinecap="round" />
                </svg>
                +84 (024) 1234 5678
              </div>
            </div>
          </div>

          {/* Right: form */}
          <div style={{ flex: 1, minWidth: '280px' }}>
            <div style={{ marginBottom: '12px' }}>
              <label style={{ display: 'block', fontSize: '12.5px', color: 'var(--on-surface-variant)', marginBottom: '5px' }}>
                Chủ đề
              </label>
              <select
                id="support-category"
                value={category}
                onChange={e => setCategory(e.target.value)}
                style={{
                  width: '100%', padding: '9px 12px',
                  border: '1px solid var(--outline-variant)',
                  borderRadius: 'var(--radius-sm)',
                  background: 'var(--surface-container-lowest)',
                  color: 'var(--on-surface)', fontSize: '13.5px',
                  fontFamily: 'var(--font-body)', outline: 'none', cursor: 'pointer',
                }}
              >
                {CATEGORIES.map(c => <option key={c}>{c}</option>)}
              </select>
            </div>

            <div style={{ marginBottom: '12px' }}>
              <label style={{ display: 'block', fontSize: '12.5px', color: 'var(--on-surface-variant)', marginBottom: '5px' }}>
                Mô tả vấn đề gặp phải
              </label>
              <textarea
                id="support-message"
                rows={4}
                value={message}
                onChange={e => setMessage(e.target.value)}
                placeholder="Vui lòng mô tả vấn đề bạn gặp phải..."
                style={{
                  width: '100%', padding: '9px 12px',
                  border: '1px solid var(--outline-variant)',
                  borderRadius: 'var(--radius-sm)',
                  background: 'var(--surface-container-lowest)',
                  color: 'var(--on-surface)', fontSize: '13.5px',
                  fontFamily: 'var(--font-body)', outline: 'none',
                  resize: 'vertical', lineHeight: '1.6',
                  boxSizing: 'border-box',
                }}
              />
            </div>

            {sent && (
              <div style={{
                padding: '10px 14px', marginBottom: '10px',
                background: 'var(--success-container)',
                color: 'var(--success)',
                borderRadius: 'var(--radius-sm)',
                fontSize: '13.5px', fontWeight: 500,
              }}>
                ✓ Yêu cầu đã được gửi thành công. Chúng tôi sẽ phản hồi sớm nhất có thể!
              </div>
            )}

            <button
              className="btn btn-primary"
              id="support-submit-btn"
              onClick={handleSend}
              style={{ fontSize: '13px', gap: '6px' }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
              Gửi yêu cầu hỗ trợ
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        marginTop: '20px', paddingTop: '16px',
        borderTop: '1px solid var(--outline-variant)',
        fontSize: '12px', color: 'var(--on-surface-variant)',
        flexWrap: 'wrap', gap: '8px',
      }}>
        <div style={{ display: 'flex', gap: '16px' }}>
          {['Điều khoản dịch vụ', 'Chính sách bảo mật', 'Cộng đồng nghiên cứu'].map(l => (
            <button key={l} style={{
              background: 'none', border: 'none', cursor: 'pointer',
              color: 'var(--on-surface-variant)', fontSize: '12px',
              fontFamily: 'var(--font-body)',
              textDecoration: 'underline', textUnderlineOffset: '2px',
            }}>
              {l}
            </button>
          ))}
        </div>
        <span>© 2024 Intelligent Research Agent. All rights reserved.</span>
      </div>
    </div>
  );
}
