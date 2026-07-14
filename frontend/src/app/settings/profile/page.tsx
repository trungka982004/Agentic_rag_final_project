'use client';

import { useState } from 'react';

// Stitch screen: "Thông tin cá nhân — Personal Information"
// Sections: Profile card + form fields, Security (password + 2FA toggle)

import { useRouter } from 'next/navigation';

const Toggle = ({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) => (
  <label className="toggle" style={{ cursor: 'pointer' }}>
    <input type="checkbox" checked={checked} onChange={e => onChange(e.target.checked)} />
    <span className="toggle-slider" />
  </label>
);

export default function ProfilePage() {
  const router = useRouter();
  const [twoFA, setTwoFA] = useState(true);
  const [tags, setTags] = useState(['Trí tuệ nhân tạo', 'Xử lý ngôn ngữ tự nhiên', 'Học sâu']);
  const [isSaving, setIsSaving] = useState(false);
  const [showToast, setShowToast] = useState(false);

  const [formData, setFormData] = useState({
    name: 'Nguyễn Văn A',
    title: 'Tiến sĩ / Phó Giáo sư',
    email: 'a.nguyen@academic.edu.vn',
    org: 'Viện Công nghệ Thông tin – Viện Hàn lâm KH&CN VN',
    pwCurrent: '',
    pwNew: '',
    pwConfirm: '',
  });

  const handleSave = () => {
    setIsSaving(true);
    // Simulate API call
    setTimeout(() => {
      setIsSaving(false);
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
    }, 800);
  };

  const handleCancel = () => {
    router.push('/settings');
  };

  return (
    <div style={{
      maxWidth: '780px',
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
          Lưu thông tin cá nhân thành công!
        </div>
      )}

      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 700, color: 'var(--on-surface)' }}>
          Thông tin cá nhân
        </h1>
        <p style={{ color: 'var(--on-surface-variant)', fontSize: '14px', marginTop: '4px' }}>
          Cập nhật thông tin học thuật và thiết lập bảo mật mới cho tài khoản của bạn.
        </p>
      </div>

      {/* Profile identity card */}
      <div className="card" style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '20px' }}>
          {/* Avatar */}
          <div style={{
            width: '56px', height: '56px', borderRadius: '50%',
            background: 'var(--primary-container)',
            color: 'var(--on-primary)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '22px', fontWeight: 700, fontFamily: 'var(--font-display)',
            flexShrink: 0, position: 'relative',
          }}>
            {formData.name.charAt(0).toUpperCase()}
            {/* Active badge */}
            <span style={{
              position: 'absolute', bottom: 0, right: 0,
              width: '14px', height: '14px', borderRadius: '50%',
              background: 'var(--success)',
              border: '2px solid var(--surface-container-lowest)',
            }} />
          </div>
          <div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '17px', fontWeight: 700, color: 'var(--on-surface)' }}>
              TS. {formData.name}
            </div>
            <span style={{
              fontSize: '10.5px', fontFamily: 'var(--font-label)', fontWeight: 700,
              background: 'var(--success-container)', color: 'var(--success)',
              padding: '2px 8px', borderRadius: '99px',
            }}>
              ● ĐANG HOẠT ĐỘNG
            </span>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
          {[
            { id: 'name',  label: 'Họ và tên',           value: formData.name, span: 1 },
            { id: 'title', label: 'Chức danh / Học vị',  value: formData.title, span: 1 },
            { id: 'email', label: 'Email học thuật',     value: formData.email, span: 1 },
            { id: 'org',   label: 'Cơ quan / Tổ chức',   value: formData.org,   span: 1 },
          ].map(f => (
            <div key={f.id} style={{ gridColumn: `span ${f.span}` }}>
              <label htmlFor={f.id} style={{
                display: 'block', fontSize: '12.5px',
                color: 'var(--on-surface-variant)', marginBottom: '5px',
              }}>
                {f.label}
              </label>
              <input 
                id={f.id} 
                className="input" 
                value={f.value} 
                onChange={(e) => setFormData({...formData, [f.id]: e.target.value})}
                style={{ fontSize: '13.5px' }} 
              />
            </div>
          ))}

          {/* Research interest tags */}
          <div style={{ gridColumn: 'span 2' }}>
            <label style={{ display: 'block', fontSize: '12.5px', color: 'var(--on-surface-variant)', marginBottom: '5px' }}>
              Lĩnh vực nghiên cứu quan tâm
            </label>
            <div style={{
              display: 'flex', flexWrap: 'wrap', gap: '6px',
              padding: '8px 10px',
              border: '1px solid var(--outline-variant)',
              borderRadius: 'var(--radius-sm)',
              background: 'var(--surface-container-lowest)',
              minHeight: '40px',
            }}>
              {tags.map(tag => (
                <span key={tag} style={{
                  display: 'inline-flex', alignItems: 'center', gap: '5px',
                  background: 'var(--primary-fixed)',
                  border: '1px solid var(--primary-fixed-dim)',
                  color: 'var(--primary-container)',
                  borderRadius: '4px',
                  padding: '3px 10px',
                  fontSize: '12.5px',
                  fontFamily: 'var(--font-label)', fontWeight: 500,
                }}>
                  {tag}
                  <button
                    onClick={() => setTags(t => t.filter(x => x !== tag))}
                    style={{
                      background: 'none', border: 'none', cursor: 'pointer',
                      color: 'var(--primary-container)', fontSize: '14px', lineHeight: 1,
                      padding: '0 1px',
                    }}
                  >×</button>
                </span>
              ))}
              <button
                style={{
                  display: 'inline-flex', alignItems: 'center', gap: '4px',
                  background: 'transparent',
                  border: '1px dashed var(--outline-variant)',
                  color: 'var(--primary-container)',
                  borderRadius: '4px', padding: '3px 10px',
                  fontSize: '12.5px', cursor: 'pointer',
                  fontFamily: 'var(--font-label)',
                }}
                id="add-tag-btn"
                onClick={() => {
                  const newTag = prompt('Nhập lĩnh vực nghiên cứu mới:');
                  if (newTag && newTag.trim() && !tags.includes(newTag.trim())) {
                    setTags([...tags, newTag.trim()]);
                  }
                }}
              >
                + Thêm lĩnh vực
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Security section */}
      <div className="card" style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--on-surface-variant)"
            strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" strokeLinecap="round" strokeLinejoin="round" /></svg>
          <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--on-surface)' }}>Thiết lập bảo mật</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginBottom: '16px' }}>
          {[
            { id: 'pwCurrent', label: 'Mật khẩu hiện tại', type: 'password', value: formData.pwCurrent, placeholder: '••••••••••••' },
            { id: 'pwNew',     label: 'Mật khẩu mới',       type: 'password', value: formData.pwNew, placeholder: 'Nhập mật khẩu mới' },
            { id: 'pwConfirm', label: 'Xác nhận mật khẩu mới', type: 'password', value: formData.pwConfirm, placeholder: 'Xác nhận lại' },
          ].map(f => (
            <div key={f.id}>
              <label htmlFor={f.id} style={{ display: 'block', fontSize: '12.5px', color: 'var(--on-surface-variant)', marginBottom: '5px' }}>
                {f.label}
              </label>
              <input 
                id={f.id} 
                type={f.type} 
                className="input" 
                value={f.value}
                onChange={(e) => setFormData({...formData, [f.id]: e.target.value})}
                placeholder={f.placeholder} 
              />
            </div>
          ))}
        </div>

        {/* 2FA toggle — Stitch style */}
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          background: 'var(--surface-container-low)',
          border: '1px solid var(--outline-variant)',
          borderRadius: 'var(--radius-sm)',
          padding: '12px 14px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '28px', height: '28px',
              background: twoFA ? 'var(--primary-fixed)' : 'var(--surface-container)',
              borderRadius: 'var(--radius-sm)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: twoFA ? 'var(--primary-container)' : 'var(--on-surface-variant)',
            }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--on-surface)' }}>
                Xác thực 2 yếu tố (2FA)
              </div>
              <div style={{ fontSize: '12px', color: 'var(--on-surface-variant)' }}>
                Bảo vệ tài khoản bằng mã bảo mật điện thoại
              </div>
            </div>
          </div>
          <Toggle checked={twoFA} onChange={setTwoFA} />
        </div>
      </div>

      {/* Action buttons */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', paddingTop: '8px' }}>
        <button className="btn btn-secondary" id="profile-cancel-btn" onClick={handleCancel}>Huỷ bỏ</button>
        <button 
          className="btn btn-primary" 
          id="profile-save-btn" 
          onClick={handleSave}
          disabled={isSaving}
          style={{ opacity: isSaving ? 0.7 : 1, minWidth: '120px' }}
        >
          {isSaving ? 'Đang lưu...' : 'Lưu thông tin'}
        </button>
      </div>
    </div>
  );
}
