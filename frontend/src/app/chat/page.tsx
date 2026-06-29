'use client';

// /chat — empty state when no session is selected
export default function ChatIndexPage() {
  return (
    <div style={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '20px',
      textAlign: 'center',
      padding: '40px',
      color: 'var(--text-muted)',
    }}>
      {/* Decorative orb */}
      <div style={{
        width: '100px',
        height: '100px',
        borderRadius: '50%',
        background: 'radial-gradient(circle at 40% 35%, rgba(59,130,246,0.25) 0%, rgba(139,92,246,0.12) 60%, transparent 100%)',
        border: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '2.4em',
        boxShadow: '0 0 40px rgba(59,130,246,0.15)',
        animation: 'glow-pulse 3s infinite',
      }}>
        🧠
      </div>

      <div>
        <h2 style={{
          fontSize: '1.15em',
          fontWeight: 600,
          marginBottom: '8px',
          background: 'linear-gradient(135deg, #93c5fd, #a78bfa)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }}>
          Chọn hoặc tạo cuộc hội thoại
        </h2>
        <p style={{ fontSize: '0.85em', color: 'var(--text-muted)', maxWidth: '320px', lineHeight: 1.6 }}>
          Chọn một phiên hội thoại ở thanh bên trái, hoặc nhấn{' '}
          <strong style={{ color: 'var(--text-secondary)' }}>Cuộc hội thoại mới</strong>{' '}
          để bắt đầu đặt câu hỏi.
        </p>
      </div>

      {/* Feature highlights */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '12px',
        maxWidth: '480px',
        marginTop: '8px',
      }}>
        {[
          { icon: '📚', label: 'RAG cục bộ', desc: 'Truy vấn tài liệu học thuật' },
          { icon: '🌐', label: 'Tìm kiếm web', desc: 'Dự phòng khi không có dữ liệu' },
          { icon: '🐍', label: 'Python REPL', desc: 'Thực thi code và tính toán' },
          { icon: '📊', label: 'Google Export', desc: 'Xuất báo cáo Docs/Sheets' },
        ].map(f => (
          <div key={f.label} style={{
            padding: '14px',
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            textAlign: 'left',
          }}>
            <div style={{ fontSize: '1.2em', marginBottom: '4px' }}>{f.icon}</div>
            <div style={{ fontSize: '0.78em', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '2px' }}>{f.label}</div>
            <div style={{ fontSize: '0.72em', color: 'var(--text-muted)' }}>{f.desc}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
