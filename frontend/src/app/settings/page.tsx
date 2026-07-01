'use client';

import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';

// ── Icon helper ──────────────────────────────────────────────────────────────
const Icon = ({ path, size = 15 }: { path: string; size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d={path} />
  </svg>
);

// ── Summary Card ─────────────────────────────────────────────────────────────
function SummaryCard({
  title, icon, href, children,
}: {
  title: string;
  icon: string;
  href: string;
  children: React.ReactNode;
}) {
  return (
    <div className="card" style={{ position: 'relative' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '30px', height: '30px',
            background: 'var(--primary-fixed)',
            borderRadius: 'var(--radius-sm)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Icon path={icon} size={14} />
          </div>
          <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--on-surface)', fontFamily: 'var(--font-display)' }}>
            {title}
          </span>
        </div>
        <Link href={href} style={{
          fontSize: '12px', color: 'var(--primary-container)',
          textDecoration: 'none', fontFamily: 'var(--font-body)',
          display: 'flex', alignItems: 'center', gap: '4px',
        }}>
          Chỉnh sửa →
        </Link>
      </div>
      {children}
    </div>
  );
}

// ── Row item inside a summary card ──────────────────────────────────────────
function InfoRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div style={{
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      padding: '8px 0', borderBottom: '1px solid var(--surface-container-high)',
      fontSize: '13.5px',
    }}>
      <span style={{ color: 'var(--on-surface-variant)', minWidth: '160px' }}>{label}</span>
      <span style={{ color: 'var(--on-surface)', fontWeight: 500, textAlign: 'right' }}>{value}</span>
    </div>
  );
}

// ── Main page ────────────────────────────────────────────────────────────────
export default function GeneralOverviewPage() {
  const { user } = useAuth();

  const initial = user?.email?.[0]?.toUpperCase() ?? 'U';
  const emailPrefix = user?.email?.split('@')[0] ?? 'Người dùng';

  return (
    <div style={{ maxWidth: '860px' }}>
      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 700, color: 'var(--on-surface)' }}>
          Cấu hình chung
        </h1>
        <p style={{ color: 'var(--on-surface-variant)', fontSize: '14px', marginTop: '4px' }}>
          Tổng quan về hồ sơ cá nhân và cấu hình hệ thống của bạn.
        </p>
      </div>

      {/* ── User Identity Banner ── */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: '16px',
        padding: '18px 20px', marginBottom: '20px',
        background: 'var(--primary-fixed)',
        border: '1px solid var(--primary-fixed-dim)',
        borderRadius: 'var(--radius-md)',
      }}>
        <div style={{
          width: '52px', height: '52px', flexShrink: 0,
          background: 'var(--primary-container)',
          borderRadius: '50%',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '20px', fontWeight: 700, color: 'var(--on-primary)',
          border: '3px solid rgba(255,255,255,0.3)',
        }}>
          {initial}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--on-surface)', fontFamily: 'var(--font-display)' }}>
            TS. Nguyễn Văn A
          </div>
          <div style={{ fontSize: '13px', color: 'var(--on-surface-variant)', marginTop: '2px' }}>
            {user?.email ?? 'Chưa đăng nhập'} · Tiến sĩ / Phó Giáo sư
          </div>
          <div style={{ marginTop: '6px' }}>
            <span style={{
              fontSize: '11px', fontFamily: 'var(--font-label)', fontWeight: 600,
              background: 'var(--success-container)', color: 'var(--success)',
              padding: '2px 8px', borderRadius: '99px',
            }}>● Đang hoạt động</span>
          </div>
        </div>
        <Link href="/settings/profile">
          <button className="btn btn-secondary" style={{ fontSize: '12.5px', gap: '5px' }}>
            <Icon path="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
            Chỉnh sửa hồ sơ
          </button>
        </Link>
      </div>

      {/* ── 2-column grid ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>

        {/* Personal Info summary */}
        <SummaryCard
          title="Thông tin cá nhân"
          icon="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8"
          href="/settings/profile"
        >
          <InfoRow label="Họ và tên" value="Nguyễn Văn A" />
          <InfoRow label="Chức danh / Học vị" value="Tiến sĩ / Phó Giáo sư" />
          <InfoRow label="Email học thuật" value="a.nguyen@academic.edu.vn" />
          <InfoRow label="Cơ quan / Tổ chức" value="Viện CNTT – Viện Hàn lâm KH&CN VN" />
          <InfoRow label="Lĩnh vực nghiên cứu" value={
            <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
              {['AI', 'NLP', 'Học sâu'].map(t => (
                <span key={t} className="chip" style={{ fontSize: '11px' }}>{t}</span>
              ))}
            </div>
          } />
        </SummaryCard>

        {/* Security summary */}
        <SummaryCard
          title="Bảo mật & Kết nối"
          icon="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"
          href="/settings/profile"
        >
          <InfoRow label="Xác thực 2 yếu tố" value={
            <span style={{
              fontSize: '11px', fontFamily: 'var(--font-label)', fontWeight: 600,
              background: 'var(--success-container)', color: 'var(--success)',
              padding: '2px 8px', borderRadius: '99px',
            }}>Đang bật</span>
          } />
          <InfoRow label="Zotero" value={
            <span style={{
              fontSize: '11px', fontFamily: 'var(--font-label)', fontWeight: 600,
              background: 'var(--success-container)', color: 'var(--success)',
              padding: '2px 8px', borderRadius: '99px',
            }}>Đang kết nối</span>
          } />
          <InfoRow label="Mendeley" value={
            <span style={{
              fontSize: '11px', fontFamily: 'var(--font-label)', fontWeight: 600,
              background: 'var(--success-container)', color: 'var(--success)',
              padding: '2px 8px', borderRadius: '99px',
            }}>Đang kết nối</span>
          } />
          <InfoRow label="Google Scholar" value={
            <span style={{
              fontSize: '11px', fontFamily: 'var(--font-label)', fontWeight: 600,
              background: 'var(--surface-container)', color: 'var(--on-surface-variant)',
              padding: '2px 8px', borderRadius: '99px',
            }}>Chưa kết nối</span>
          } />
          <div style={{ paddingTop: '8px' }}>
            <Link href="/settings/academic" style={{
              fontSize: '12.5px', color: 'var(--primary-container)',
              textDecoration: 'none',
            }}>
              Quản lý kết nối học thuật →
            </Link>
          </div>
        </SummaryCard>

        {/* LLM Config summary */}
        <SummaryCard
          title="Cấu hình AI hiện tại"
          icon="M13 2L3 14h9l-1 8 10-12h-9l1-8z"
          href="/settings/config"
        >
          <InfoRow label="Mô hình LLM" value="Qwen 2.5 (Mặc định)" />
          <InfoRow label="Temperature" value={
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                flex: 1, height: '4px', background: 'var(--outline-variant)',
                borderRadius: '2px', overflow: 'hidden', minWidth: '80px',
              }}>
                <div style={{
                  width: '20%', height: '100%',
                  background: 'var(--primary-container)',
                  borderRadius: '2px',
                }} />
              </div>
              <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>0.2</span>
            </div>
          } />
          <InfoRow label="Max Tokens" value={<span style={{ fontFamily: 'monospace' }}>2048</span>} />
          <InfoRow label="GPU Boost" value={
            <span style={{
              fontSize: '11px', fontFamily: 'var(--font-label)', fontWeight: 600,
              background: 'var(--success-container)', color: 'var(--success)',
              padding: '2px 8px', borderRadius: '99px',
            }}>Bật</span>
          } />
          <InfoRow label="Tự động phân tích" value={
            <span style={{
              fontSize: '11px', fontFamily: 'var(--font-label)', fontWeight: 600,
              background: 'var(--success-container)', color: 'var(--success)',
              padding: '2px 8px', borderRadius: '99px',
            }}>Bật</span>
          } />
        </SummaryCard>

        {/* Quick links */}
        <div className="card">
          <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--on-surface)', fontFamily: 'var(--font-display)', marginBottom: '14px' }}>
            Truy cập nhanh
          </div>
          {[
            { label: 'Thư viện tài liệu', desc: 'Quản lý tài liệu nghiên cứu', href: '/settings/library', icon: 'M3 3h4v18H3zM9 3h4v18H9zM15 3l4 1-1 17-4-1' },
            { label: 'Đoạn trích đã lưu', desc: 'Xem các ghi chú quan trọng', href: '/settings/snippets', icon: 'M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z' },
            { label: 'Trích dẫn khoa học', desc: 'Xuất danh mục tài liệu tham khảo', href: '/settings/citations', icon: 'M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z' },
            { label: 'Trợ giúp & Hỗ trợ', desc: 'Câu hỏi thường gặp & liên hệ', href: '/settings/support', icon: 'M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3M12 17h.01' },
          ].map(item => (
            <Link key={item.href} href={item.href} style={{ textDecoration: 'none' }}>
              <div style={{
                display: 'flex', alignItems: 'center', gap: '10px',
                padding: '10px 0',
                borderBottom: '1px solid var(--surface-container-high)',
                cursor: 'pointer',
                transition: 'opacity 0.12s',
              }}
                onMouseEnter={e => (e.currentTarget.style.opacity = '0.7')}
                onMouseLeave={e => (e.currentTarget.style.opacity = '1')}
              >
                <div style={{
                  width: '28px', height: '28px', flexShrink: 0,
                  background: 'var(--surface-container)',
                  borderRadius: 'var(--radius-sm)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: 'var(--primary-container)',
                }}>
                  <Icon path={item.icon} size={13} />
                </div>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--on-surface)' }}>{item.label}</div>
                  <div style={{ fontSize: '11.5px', color: 'var(--on-surface-variant)', marginTop: '1px' }}>{item.desc}</div>
                </div>
                <span style={{ marginLeft: 'auto', color: 'var(--on-surface-variant)', fontSize: '14px' }}>›</span>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
