'use client';

import { useState, FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { apiRegister, apiLogin } from '@/services/api';

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    if (password !== confirm) {
      setError('Mật khẩu xác nhận không khớp.');
      return;
    }
    if (password.length < 6) {
      setError('Mật khẩu phải có ít nhất 6 ký tự.');
      return;
    }
    setLoading(true);
    try {
      await apiRegister(email, password);
      const tokens = await apiLogin(email, password);
      localStorage.setItem('access_token', tokens.access_token);
      router.push('/chat');
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? 'Đăng ký thất bại. Email có thể đã được sử dụng.';
      setError(detail);
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
      background: 'var(--bg-base)',
      padding: '24px',
    }}>
      <div style={{
        position: 'fixed',
        inset: 0,
        background: 'radial-gradient(ellipse 80% 60% at 50% 0%, rgba(139,92,246,0.08) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />

      <div className="animate-fade-in" style={{ width: '100%', maxWidth: '400px', position: 'relative', zIndex: 1 }}>
        <div style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-xl)',
          padding: '40px 36px',
          boxShadow: 'var(--shadow-lg)',
        }}>
          <div style={{ textAlign: 'center', marginBottom: '32px' }}>
            <div style={{
              width: '52px',
              height: '52px',
              borderRadius: 'var(--radius-lg)',
              background: 'linear-gradient(135deg, #2d1b69 0%, #1e3a5f 100%)',
              border: '1px solid rgba(139,92,246,0.4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.6em',
              margin: '0 auto 16px',
              boxShadow: '0 0 20px rgba(139,92,246,0.25)',
            }}>
              ✨
            </div>
            <h1 style={{
              fontSize: '1.3em',
              fontWeight: 700,
              background: 'linear-gradient(135deg, #c4b5fd, #93c5fd)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              margin: '0 0 4px',
            }}>
              Tạo tài khoản
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.83em', margin: 0 }}>
              Bắt đầu hành trình nghiên cứu của bạn
            </p>
          </div>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {[
              { id: 'reg-email', label: 'Email', type: 'email', value: email, setter: setEmail, placeholder: 'you@example.com' },
              { id: 'reg-password', label: 'Mật khẩu', type: 'password', value: password, setter: setPassword, placeholder: '••••••••' },
              { id: 'reg-confirm', label: 'Xác nhận mật khẩu', type: 'password', value: confirm, setter: setConfirm, placeholder: '••••••••' },
            ].map(field => (
              <div key={field.id}>
                <label htmlFor={field.id} style={{
                  display: 'block', fontSize: '0.8em', color: 'var(--text-secondary)',
                  marginBottom: '6px', fontWeight: 500,
                }}>
                  {field.label}
                </label>
                <input
                  id={field.id}
                  type={field.type}
                  value={field.value}
                  onChange={e => field.setter(e.target.value)}
                  placeholder={field.placeholder}
                  required
                  style={{
                    width: '100%', padding: '10px 14px',
                    background: 'var(--bg-elevated)',
                    border: '1px solid var(--border-muted)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--text-primary)', fontSize: '0.9em',
                    outline: 'none', transition: 'border-color 0.2s',
                    boxSizing: 'border-box',
                  }}
                  onFocus={e => (e.target.style.borderColor = 'rgba(139,92,246,0.5)')}
                  onBlur={e => (e.target.style.borderColor = 'var(--border-muted)')}
                />
              </div>
            ))}

            {error && (
              <div style={{
                padding: '10px 14px',
                background: 'rgba(239,68,68,0.08)',
                border: '1px solid rgba(239,68,68,0.25)',
                borderRadius: 'var(--radius-md)',
                color: '#fca5a5', fontSize: '0.82em',
              }}>
                ⚠️ {error}
              </div>
            )}

            <button
              id="register-submit-btn"
              type="submit"
              disabled={loading}
              style={{
                padding: '12px',
                background: loading
                  ? 'var(--bg-overlay)'
                  : 'linear-gradient(135deg, var(--accent-secondary), var(--accent-primary))',
                border: 'none', borderRadius: 'var(--radius-md)',
                color: '#fff', fontSize: '0.9em', fontWeight: 600,
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                boxShadow: loading ? 'none' : '0 4px 14px rgba(139,92,246,0.4)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
              }}
            >
              {loading ? (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                    strokeWidth="2" style={{ animation: 'spin 1s linear infinite' }}>
                    <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                  </svg>
                  Đang đăng ký...
                </>
              ) : 'Tạo tài khoản'}
            </button>
          </form>

          <p style={{ textAlign: 'center', marginTop: '20px', fontSize: '0.82em', color: 'var(--text-muted)' }}>
            Đã có tài khoản?{' '}
            <Link href="/login" style={{ color: 'var(--text-accent)', textDecoration: 'none', fontWeight: 500 }}>
              Đăng nhập
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
