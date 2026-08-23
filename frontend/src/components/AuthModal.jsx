import React, { useState } from 'react';
import { 
  X, 
  Lock, 
  User, 
  Briefcase, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  GraduationCap, 
  ArrowRight,
  ShieldCheck,
  FlaskConical,
  Eye,
  EyeOff
} from 'lucide-react';

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [authTab, setAuthTab] = useState('login'); // 'login' | 'register'
  const [username, setUsername] = useState('akmal');
  const [password, setPassword] = useState('123');
  const [showPassword, setShowPassword] = useState(false);
  
  // Register fields
  const [regName, setRegName] = useState('');
  const [regUsername, setRegUsername] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regTrack, setRegTrack] = useState('Machine Learning & AI');

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  if (!isOpen) return null;

  const handleLogin = async (e) => {
    if (e) e.preventDefault();
    setIsLoading(true);
    setErrorMessage('');

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const json = await res.json();
      if (json.status === 'success') {
        localStorage.setItem('talentxai_auth_user', JSON.stringify(json.data));
        onAuthSuccess(json.data);
        onClose();
      } else {
        setErrorMessage(json.detail || 'Username atau Password salah.');
      }
    } catch (err) {
      console.error(err);
      setErrorMessage('Gagal menghubungi backend auth: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e) => {
    if (e) e.preventDefault();
    if (!regName.trim() || !regUsername.trim() || !regPassword.trim()) {
      setErrorMessage('Mohon lengkapi seluruh field pendaftaran!');
      return;
    }

    setIsLoading(true);
    setErrorMessage('');

    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: regName,
          username: regUsername,
          password: regPassword,
          track: regTrack
        })
      });

      const json = await res.json();
      if (json.status === 'success') {
        localStorage.setItem('talentxai_auth_user', JSON.stringify(json.data));
        onAuthSuccess(json.data);
        onClose();
      } else {
        setErrorMessage(json.detail || 'Terjadi kesalahan saat registrasi.');
      }
    } catch (err) {
      console.error(err);
      setErrorMessage('Gagal menghubungi backend auth: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const quickFill = (u, p) => {
    setUsername(u);
    setPassword(p);
    setAuthTab('login');
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div 
        className="modal-content" 
        style={{ maxWidth: '480px', padding: '2rem' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 12px rgba(37,99,235,0.3)'
            }}>
              <Lock size={20} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#0F172A', lineHeight: 1.2 }}>
                {authTab === 'login' ? 'Masuk ke Akun Anda' : 'Buat Akun Mahasiswa'}
              </h2>
              <p style={{ fontSize: '0.82rem', color: '#64748B', marginTop: '0.15rem' }}>
                Platform Rekomendasi Karir AI & Portofolio BRIN
              </p>
            </div>
          </div>

          <button 
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: '#94A3B8', padding: '4px' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Tab Switcher (Login vs Register) */}
        <div style={{
          display: 'flex',
          background: '#F1F5F9',
          padding: '4px',
          borderRadius: '12px',
          marginBottom: '1.25rem',
          border: '1px solid #E2E8F0'
        }}>
          <button
            onClick={() => { setAuthTab('login'); setErrorMessage(''); }}
            style={{
              flex: 1,
              padding: '0.5rem',
              borderRadius: '9px',
              border: 'none',
              fontSize: '0.86rem',
              fontWeight: 700,
              cursor: 'pointer',
              background: authTab === 'login' ? '#FFFFFF' : 'transparent',
              color: authTab === 'login' ? '#1E293B' : '#64748B',
              boxShadow: authTab === 'login' ? '0 2px 6px rgba(0,0,0,0.06)' : 'none',
              transition: 'all 0.15s ease'
            }}
          >
            🔑 Masuk Akun
          </button>
          <button
            onClick={() => { setAuthTab('register'); setErrorMessage(''); }}
            style={{
              flex: 1,
              padding: '0.5rem',
              borderRadius: '9px',
              border: 'none',
              fontSize: '0.86rem',
              fontWeight: 700,
              cursor: 'pointer',
              background: authTab === 'register' ? '#FFFFFF' : 'transparent',
              color: authTab === 'register' ? '#1E293B' : '#64748B',
              boxShadow: authTab === 'register' ? '0 2px 6px rgba(0,0,0,0.06)' : 'none',
              transition: 'all 0.15s ease'
            }}
          >
            ✨ Daftar Baru
          </button>
        </div>

        {/* Error Alert */}
        {errorMessage && (
          <div style={{
            background: '#FEF2F2',
            border: '1px solid #FECACA',
            color: '#991B1B',
            padding: '0.65rem 0.85rem',
            borderRadius: '10px',
            fontSize: '0.82rem',
            marginBottom: '1rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <AlertCircle size={16} flexShrink={0} />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* TAB 1: LOGIN FORM */}
        {authTab === 'login' && (
          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.84rem', fontWeight: 700, color: '#334155', marginBottom: '0.35rem' }}>
                Username
              </label>
              <div style={{ position: 'relative' }}>
                <input 
                  type="text"
                  placeholder="Masukkan username (e.g. akmal / demo)"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  style={{
                    width: '100%',
                    padding: '0.65rem 0.85rem 0.65rem 2.4rem',
                    borderRadius: '10px',
                    border: '1px solid #CBD5E1',
                    fontSize: '0.9rem',
                    outline: 'none',
                    transition: 'border 0.2s'
                  }}
                />
                <User size={16} style={{ position: 'absolute', left: '0.8rem', top: '50%', transform: 'translateY(-50%)', color: '#94A3B8' }} />
              </div>
            </div>

            <div style={{ marginBottom: '1.25rem' }}>
              <label style={{ display: 'block', fontSize: '0.84rem', fontWeight: 700, color: '#334155', marginBottom: '0.35rem' }}>
                Password
              </label>
              <div style={{ position: 'relative' }}>
                <input 
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Masukkan password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  style={{
                    width: '100%',
                    padding: '0.65rem 2.4rem 0.65rem 2.4rem',
                    borderRadius: '10px',
                    border: '1px solid #CBD5E1',
                    fontSize: '0.9rem',
                    outline: 'none',
                    transition: 'border 0.2s'
                  }}
                />
                <Lock size={16} style={{ position: 'absolute', left: '0.8rem', top: '50%', transform: 'translateY(-50%)', color: '#94A3B8' }} />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{ position: 'absolute', right: '0.8rem', top: '50%', transform: 'translateY(-50%)', background: 'transparent', border: 'none', cursor: 'pointer', color: '#94A3B8' }}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary"
              style={{ width: '100%', justifyContent: 'center', padding: '0.75rem', fontSize: '0.95rem', borderRadius: '12px' }}
            >
              {isLoading ? 'Memverifikasi...' : '🚀 Masuk ke Akun'}
            </button>

            {/* Quick Demo Credentials */}
            <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #E2E8F0' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
                💡 Akun Cepat Siap Pakai:
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                <button
                  type="button"
                  onClick={() => quickFill('akmal', '123')}
                  style={{
                    padding: '0.45rem 0.6rem',
                    borderRadius: '8px',
                    border: '1px solid #A7F3D0',
                    background: '#ECFDF5',
                    color: '#065F46',
                    fontSize: '0.78rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.3rem'
                  }}
                >
                  <User size={13} />
                  Akun: <strong>akmal</strong> / 123
                </button>

                <button
                  type="button"
                  onClick={() => quickFill('demo', '123')}
                  style={{
                    padding: '0.45rem 0.6rem',
                    borderRadius: '8px',
                    border: '1px solid #BFDBFE',
                    background: '#EFF6FF',
                    color: '#1E40AF',
                    fontSize: '0.78rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.3rem'
                  }}
                >
                  <FlaskConical size={13} />
                  Demo: <strong>demo</strong> / 123
                </button>
              </div>
            </div>
          </form>
        )}

        {/* TAB 2: REGISTER FORM */}
        {authTab === 'register' && (
          <form onSubmit={handleRegister}>
            <div style={{ marginBottom: '0.85rem' }}>
              <label style={{ display: 'block', fontSize: '0.84rem', fontWeight: 700, color: '#334155', marginBottom: '0.35rem' }}>
                Nama Lengkap
              </label>
              <input 
                type="text"
                placeholder="Contoh: Akmal Yaasir Fauzaan"
                value={regName}
                onChange={(e) => setRegName(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '0.65rem 0.85rem',
                  borderRadius: '10px',
                  border: '1px solid #CBD5E1',
                  fontSize: '0.9rem',
                  outline: 'none'
                }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '0.85rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.84rem', fontWeight: 700, color: '#334155', marginBottom: '0.35rem' }}>
                  Username
                </label>
                <input 
                  type="text"
                  placeholder="e.g. akmal2026"
                  value={regUsername}
                  onChange={(e) => setRegUsername(e.target.value)}
                  required
                  style={{
                    width: '100%',
                    padding: '0.65rem 0.85rem',
                    borderRadius: '10px',
                    border: '1px solid #CBD5E1',
                    fontSize: '0.9rem',
                    outline: 'none'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.84rem', fontWeight: 700, color: '#334155', marginBottom: '0.35rem' }}>
                  Password
                </label>
                <input 
                  type="password"
                  placeholder="Buat password"
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  required
                  style={{
                    width: '100%',
                    padding: '0.65rem 0.85rem',
                    borderRadius: '10px',
                    border: '1px solid #CBD5E1',
                    fontSize: '0.9rem',
                    outline: 'none'
                  }}
                />
              </div>
            </div>

            <div style={{ marginBottom: '1.25rem' }}>
              <label style={{ display: 'block', fontSize: '0.84rem', fontWeight: 700, color: '#334155', marginBottom: '0.35rem' }}>
                Peminatan Karir / Minat Bidang
              </label>
              <select
                value={regTrack}
                onChange={(e) => setRegTrack(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.65rem 0.85rem',
                  borderRadius: '10px',
                  border: '1px solid #CBD5E1',
                  fontSize: '0.9rem',
                  outline: 'none',
                  background: 'white'
                }}
              >
                <option value="Machine Learning & AI">🤖 Machine Learning & AI</option>
                <option value="Web & Full-Stack">💻 Web & Full-Stack Development</option>
                <option value="Networking & Cloud">☁️ Networking & Cloud Infrastructure</option>
                <option value="Sistem Informasi & Bisnis">📊 Sistem Informasi & Business Analyst</option>
                <option value="SAP & Enterprise Systems">🏢 SAP & Enterprise Architecture</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary"
              style={{
                width: '100%',
                justifyContent: 'center',
                padding: '0.75rem',
                fontSize: '0.95rem',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #10B981, #059669)'
              }}
            >
              {isLoading ? 'Mendaftarkan...' : '✨ Daftarkan Akun & Mulai'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
