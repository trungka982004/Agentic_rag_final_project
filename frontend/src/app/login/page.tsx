'use client';

import { FormEvent, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { apiLogin } from '@/services/api';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const tokens = await apiLogin(email, password);
      localStorage.setItem('access_token', tokens.access_token);
      router.push('/chat');
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Email hoặc mật khẩu không đúng.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--surface-container-low)',
    }}>
      {/* Card */}
      <div style={{
        width: '100%',
        maxWidth: '420px',
        background: 'var(--surface-container-lowest)',
        border: '1px solid var(--outline-variant)',
        borderRadius: 'var(--radius-lg)',
        padding: '40px 36px',
        boxShadow: 'var(--shadow-2)',
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          {/* Logo box */}
          <div style={{
            width: '44px', height: '44px',
            background: 'var(--primary-container)',
            borderRadius: 'var(--radius-md)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 16px',
          }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
              stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9.5 2a6 6 0 0 1 5.5 8.5M9.5 2A6 6 0 0 0 4 8.5c0 3.1 2 5.7 4.8 6.5M9.5 2v3M15 10.5A6 6 0 0 1 9.5 17M15 10.5A6 6 0 0 0 21 8.5c0-3.3-2.7-6-6-6M15 10.5v3M9.5 17v5M9.5 17H5m4.5 5H5m9.5-7v5m0-5h4m-4 5h4" />
            </svg>
          </div>
          <div style={{
            fontFamily: 'var(--font-display)',
            fontSize: '11px',
            fontWeight: 600,
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
            color: 'var(--on-surface-variant)',
            marginBottom: '4px',
          }}>
            Intelligent Research Agent
          </div>
          <h1 style={{
            fontFamily: 'var(--font-display)',
            fontSize: '22px',
            fontWeight: 700,
            color: 'var(--on-surface)',
            margin: 0,
          }}>
            Đăng nhập
          </h1>
          <p style={{ fontSize: '13.5px', color: 'var(--on-surface-variant)', marginTop: '6px' }}>
            Đăng nhập để tiếp tục nghiên cứu
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <label htmlFor="email" style={{
              display: 'block',
              fontSize: '13px',
              fontWeight: 500,
              color: 'var(--on-surface)',
              marginBottom: '6px',
            }}>Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              className="input"
            />
          </div>

          <div>
            <label htmlFor="password" style={{
              display: 'block',
              fontSize: '13px',
              fontWeight: 500,
              color: 'var(--on-surface)',
              marginBottom: '6px',
            }}>Mật khẩu</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              className="input"
            />
          </div>

          {error && (
            <div style={{
              padding: '10px 14px',
              background: 'var(--error-container)',
              border: '1px solid rgba(186,26,26,0.2)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--error)',
              fontSize: '13px',
            }}>
              {error}
            </div>
          )}

          <button
            id="login-submit-btn"
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{
              width: '100%',
              padding: '11px',
              marginTop: '4px',
              justifyContent: 'center',
            }}
          >
            {loading ? (
              <>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                  strokeWidth="2" style={{ animation: 'spin 1s linear infinite' }}>
                  <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                </svg>
                Đang đăng nhập...
              </>
            ) : 'Đăng nhập'}
          </button>
        </form>

        <p style={{
          textAlign: 'center',
          marginTop: '20px',
          fontSize: '13px',
          color: 'var(--on-surface-variant)',
        }}>
          Chưa có tài khoản?{' '}
          <Link href="/register" style={{
            color: 'var(--primary-container)',
            fontWeight: 600,
            textDecoration: 'none',
          }}>
            Đăng ký ngay
          </Link>
        </p>
      </div>
    </div>
  );
}
