'use client';

import { useState } from 'react';

// Stitch screen: "Cấu hình hệ thống"
// Sections: LLM Config (model dropdown + temperature slider + max tokens)
//           RAG Performance toggles
//           System Data Management (clear cache, backup, reset)
//           Agent tip card

const Toggle = ({ checked, onChange, id }: { checked: boolean; onChange: (v: boolean) => void; id?: string }) => (
  <label className="toggle" style={{ cursor: 'pointer' }} htmlFor={id}>
    <input id={id} type="checkbox" checked={checked} onChange={e => onChange(e.target.checked)} />
    <span className="toggle-slider" />
  </label>
);

const LLM_MODELS = [
  'Qwen 2.5 (Mặc định)',
  'Llama 3.1 70B',
  'Mistral 7B',
  'GPT-4o Mini',
  'Gemini 1.5 Flash',
];

export default function SystemConfigPage() {
  const [model, setModel] = useState(LLM_MODELS[0]);
  const [temperature, setTemperature] = useState(0.2);
  const [maxTokens, setMaxTokens] = useState(2048);
  const [gpuBoost, setGpuBoost] = useState(true);
  const [autoAnalyze, setAutoAnalyze] = useState(true);
  const [optimizeNetwork, setOptimizeNetwork] = useState(false);
  const [clearConfirm, setClearConfirm] = useState(false);

  return (
    <div style={{ maxWidth: '900px' }}>
      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 700, color: 'var(--on-surface)' }}>
          Cấu hình hệ thống
        </h1>
        <p style={{ color: 'var(--on-surface-variant)', fontSize: '14px', marginTop: '4px' }}>
          Điều chỉnh các tham số mô hình AI, hiệu suất RAG và quản lý dữ liệu nghiên cứu của hệ thống.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>

        {/* ── LEFT: LLM Config ── */}
        <div>
          <div className="card" style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '18px' }}>
              <div style={{
                width: '32px', height: '32px',
                background: 'var(--primary-fixed)',
                borderRadius: 'var(--radius-sm)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--primary-container)" strokeWidth="2">
                  <path d="M9.5 2A6 6 0 0 1 15 10.5M9.5 2A6 6 0 0 0 4 8.5c0 3.1 2 5.7 4.8 6.5M9.5 2v3M15 10.5A6 6 0 0 1 9.5 17M15 10.5A6 6 0 0 0 21 8.5c0-3.3-2.7-6-6-6M15 10.5v3M9.5 17v5M9.5 17H5m4.5 5H5m9.5-7v5m0-5h4m-4 5h4" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--on-surface)', fontFamily: 'var(--font-display)' }}>
                Cấu hình mô hình ngôn ngữ (LLM)
              </div>
            </div>

            {/* Model selector */}
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '12.5px', color: 'var(--on-surface-variant)', marginBottom: '5px', fontWeight: 500 }}>
                Bộ não phân tích (Mô hình LLM)
              </label>
              <select
                id="llm-model-select"
                value={model}
                onChange={e => setModel(e.target.value)}
                style={{
                  width: '100%', padding: '9px 12px',
                  border: '1px solid var(--outline-variant)',
                  borderRadius: 'var(--radius-sm)',
                  background: 'var(--surface-container-lowest)',
                  color: 'var(--on-surface)', fontSize: '13.5px',
                  fontFamily: 'var(--font-body)', outline: 'none', cursor: 'pointer',
                }}
              >
                {LLM_MODELS.map(m => <option key={m}>{m}</option>)}
              </select>
            </div>

            {/* Temperature slider */}
            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <label style={{ fontSize: '12.5px', color: 'var(--on-surface-variant)', fontWeight: 500 }}>
                  Độ sáng tạo (Temperature)
                </label>
                <span style={{
                  fontSize: '12px', fontFamily: 'monospace',
                  background: 'var(--primary-fixed)',
                  color: 'var(--primary-container)',
                  padding: '2px 8px', borderRadius: '4px', fontWeight: 600,
                }}>
                  {temperature.toFixed(1)}
                </span>
              </div>
              <input
                id="llm-temperature"
                type="range"
                min="0" max="1" step="0.1"
                value={temperature}
                onChange={e => setTemperature(parseFloat(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--primary-container)' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--on-surface-variant)', marginTop: '3px' }}>
                <span>Chính xác (0.0)</span>
                <span>Sáng tạo (1.0)</span>
              </div>
            </div>

            {/* Max tokens */}
            <div>
              <label style={{ display: 'block', fontSize: '12.5px', color: 'var(--on-surface-variant)', marginBottom: '5px', fontWeight: 500 }}>
                Độ dài câu trả lời tối đa (Tokens)
              </label>
              <input
                id="llm-max-tokens"
                type="number"
                className="input"
                value={maxTokens}
                onChange={e => setMaxTokens(parseInt(e.target.value) || 2048)}
                min={256} max={8192} step={256}
                style={{ fontSize: '13.5px', fontFamily: 'monospace' }}
              />
              <div style={{ fontSize: '11.5px', color: 'var(--on-surface-variant)', marginTop: '4px' }}>
                Đề xuất: 2048 cho phân tích học thuật, 4096 cho báo cáo dài.
              </div>
            </div>
          </div>

          {/* Agent Tip Card */}
          <div style={{
            background: 'var(--primary-fixed)',
            border: '1px solid var(--primary-fixed-dim)',
            borderRadius: 'var(--radius-md)',
            padding: '14px 16px',
            display: 'flex', gap: '10px', alignItems: 'flex-start',
          }}>
            <div style={{
              width: '28px', height: '28px', flexShrink: 0,
              background: 'var(--primary-container)',
              borderRadius: '50%',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="white" stroke="none">
                <path d="M12 2a10 10 0 1 0 0 20A10 10 0 0 0 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
              </svg>
            </div>
            <div>
              <div style={{ fontSize: '12.5px', fontWeight: 600, color: 'var(--primary-container)', marginBottom: '4px', fontFamily: 'var(--font-display)' }}>
                Mẹo từ Agent
              </div>
              <div style={{ fontSize: '12.5px', color: 'var(--on-primary-fixed)', lineHeight: '1.6' }}>
                Sử dụng Temperature <strong>0.2</strong> giúp cải thiện độ chính xác khi trích dẫn học thuật.
                Tăng lên <strong>0.7–0.9</strong> khi cần tổng hợp sáng tạo hoặc brainstorming ý tưởng nghiên cứu.
              </div>
            </div>
          </div>
        </div>

        {/* ── RIGHT: Performance + Data Management ── */}
        <div>
          {/* RAG Performance Toggles */}
          <div className="card" style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <div style={{
                width: '32px', height: '32px',
                background: 'var(--success-container)',
                borderRadius: 'var(--radius-sm)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--success)" strokeWidth="2">
                  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--on-surface)', fontFamily: 'var(--font-display)' }}>
                Tối ưu hóa &amp; Hiệu năng RAG
              </div>
            </div>

            {[
              {
                id: 'toggle-gpu',
                label: 'Tăng tốc độ phản hồi',
                desc: 'Sử dụng tài nguyên GPU để xử lý mô hình AI nhanh hơn',
                val: gpuBoost, set: setGpuBoost,
              },
              {
                id: 'toggle-auto',
                label: 'Tự động phân tích tài liệu',
                desc: 'Phân tích tài liệu mới ngay khi tải lên thay vì theo lịch',
                val: autoAnalyze, set: setAutoAnalyze,
              },
              {
                id: 'toggle-network',
                label: 'Tối ưu dung lượng mạng',
                desc: 'Nén dữ liệu truyền tải khi kết nối băng thông thấp',
                val: optimizeNetwork, set: setOptimizeNetwork,
              },
            ].map((t, i, arr) => (
              <div key={t.id} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '12px 0',
                borderBottom: i < arr.length - 1 ? '1px solid var(--surface-container-high)' : 'none',
              }}>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--on-surface)' }}>{t.label}</div>
                  <div style={{ fontSize: '11.5px', color: 'var(--on-surface-variant)', marginTop: '2px' }}>{t.desc}</div>
                </div>
                <Toggle id={t.id} checked={t.val} onChange={t.set} />
              </div>
            ))}
          </div>

          {/* System Data Management */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <div style={{
                width: '32px', height: '32px',
                background: 'var(--surface-container)',
                borderRadius: 'var(--radius-sm)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--on-surface-variant)" strokeWidth="2">
                  <ellipse cx="12" cy="5" rx="9" ry="3" strokeLinecap="round" />
                  <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" strokeLinecap="round" />
                  <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" strokeLinecap="round" />
                </svg>
              </div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--on-surface)', fontFamily: 'var(--font-display)' }}>
                Quản lý dữ liệu hệ thống
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {/* Clear cache */}
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '11px 14px',
                border: '1px solid var(--outline-variant)',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--surface-container-lowest)',
              }}>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--on-surface)' }}>Xóa bộ nhớ đệm cục bộ</div>
                  <div style={{ fontSize: '11.5px', color: 'var(--on-surface-variant)', marginTop: '2px' }}>Giải phóng không gian lưu trữ tạm thời</div>
                </div>
                <button
                  className="btn btn-secondary"
                  id="clear-cache-btn"
                  onClick={() => { setClearConfirm(true); setTimeout(() => setClearConfirm(false), 2000); }}
                  style={{ fontSize: '12px', padding: '5px 12px', gap: '5px' }}
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="3 6 5 6 21 6" strokeLinecap="round" />
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" strokeLinecap="round" />
                  </svg>
                  {clearConfirm ? '✓ Đã xóa' : 'Xóa ngay'}
                </button>
              </div>

              {/* Backup */}
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '11px 14px',
                border: '1px solid var(--outline-variant)',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--surface-container-lowest)',
              }}>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--on-surface)' }}>Sao lưu cấu hình dự án</div>
                  <div style={{ fontSize: '11.5px', color: 'var(--on-surface-variant)', marginTop: '2px' }}>Xuất toàn bộ cấu hình hệ thống về máy</div>
                </div>
                <button
                  className="btn btn-secondary"
                  id="backup-config-btn"
                  style={{ fontSize: '12px', padding: '5px 12px', gap: '5px' }}
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="16 16 12 12 8 16" strokeLinecap="round" strokeLinejoin="round" />
                    <line x1="12" y1="12" x2="12" y2="21" strokeLinecap="round" />
                    <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  Sao lưu
                </button>
              </div>

              {/* Reset */}
              <div style={{ paddingTop: '4px', textAlign: 'center' }}>
                <button
                  id="reset-config-btn"
                  style={{
                    background: 'none', border: 'none', cursor: 'pointer',
                    color: 'var(--error)', fontSize: '12.5px',
                    textDecoration: 'underline', textUnderlineOffset: '2px',
                    fontFamily: 'var(--font-body)',
                  }}
                >
                  Khôi phục cài đặt gốc của hệ thống
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Action buttons */}
      <div style={{
        display: 'flex', justifyContent: 'flex-end', gap: '10px',
        marginTop: '24px', paddingTop: '20px',
        borderTop: '1px solid var(--outline-variant)',
      }}>
        <button className="btn btn-secondary" id="config-cancel-btn">Huỷ thay đổi</button>
        <button className="btn btn-primary" id="config-save-btn">Lưu cấu hình</button>
      </div>
    </div>
  );
}
