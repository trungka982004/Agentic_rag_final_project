'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import type { User } from '@/types';

interface Props {
  user: User | null;
  title?: string;
  isConnected?: boolean;
  sessionId?: string;
}

const Icon = ({ path, size = 16 }: { path: string; size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d={path} />
  </svg>
);

const ICONS = {
  bell: 'M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 0 1-3.46 0',
  help: 'M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3M12 17h.01',
  settings: 'M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2zM12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
  edit: 'M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z',
};

export default function TopBar({ user, title, isConnected, sessionId }: Props) {
  const pathname = usePathname();
  const isChat = pathname.startsWith('/chat');
  const isSettings = pathname.startsWith('/settings');

  return (
    <header style={{
      height: 'var(--topbar-height)',
      background: 'var(--surface-container-lowest)',
      borderBottom: '1px solid var(--outline-variant)',
      display: 'flex',
      alignItems: 'center',
      paddingLeft: '20px',
      paddingRight: '16px',
      gap: '12px',
      flexShrink: 0,
    }}>
      {/* Left: title */}
      <div style={{ flex: 1, overflow: 'hidden' }}>
        {title && (
          <div style={{
            fontFamily: 'var(--font-display)',
            fontSize: '14px',
            fontWeight: 600,
            color: 'var(--on-surface)',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}>
            {title}
          </div>
        )}
        {isConnected !== undefined && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px', marginTop: '1px' }}>
            <span style={{
              width: '6px', height: '6px',
              borderRadius: '50%',
              background: isConnected ? 'var(--success)' : 'var(--on-surface-variant)',
              display: 'inline-block',
            }} />
            <span style={{ fontSize: '11.5px', color: 'var(--on-surface-variant)' }}>
              {isConnected ? 'Connected' : 'Reconnecting...'}
            </span>
          </div>
        )}
      </div>

      {/* Center: nav tabs — Library / Settings */}
      <nav className="nav-tabs" style={{ height: 'var(--topbar-height)' }}>
        <Link
          href="/chat"
          className={`nav-tab ${isChat ? 'nav-tab--active' : ''}`}
        >
          Library
        </Link>
        <Link
          href="/settings"
          className={`nav-tab ${isSettings ? 'nav-tab--active' : ''}`}
        >
          Settings
        </Link>
      </nav>

      {/* Right: status + action icons + avatar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
        {/* Status badge */}
        <span className={`status-badge ${isConnected !== false ? 'status-badge--active' : ''}`}
          style={{ marginRight: '8px', fontSize: '10.5px' }}>
          {isConnected !== false ? 'ACTIVE' : 'OFFLINE'}
        </span>

        <button className="btn-icon" title="Help" id="topbar-help-btn">
          <Icon path={ICONS.help} size={17} />
        </button>
        <button className="btn-icon" title="Edit" id="topbar-edit-btn">
          <Icon path={ICONS.edit} size={17} />
        </button>
        <Link href="/settings/profile">
          <div style={{
            width: '30px', height: '30px',
            borderRadius: '50%',
            background: 'var(--primary-container)',
            color: 'var(--on-primary)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '12px', fontWeight: 700,
            cursor: 'pointer',
            border: '2px solid var(--outline-variant)',
          }}>
            {user?.email?.[0]?.toUpperCase() ?? 'U'}
          </div>
        </Link>
      </div>
    </header>
  );
}
