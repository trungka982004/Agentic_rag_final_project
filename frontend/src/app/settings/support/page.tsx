'use client';

// Support page stub
export default function SupportPage() {
  const FAQS = [
    { q: 'Hệ thống hỗ trợ định dạng tài liệu nào?', a: 'PDF, DOCX, TXT, Markdown, LaTeX. Tối đa 50MB mỗi tệp.' },
    { q: 'RAG hoạt động như thế nào?', a: 'Hệ thống chunk tài liệu → tạo embedding → lưu vào vector store. Khi hỏi, agent tìm kiếm các chunk liên quan và tổng hợp câu trả lời.' },
    { q: 'Làm sao xuất kết quả sang Google Docs?', a: 'Sau khi agent tạo báo cáo, nhấn nút "Xuất Google Docs" hiện ra dưới câu trả lời.' },
    { q: 'Dữ liệu nghiên cứu của tôi có được bảo mật không?', a: 'Có. Dữ liệu được lưu trữ trong hệ thống riêng và không chia sẻ với bên thứ ba.' },
  ];

  return (
    <div style={{ maxWidth: '720px' }}>
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 700, color: 'var(--on-surface)' }}>
          Trợ giúp &amp; Hỗ trợ
        </h1>
        <p style={{ color: 'var(--on-surface-variant)', fontSize: '14px', marginTop: '4px' }}>
          Tài liệu hướng dẫn và câu hỏi thường gặp về hệ thống.
        </p>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {FAQS.map((faq, i) => (
          <details key={i} style={{ border: '1px solid var(--outline-variant)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
            <summary style={{
              padding: '14px 18px',
              fontSize: '14px', fontWeight: 600, color: 'var(--on-surface)',
              cursor: 'pointer',
              background: 'var(--surface-container-lowest)',
              listStyle: 'none',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            }}>
              {faq.q}
              <span style={{ color: 'var(--primary-container)', fontSize: '16px' }}>›</span>
            </summary>
            <div style={{
              padding: '12px 18px 16px',
              fontSize: '14px', lineHeight: '1.7',
              color: 'var(--on-surface-variant)',
              background: 'var(--surface-container-low)',
              borderTop: '1px solid var(--outline-variant)',
            }}>
              {faq.a}
            </div>
          </details>
        ))}
      </div>
    </div>
  );
}
