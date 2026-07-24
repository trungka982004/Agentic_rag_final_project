'use client';

// Stitch screen: "Academic Integration"
// 2x2 grid: Zotero (connected), Mendeley (connected), Google Scholar (disconnected), ORCID ID (form)

import { useState } from 'react';
import { useRouter } from 'next/navigation';

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
  isProcessing?: boolean;
}

const Toggle = ({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) => (
  <label className="toggle" style={{ cursor: 'pointer' }}>
    <input type="checkbox" checked={checked} onChange={e => onChange(e.target.checked)} />
    <span className="toggle-slider" />
  </label>
);

function ServiceCard({ id, logo, name, status, account, lastSync, description, onSync, onDisconnect, onConnect, isProcessing }: ServiceCardProps) {
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
              {status === 'connected' ? '● CONNECTED' : '○ DISCONNECTED'}
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
              <div style={{ fontSize: '11px', color: 'var(--on-surface-variant)' }}>Account</div>
              <div style={{ fontSize: '12.5px', fontWeight: 500, color: 'var(--on-surface)', marginTop: '2px' }}>{account}</div>
            </div>
            <div style={{
              background: 'var(--surface-container-low)',
              borderRadius: 'var(--radius-sm)',
              padding: '8px 10px',
            }}>
              <div style={{ fontSize: '11px', color: 'var(--on-surface-variant)' }}>Last Updated</div>
              <div style={{ fontSize: '12.5px', fontWeight: 500, color: 'var(--on-surface)', marginTop: '2px' }}>{lastSync}</div>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '8px', marginTop: 'auto' }}>
            <button 
              className="btn btn-secondary" 
              style={{ flex: 1, justifyContent: 'center', fontSize: '13px', opacity: isProcessing ? 0.7 : 1 }}
              id={`${id}-sync-btn`} 
              onClick={onSync}
              disabled={isProcessing}
            >
              {isProcessing ? 'Syncing...' : 'Sync Now'}
            </button>
            <button 
              className="btn btn-danger" 
              style={{ flex: 1, justifyContent: 'center', fontSize: '13px', opacity: isProcessing ? 0.7 : 1 }}
              id={`${id}-disconnect-btn`} 
              onClick={onDisconnect}
              disabled={isProcessing}
            >
              Disconnect
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
          <button 
            className="btn btn-primary" 
            style={{ width: '100%', justifyContent: 'center', fontSize: '13px', opacity: isProcessing ? 0.7 : 1 }}
            id={`${id}-connect-btn`} 
            onClick={onConnect}
            disabled={isProcessing}
          >
            {isProcessing ? 'Connecting...' : 'Connect Account'}
          </button>
        </>
      )}
    </div>
  );
}

export default function AcademicIntegrationPage() {
  const router = useRouter();
  const [orcid, setOrcid] = useState('');
  
  const [isSaving, setIsSaving] = useState(false);
  const [showToast, setShowToast] = useState('');
  const [processingId, setProcessingId] = useState<string | null>(null);

  const [services, setServices] = useState([
    { id: 'zotero', status: 'connected', account: 'nguyenvana_academic', lastSync: 'Auto sync' },
    { id: 'mendeley', status: 'connected', account: 'a.nguyen@mendeley.org', lastSync: '1 hour ago' },
    { id: 'scholar', status: 'disconnected', account: '', lastSync: '' }
  ]);

  const showNotification = (msg: string) => {
    setShowToast(msg);
    setTimeout(() => setShowToast(''), 3000);
  };

  const handleServiceAction = (id: string, action: 'sync' | 'connect' | 'disconnect') => {
    setProcessingId(id);
    setTimeout(() => {
      if (action === 'disconnect') {
        setServices(services.map(s => s.id === id ? { ...s, status: 'disconnected', account: '', lastSync: '' } : s));
        showNotification(`Disconnected ${id}`);
      } else if (action === 'connect') {
        setServices(services.map(s => s.id === id ? { ...s, status: 'connected', account: `user_${id}@example.com`, lastSync: 'Just now' } : s));
        showNotification(`Successfully connected to ${id}`);
      } else {
        setServices(services.map(s => s.id === id ? { ...s, lastSync: 'Just now' } : s));
        showNotification(`Synced data from ${id}`);
      }
      setProcessingId(null);
    }, 1000);
  };

  const handleSave = () => {
    setIsSaving(true);
    setTimeout(() => {
      setIsSaving(false);
      showNotification('Settings saved successfully!');
    }, 800);
  };

  const handleCancel = () => {
    router.push('/settings');
  };

  return (
    <div style={{
      maxWidth: '880px',
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
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 700, color: 'var(--on-surface)' }}>
          Academic Integration
        </h1>
        <p style={{ color: 'var(--on-surface-variant)', fontSize: '14px', marginTop: '4px', maxWidth: '560px' }}>
          Manage and synchronize your research accounts. Connect with digital libraries and academic databases to automate the document collection process.
        </p>
      </div>

      {/* 2x2 service grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
        <ServiceCard
          id="zotero"
          logo="Z"
          name="Zotero"
          status={services.find(s => s.id === 'zotero')?.status as any}
          account={services.find(s => s.id === 'zotero')?.account}
          lastSync={services.find(s => s.id === 'zotero')?.lastSync}
          isProcessing={processingId === 'zotero'}
          onSync={() => handleServiceAction('zotero', 'sync')} 
          onDisconnect={() => handleServiceAction('zotero', 'disconnect')} 
          onConnect={() => handleServiceAction('zotero', 'connect')}
        />
        <ServiceCard
          id="mendeley"
          logo="M"
          name="Mendeley"
          status={services.find(s => s.id === 'mendeley')?.status as any}
          account={services.find(s => s.id === 'mendeley')?.account}
          lastSync={services.find(s => s.id === 'mendeley')?.lastSync}
          isProcessing={processingId === 'mendeley'}
          onSync={() => handleServiceAction('mendeley', 'sync')} 
          onDisconnect={() => handleServiceAction('mendeley', 'disconnect')} 
          onConnect={() => handleServiceAction('mendeley', 'connect')}
        />
        <ServiceCard
          id="scholar"
          logo="G"
          name="Google Scholar"
          status={services.find(s => s.id === 'scholar')?.status as any}
          account={services.find(s => s.id === 'scholar')?.account}
          lastSync={services.find(s => s.id === 'scholar')?.lastSync}
          description="Connect to automatically update citation lists and articles from Google Scholar into the system."
          isProcessing={processingId === 'scholar'}
          onSync={() => handleServiceAction('scholar', 'sync')} 
          onDisconnect={() => handleServiceAction('scholar', 'disconnect')} 
          onConnect={() => handleServiceAction('scholar', 'connect')}
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
                Verify academic researcher identity
              </div>
            </div>
          </div>
          <label style={{ fontSize: '12px', color: 'var(--on-surface-variant)', display: 'block', marginBottom: '6px' }}>
            ORCID Number
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
            style={{ width: '100%', justifyContent: 'center', fontSize: '13px', opacity: processingId === 'orcid' ? 0.7 : 1 }}
            id="orcid-verify-btn"
            disabled={processingId === 'orcid' || !orcid}
            onClick={() => {
              setProcessingId('orcid');
              setTimeout(() => {
                showNotification(`Verified ORCID: ${orcid}`);
                setProcessingId(null);
              }, 1200);
            }}
          >
            {processingId === 'orcid' ? 'Verifying...' : 'Verify & Connect'}
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
          Upgrade Premium
        </button>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn btn-secondary" id="academic-back-btn" onClick={handleCancel}>← Back</button>
          <button 
            className="btn btn-primary" 
            id="academic-save-btn" 
            onClick={handleSave}
            disabled={isSaving}
            style={{ opacity: isSaving ? 0.7 : 1, minWidth: '160px' }}
          >
            {isSaving ? 'Saving...' : 'Save Connection Settings'}
          </button>
        </div>
      </div>
    </div>
  );
}
