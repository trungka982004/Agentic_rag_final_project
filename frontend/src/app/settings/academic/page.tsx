'use client';

// Stitch screen: "Kết nối học thuật — Academic Integration"
// 2x2 grid: Zotero (connected), Mendeley (connected), Google Scholar (disconnected), ORCID ID (form)

import { useState } from 'react';

interface ServiceCardProps {
  id: string;
  logo: string;
  name: string;
  status: 'connected' | 'disconnected';
  account?: string;
  lastSync?: string;
  description?: string;
  onSync: () => void;
  onDisconnect: () => void;
  onConnect: () => void;
}

const Toggle = ({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) => (
  <label className="toggle" style={{ cursor: 'pointer' }}>
    <input type="checkbox" checked={checked} onChange={e => onChange(e.target.checked)} />
    <span className="toggle-slider" />
  </label>
);

function ServiceCard({ id, logo, name, status, account, lastSync, description, onSync, onDisconnect, onConnect }: ServiceCardProps) {
  const [autoSync, setAutoSync] = useState(status === 'connected');

  return (
    <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', marginBottom: '14px' }}>
        {/* Logo */}
        <div style={{
          width: '36px', height: '36px',
          background: status === 'connected' ? 'var(--primary-fixed)' : 'var(--surface-container)',
          borderRadius: 'var(--radius-sm)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontWeight: 800, fontSize: '16px',
          color: status === 'connected' ? 'var(--primary-container)' : 'var(--on-surface-variant)',
          fontFamily: 'var(--font-display)',
          flexShrink: 0,
        }}>
          {logo}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--on-surface)' }}>{name}</span>
            <span style={{
              fontSize: '10.5px', fontFamily: 'var(--font-label)', fontWeight: 700,
              padding: '2px 7px', borderRadius: '99px',
              background: status === 'connected' ? 'var(--success-container)' : 'var(--surface-container)',
              color: status === 'connected' ? 'var(--success)' : 'var(--on-surface-variant)',
            }}>
              {status === 'connected' ? '● ĐANG KẾT NỐI' : '○ CHƯA KẾT NỐI'}
            </span>
          </div>
          {account && (
            <div style={{ fontSize: '12px', color: 'var(--on-surface-variant)', marginTop: '3px' }}>{account}</div>
          )}
        </div>
        {status === 'connected' && (
          <Toggle checked={autoSync} onChange={setAutoSync} />
        )}
      </div>

      {status === 'connected' ? (
        <>
          <div style={{
            display: 'grid', gridTemplateColumns: '1fr 1fr',
            gap: '8px', marginBottom: '14px',
          }}>
            <div style={{
              background: 'var(--surface-container-low)',
              borderRadius: 'var(--radius-sm)',
              padding: '8px 10px',
            }}>
              <div style={{ fontSize: '11px', color: 'var(--on-surface-variant)' }}>Tài khoản</div>
              <div style={{ fontSize: '12.5px', fontWeight: 500, color: 'var(--on-surface)', marginTop: '2px' }}>{account}</div>
            </div>
            <div style={{
              background: 'var(--surface-container-low)',
              borderRadius: 'var(--radius-sm)',
              padding: '8px 10px',
            }}>
              <div style={{ fontSize: '11px', color: 'var(--on-surface-variant)' }}>Cập nhật lần cuối</div>
              <div style={{ fontSize: '12.5px', fontWeight: 500, color: 'var(--on-surface)', marginTop: '2px' }}>{lastSync}</div>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '8px', marginTop: 'auto' }}>
            <button className="btn btn-secondary" style={{ flex: 1, justifyContent: 'center', fontSize: '13px' }}
              id={`${id}-sync-btn`} onClick={onSync}>
              Đồng bộ ngay
            </button>
            <button className="btn btn-danger" style={{ flex: 1, justifyContent: 'center', fontSize: '13px' }}
              id={`${id}-disconnect-btn`} onClick={onDisconnect}>
              Ngắt kết nối
            </button>
          </div>
        </>
      ) : (
        <>
          {description && (
            <p style={{ fontSize: '12.5px', color: 'var(--on-surface-variant)', lineHeight: '1.6', marginBottom: '12px', flex: 1 }}>
              {description}
            </p>
          )}
          <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', fontSize: '13px' }}
            id={`${id}-connect-btn`} onClick={onConnect}>
            Kết nối tài khoản
          </button>
        </>
      )}
    </div>
  );
}

export default function AcademicIntegrationPage() {
  const [orcid, setOrcid] = useState('');

  return (
    <div style={{ maxWidth: '880px' }}>
      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 700, color: 'var(--on-surface)' }}>
          Kết nối học thuật
        </h1>
        <p style={{ color: 'var(--on-surface-variant)', fontSize: '14px', marginTop: '4px', maxWidth: '560px' }}>
          Quản lý và đồng bộ hóa các tài khoản nghiên cứu của bạn. Kết nối với các thư viện số và cơ sở dữ
          liệu học thuật để tự động hóa quy trình thu thập tài liệu.
        </p>
      </div>

      {/* 2x2 service grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
        <ServiceCard
          id="zotero"
          logo="Z"
          name="Zotero"
          status="connected"
          account="nguyenvana_academic"
          lastSync="Tự động đồng bộ"
          onSync={() => {}} onDisconnect={() => {}} onConnect={() => {}}
        />
        <ServiceCard
          id="mendeley"
          logo="M"
          name="Mendeley"
          status="connected"
          account="a.nguyen@mendeley.org"
          lastSync="1 giờ trước"
          onSync={() => {}} onDisconnect={() => {}} onConnect={() => {}}
        />
        <ServiceCard
          id="scholar"
          logo="G"
          name="Google Scholar"
          status="disconnected"
          description="Kết nối để tự động cập nhật danh sách trích dẫn và các bài báo từ Google Scholar vào hệ thống."
          onSync={() => {}} onDisconnect={() => {}} onConnect={() => {}}
        />

        {/* ORCID Card */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
            <div style={{
              width: '36px', height: '36px',
              background: 'var(--success-container)',
              borderRadius: 'var(--radius-sm)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '10px', fontWeight: 800, color: 'var(--success)',
              fontFamily: 'var(--font-display)',
            }}>
              iD
            </div>
            <div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--on-surface)' }}>ORCID ID</div>
              <div style={{ fontSize: '11.5px', color: 'var(--on-surface-variant)' }}>
                Xác thực danh tính nhà nghiên cứu học thuật
              </div>
            </div>
          </div>
          <label style={{ fontSize: '12px', color: 'var(--on-surface-variant)', display: 'block', marginBottom: '6px' }}>
            Mã số ORCID
          </label>
          <input
            id="orcid-input"
            className="input"
            value={orcid}
            onChange={e => setOrcid(e.target.value)}
            placeholder="0000-0000-0000-0000"
            style={{ marginBottom: '12px', fontFamily: 'monospace', letterSpacing: '0.05em' }}
          />
          <button
            className="btn btn-secondary"
            style={{ width: '100%', justifyContent: 'center', fontSize: '13px' }}
            id="orcid-verify-btn"
          >
            Xác thực &amp; Kết nối
          </button>
        </div>
      </div>

      {/* Footer actions */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingTop: '20px',
        borderTop: '1px solid var(--outline-variant)',
      }}>
        <button className="upgrade-btn" style={{ width: 'auto', padding: '8px 20px' }}
          id="academic-upgrade-btn">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Nâng cấp Premium
        </button>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn btn-secondary" id="academic-back-btn">← Quay lại</button>
          <button className="btn btn-primary" id="academic-save-btn">Lưu thiết lập kết nối</button>
        </div>
      </div>
    </div>
  );
}
