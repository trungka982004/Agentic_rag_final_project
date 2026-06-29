'use client';

import { useState } from 'react';

// Stitch screen: "Thiết lập & Dữ liệu học thuật"
// Layout: 2-column, left=Account Info + Security, right=Academic Sync + Performance

const Toggle = ({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) => (
  <label className="toggle" style={{ cursor: 'pointer' }}>
    <input type="checkbox" checked={checked} onChange={e => onChange(e.target.checked)} />
    <span className="toggle-slider" />
  </label>
);

const StatusBadge = ({ status }: { status: 'connected' | 'pending' | 'disconnected' }) => {
  const map = {
    connected:    { label: 'Đang kết nối', bg: 'var(--success-container)', color: 'var(--success)' },
    pending:      { label: 'Re-auth', bg: 'var(--warning-container)', color: 'var(--warning)' },
    disconnected: { label: 'Chưa kết nối', bg: 'var(--surface-container)', color: 'var(--on-surface-variant)' },
  }[status];
  return (
    <span style={{
      fontSize: '11px', fontFamily: 'var(--font-label)', fontWeight: 600,
      padding: '2px 8px', borderRadius: '99px',
      background: map.bg, color: map.color,
    }}>
      {map.label}
    </span>
  );
};

export default function GeneralSettingPage() {
  const [gpuBoost, setGpuBoost] = useState(true);
  const [autoPreload, setAutoPreload] = useState(true);
  const [offlineMode, setOfflineMode] = useState(false);

  const academicServices = [
    { name: 'Zotero Integration', id: 'zotero',   status: 'connected' as const,    detail: 'Đồng bộ tới 5 gần nhất', lastSync: '—' },
    { name: 'Mendeley Cloud',     id: 'mendeley',  status: 'pending' as const,      detail: 'Yêu cầu xác thực lại', lastSync: '—' },
    { name: 'Google Scholar',     id: 'scholar',   status: 'disconnected' as const, detail: 'Chưa kết nối', lastSync: '—' },
  ];

  return (
    <div style={{ maxWidth: '900px' }}>
      {/* Page header */}
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 700, color: 'var(--on-surface)' }}>
          Thiết lập &amp; Dữ liệu học thuật
        </h1>
        <p style={{ color: 'var(--on-surface-variant)', fontSize: '14px', marginTop: '4px' }}>
          Quản lý thông tin tài khoản, tích hợp cơ sở dữ liệu và cấu hình hệ thống nghiên cứu.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>

        {/* ── LEFT: Account Info ── */}
        <div>
          <div className="card" style={{ marginBottom: '0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <div style={{
                width: '32px', height: '32px',
                background: 'var(--primary-fixed)',
                borderRadius: 'var(--radius-sm)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--primary-container)"
                  strokeWidth="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8" /></svg>
              </div>
              <div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--on-surface)' }}>Thông tin tài khoản</div>
                <span style={{
                  fontSize: '10.5px', fontFamily: 'var(--font-label)', fontWeight: 600,
                  background: 'var(--success-container)', color: 'var(--success)',
                  padding: '1px 7px', borderRadius: '99px',
                }}>● Đang hoạt động</span>
              </div>
            </div>

            {[
              { label: 'Họ và tên', value: 'TS. Nguyễn Văn A' },
              { label: 'Học vị', value: 'Tiến sĩ (TS.)' },
              { label: 'Chức danh', value: 'Giảng viên cao cấp' },
              { label: 'Đơn vị công tác', value: 'Đại học Quốc gia Hà Nội' },
            ].map(f => (
              <div key={f.label} style={{ marginBottom: '12px' }}>
                <label style={{ fontSize: '12px', color: 'var(--on-surface-variant)', display: 'block', marginBottom: '4px' }}>
                  {f.label}
                </label>
                <input className="input" defaultValue={f.value} style={{ fontSize: '13.5px' }} />
              </div>
            ))}
          </div>

          {/* Security */}
          <div className="card" style={{ marginTop: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--on-surface-variant)"
                strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /></svg>
              <span style={{ fontSize: '13.5px', fontWeight: 600, color: 'var(--on-surface)' }}>Bảo mật tài khoản</span>
            </div>
            <p style={{ fontSize: '12.5px', color: 'var(--on-surface-variant)', marginBottom: '12px' }}>
              Lần đổi mật khẩu cuối: <strong>45 ngày trước</strong>.
            </p>
            <button className="btn btn-secondary" style={{ width: '100%', justifyContent: 'center', gap: '6px' }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M15 7h3a5 5 0 0 1 5 5 5 5 0 0 1-5 5h-3M9 7H6a5 5 0 0 0-5 5 5 5 0 0 0 5 5h3M8 12h8" />
              </svg>
              Đổi mật khẩu tài khoản
            </button>
          </div>
        </div>

        {/* ── RIGHT: Academic Sync + Performance ── */}
        <div>
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <div style={{ fontSize: '13.5px', fontWeight: 600, color: 'var(--on-surface)' }}>Đồng bộ học thuật</div>
              <button className="btn btn-secondary" style={{ fontSize: '12px', padding: '4px 10px' }}>Auto-sync</button>
            </div>

            {academicServices.map(svc => (
              <div key={svc.id} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '10px 0',
                borderBottom: '1px solid var(--surface-container-high)',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{
                    width: '28px', height: '28px',
                    background: 'var(--surface-container)',
                    borderRadius: 'var(--radius-sm)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontWeight: 800, fontSize: '13px', color: 'var(--primary-container)',
                    fontFamily: 'var(--font-display)',
                  }}>
                    {svc.name[0]}
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--on-surface)' }}>{svc.name}</div>
                    <div style={{ fontSize: '11.5px', color: 'var(--on-surface-variant)' }}>{svc.detail}</div>
                  </div>
                </div>
                <StatusBadge status={svc.status} />
              </div>
            ))}
          </div>

          {/* Performance options */}
          <div className="card" style={{ marginTop: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--on-surface-variant)"
                strokeWidth="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" /></svg>
              <span style={{ fontSize: '13.5px', fontWeight: 600, color: 'var(--on-surface)' }}>Tùy chọn hiệu suất</span>
            </div>

            {[
              { label: 'Tăng tốc độ phân tích', desc: 'Sử dụng tài nguyên GPU cho các mô hình AI', val: gpuBoost, set: setGpuBoost },
              { label: 'Tự động phân tích tài liệu', desc: 'Tải lên để tự động hàng ngày mỗi hôm', val: autoPreload, set: setAutoPreload },
              { label: 'Tối ưu băng thông mạng', desc: 'Nén nội dung truyền tải khi kết nối chậm', val: offlineMode, set: setOfflineMode },
            ].map(t => (
              <div key={t.label} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '10px 0',
                borderBottom: '1px solid var(--surface-container-high)',
              }}>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--on-surface)' }}>{t.label}</div>
                  <div style={{ fontSize: '11.5px', color: 'var(--on-surface-variant)', marginTop: '2px' }}>{t.desc}</div>
                </div>
                <Toggle checked={t.val} onChange={t.set} />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Action buttons — Stitch: "Huỷ thay đổi" + "Lưu cấu hình" */}
      <div style={{
        display: 'flex', justifyContent: 'flex-end', gap: '10px',
        marginTop: '24px', paddingTop: '20px',
        borderTop: '1px solid var(--outline-variant)',
      }}>
        <button className="btn btn-secondary" id="settings-cancel-btn">Huỷ thay đổi</button>
        <button className="btn btn-primary" id="settings-save-btn">Lưu cấu hình</button>
      </div>
    </div>
  );
}
