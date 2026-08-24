import React, { useState } from 'react';
import { 
  Briefcase, 
  Sparkles, 
  ShieldCheck, 
  TrendingUp, 
  GraduationCap, 
  Award, 
  BookOpen, 
  Lock, 
  User, 
  ArrowRight, 
  CheckCircle2, 
  Zap, 
  Database,
  Users,
  School,
  Cloud,
  Terminal,
  Cpu,
  Building,
  Eye, 
  EyeOff,
  AlertCircle
} from 'lucide-react';

export default function LandingPortal({ onLoginSuccess }) {
  const [authMode, setAuthMode] = useState('demo'); // 'demo' | 'login' | 'register'
  const [username, setUsername] = useState('demo');
  const [password, setPassword] = useState('123');
  const [showPassword, setShowPassword] = useState(false);

  // Register fields
  const [regName, setRegName] = useState('');
  const [regUsername, setRegUsername] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regTrack, setRegTrack] = useState('Machine Learning & AI');

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Handle Mode Switch
  const switchMode = (mode) => {
    setAuthMode(mode);
    setErrorMessage('');
    if (mode === 'demo') {
      setUsername('demo');
      setPassword('123');
    } else if (mode === 'login') {
      setUsername('akmal');
      setPassword('123');
    }
  };

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
        onLoginSuccess(json.data);
      } else {
        setErrorMessage(json.detail || 'Username atau Password salah.');
      }
    } catch (err) {
      console.error(err);
      setErrorMessage('Gagal terhubung ke server backend: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e) => {
    if (e) e.preventDefault();
    if (!regName.trim() || !regUsername.trim() || !regPassword.trim()) {
      setErrorMessage('Mohon lengkapi semua field registrasi!');
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
        onLoginSuccess(json.data);
      } else {
        setErrorMessage(json.detail || 'Terjadi kesalahan saat pendaftaran.');
      }
    } catch (err) {
      console.error(err);
      setErrorMessage('Gagal terhubung ke backend: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: '#F7F9FB',
      color: '#191C1E',
      fontFamily: 'var(--font-main)',
      display: 'flex',
      flexDirection: 'column',
      position: 'relative',
      overflowX: 'hidden'
    }}>
      {/* Top Header matching Google Stitch Screen 3 */}
      <header style={{
        width: '100%',
        padding: '1.25rem 2.5rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        maxWidth: '1280px',
        margin: '0 auto',
        position: 'relative',
        zIndex: 10
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #004AC6 0%, #003EA8 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 900,
            fontSize: '1.2rem',
            boxShadow: '0 4px 14px rgba(0, 74, 198, 0.3)'
          }}>
            <Briefcase size={20} />
          </div>
          <div>
            <div style={{ fontSize: '1.2rem', fontWeight: 900, color: '#004AC6', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
              TalentXAI PRO
            </div>
            <div style={{ fontSize: '0.68rem', color: '#006C49', fontWeight: 800, letterSpacing: '0.08em', textTransform: 'uppercase', marginTop: '2px' }}>
              Career Intelligence Platform
            </div>
          </div>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          background: '#ECEEF0',
          padding: '0.4rem 0.9rem',
          borderRadius: '9999px',
          border: '1px solid rgba(195, 198, 215, 0.4)'
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: '#006C49',
            boxShadow: '0 0 8px rgba(0, 108, 73, 0.6)'
          }}></span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', fontWeight: 600, color: '#434655' }}>
            Neural Cross-Encoder & XAI Engine Online
          </span>
        </div>
      </header>

      {/* Main Hero & Auth Section */}
      <main style={{
        flexGrow: 1,
        maxWidth: '1280px',
        margin: '0 auto',
        width: '100%',
        padding: '2.5rem 2.5rem 3rem 2.5rem',
        display: 'grid',
        gridTemplateColumns: '1.15fr 0.85fr',
        gap: '3rem',
        alignItems: 'center',
        zIndex: 10
      }}>
        {/* Left Column: Hero Content & Bento Stat Cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <h1 style={{
            fontSize: '3.2rem',
            fontFamily: 'var(--font-heading)',
            fontWeight: 800,
            color: '#191C1E',
            lineHeight: 1.15,
            letterSpacing: '-0.035em'
          }}>
            Temukan Karir Ideal Berbasis <span className="gradient-text">Capaian Kurikulum</span> Akademik
          </h1>

          <p style={{
            fontSize: '1.05rem',
            color: '#434655',
            lineHeight: 1.65,
            maxWidth: '580px'
          }}>
            Platform intelijen presisi yang mengintegrasikan transkrip <strong>KHS multi-semester</strong> dan portofolio <strong>sertifikasi industri</strong>, didukung penjelasan transparan via <strong>Cross-Encoder, SHAP Feature Attribution</strong>, dan bimbingan <strong>DiCE Roadmap</strong>.
          </p>

          {/* 3 Bento Live Stat Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginTop: '0.5rem' }}>
            <div className="glass-panel glow-hover" style={{ padding: '1.25rem', borderRadius: '1rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              <Database size={22} color="#004AC6" style={{ marginBottom: '0.25rem' }} />
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.65rem', fontWeight: 800, color: '#191C1E', lineHeight: 1 }}>
                4.570+
              </div>
              <div style={{ fontSize: '0.8rem', color: '#737686', fontWeight: 600 }}>
                Lowongan Aktif
              </div>
            </div>

            <div className="glass-panel glow-hover" style={{ padding: '1.25rem', borderRadius: '1rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              <Users size={22} color="#006C49" style={{ marginBottom: '0.25rem' }} />
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.65rem', fontWeight: 800, color: '#191C1E', lineHeight: 1 }}>
                8
              </div>
              <div style={{ fontSize: '0.8rem', color: '#737686', fontWeight: 600 }}>
                Mahasiswa Benchmark
              </div>
            </div>

            <div className="glass-panel glow-hover" style={{ padding: '1.25rem', borderRadius: '1rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              <School size={22} color="#996100" style={{ marginBottom: '0.25rem' }} />
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.65rem', fontWeight: 800, color: '#191C1E', lineHeight: 1 }}>
                1.139
              </div>
              <div style={{ fontSize: '0.8rem', color: '#737686', fontWeight: 600 }}>
                Rekomendasi Kursus
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Google Stitch Auth Gateway Card */}
        <div style={{ width: '100%', maxWidth: '460px', margin: '0 auto' }}>
          <div className="glass-panel" style={{
            borderRadius: '1.25rem',
            overflow: 'hidden',
            boxShadow: '0 12px 36px -6px rgba(0, 74, 198, 0.12)',
            border: '1px solid rgba(195, 198, 215, 0.5)'
          }}>
            {/* Tab Navigation */}
            <div style={{
              display: 'flex',
              borderBottom: '1px solid #E0E3E5',
              background: '#F2F4F6'
            }}>
              <button
                onClick={() => switchMode('demo')}
                style={{
                  flex: 1,
                  padding: '0.9rem 0.5rem',
                  border: 'none',
                  borderBottom: authMode === 'demo' ? '2.5px solid #004AC6' : '2.5px solid transparent',
                  background: authMode === 'demo' ? '#FFFFFF' : 'transparent',
                  color: authMode === 'demo' ? '#004AC6' : '#737686',
                  fontWeight: 700,
                  fontSize: '0.86rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                🧪 Akun Demo Eksperimen
              </button>

              <button
                onClick={() => switchMode('login')}
                style={{
                  flex: 1,
                  padding: '0.9rem 0.5rem',
                  border: 'none',
                  borderBottom: authMode === 'login' ? '2.5px solid #004AC6' : '2.5px solid transparent',
                  background: authMode === 'login' ? '#FFFFFF' : 'transparent',
                  color: authMode === 'login' ? '#004AC6' : '#737686',
                  fontWeight: 700,
                  fontSize: '0.86rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                👤 Login Mahasiswa
              </button>
            </div>

            {/* Error Message Alert */}
            {errorMessage && (
              <div style={{
                margin: '1rem 1.5rem 0 1.5rem',
                background: '#FFDAD6',
                color: '#BA1A1A',
                border: '1px solid #FFB4AB',
                padding: '0.65rem 0.85rem',
                borderRadius: '8px',
                fontSize: '0.84rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem'
              }}>
                <AlertCircle size={15} style={{ flexShrink: 0 }} />
                <span>{errorMessage}</span>
              </div>
            )}

            {/* TAB CONTENT 1: DEMO EXPERIMENT MODE */}
            {authMode === 'demo' && (
              <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{
                  background: '#EFF6FF',
                  border: '1px solid #BFDBFE',
                  borderRadius: '12px',
                  padding: '1rem',
                  display: 'flex',
                  gap: '0.75rem',
                  alignItems: 'flex-start'
                }}>
                  <Sparkles size={20} color="#004AC6" style={{ flexShrink: 0, marginTop: '2px' }} />
                  <p style={{ fontSize: '0.86rem', color: '#1E40AF', lineHeight: 1.5, margin: 0 }}>
                    Akses instan ke data <strong>8 mahasiswa benchmark</strong> (Machine Learning, Web, Cloud, SAP) untuk mengeksplorasi seluruh kapabilitas mesin Explainable AI tanpa registrasi.
                  </p>
                </div>

                <button
                  onClick={handleLogin}
                  disabled={isLoading}
                  style={{
                    width: '100%',
                    padding: '0.85rem 1.25rem',
                    borderRadius: '10px',
                    background: 'linear-gradient(135deg, #004AC6 0%, #2563EB 100%)',
                    color: '#FFFFFF',
                    border: 'none',
                    fontWeight: 700,
                    fontSize: '0.96rem',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    gap: '0.5rem',
                    boxShadow: '0 4px 14px rgba(0, 74, 198, 0.3)',
                    transition: 'all 0.2s',
                    marginTop: '0.5rem'
                  }}
                >
                  {isLoading ? 'Memuat Data Demo...' : 'Eksplorasi Data Demo'}
                  <ArrowRight size={18} />
                </button>
              </div>
            )}

            {/* TAB CONTENT 2: LOGIN MAHASISWA */}
            {authMode === 'login' && (
              <form onSubmit={handleLogin} style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontFamily: 'var(--font-mono)', fontSize: '0.78rem', fontWeight: 700, color: '#191C1E', marginBottom: '0.35rem' }}>
                    Username / Akun
                  </label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Masukkan username (contoh: akmal)"
                    style={{
                      width: '100%',
                      padding: '0.7rem 0.9rem',
                      borderRadius: '10px',
                      border: '1px solid #C3C6D7',
                      background: '#FFFFFF',
                      fontSize: '0.92rem',
                      outline: 'none',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontFamily: 'var(--font-mono)', fontSize: '0.78rem', fontWeight: 700, color: '#191C1E', marginBottom: '0.35rem' }}>
                    Password
                  </label>
                  <div style={{ position: 'relative' }}>
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      style={{
                        width: '100%',
                        padding: '0.7rem 2.5rem 0.7rem 0.9rem',
                        borderRadius: '10px',
                        border: '1px solid #C3C6D7',
                        background: '#FFFFFF',
                        fontSize: '0.92rem',
                        outline: 'none',
                        boxSizing: 'border-box'
                      }}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      style={{
                        position: 'absolute',
                        right: '10px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'transparent',
                        border: 'none',
                        color: '#737686',
                        cursor: 'pointer'
                      }}
                    >
                      {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  style={{
                    width: '100%',
                    padding: '0.85rem 1.25rem',
                    borderRadius: '10px',
                    background: '#004AC6',
                    color: '#FFFFFF',
                    border: 'none',
                    fontWeight: 700,
                    fontSize: '0.96rem',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    gap: '0.5rem',
                    boxShadow: '0 4px 14px rgba(0, 74, 198, 0.25)',
                    transition: 'all 0.2s',
                    marginTop: '0.5rem'
                  }}
                >
                  {isLoading ? 'Memproses...' : 'Masuk Sistem'}
                </button>

                <div style={{ textAlign: 'center', fontSize: '0.82rem', color: '#737686', marginTop: '0.25rem' }}>
                  Belum punya akun?{' '}
                  <span 
                    onClick={() => switchMode('register')}
                    style={{ color: '#004AC6', fontWeight: 700, cursor: 'pointer', textDecoration: 'underline' }}
                  >
                    Daftar Mahasiswa Baru
                  </span>
                </div>
              </form>
            )}

            {/* TAB CONTENT 3: REGISTER NEW STUDENT */}
            {authMode === 'register' && (
              <form onSubmit={handleRegister} style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#191C1E', marginBottom: '0.25rem' }}>
                    Nama Lengkap
                  </label>
                  <input
                    type="text"
                    value={regName}
                    onChange={(e) => setRegName(e.target.value)}
                    placeholder="Nama Lengkap Mahasiswa"
                    style={{
                      width: '100%',
                      padding: '0.6rem 0.8rem',
                      borderRadius: '8px',
                      border: '1px solid #C3C6D7',
                      fontSize: '0.88rem',
                      outline: 'none',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#191C1E', marginBottom: '0.25rem' }}>
                    Username
                  </label>
                  <input
                    type="text"
                    value={regUsername}
                    onChange={(e) => setRegUsername(e.target.value)}
                    placeholder="Username baru"
                    style={{
                      width: '100%',
                      padding: '0.6rem 0.8rem',
                      borderRadius: '8px',
                      border: '1px solid #C3C6D7',
                      fontSize: '0.88rem',
                      outline: 'none',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#191C1E', marginBottom: '0.25rem' }}>
                    Password
                  </label>
                  <input
                    type="password"
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    placeholder="Password"
                    style={{
                      width: '100%',
                      padding: '0.6rem 0.8rem',
                      borderRadius: '8px',
                      border: '1px solid #C3C6D7',
                      fontSize: '0.88rem',
                      outline: 'none',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#191C1E', marginBottom: '0.25rem' }}>
                    Peminatan Karir
                  </label>
                  <select
                    value={regTrack}
                    onChange={(e) => setRegTrack(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.6rem 0.8rem',
                      borderRadius: '8px',
                      border: '1px solid #C3C6D7',
                      fontSize: '0.88rem',
                      background: '#FFFFFF',
                      boxSizing: 'border-box'
                    }}
                  >
                    <option value="Machine Learning & AI">🤖 Machine Learning & AI</option>
                    <option value="Web & Full-Stack">💻 Web & Full-Stack Development</option>
                    <option value="Networking & Cloud">☁️ Networking & Cloud Infrastructure</option>
                    <option value="SAP & Enterprise Systems">🏢 SAP & Enterprise Systems</option>
                  </select>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  style={{
                    width: '100%',
                    padding: '0.8rem',
                    borderRadius: '8px',
                    background: '#006C49',
                    color: '#FFFFFF',
                    border: 'none',
                    fontWeight: 700,
                    fontSize: '0.92rem',
                    cursor: 'pointer',
                    marginTop: '0.5rem'
                  }}
                >
                  {isLoading ? 'Mendaftarkan...' : 'Daftar & Masuk'}
                </button>

                <div style={{ textAlign: 'center', fontSize: '0.8rem', color: '#737686' }}>
                  Sudah punya akun?{' '}
                  <span 
                    onClick={() => switchMode('login')}
                    style={{ color: '#004AC6', fontWeight: 700, cursor: 'pointer', textDecoration: 'underline' }}
                  >
                    Kembali ke Login
                  </span>
                </div>
              </form>
            )}
          </div>
        </div>
      </main>

      {/* 4 Industry Track Cards matching Google Stitch Screen 3 */}
      <section style={{
        width: '100%',
        background: '#ECEEF0',
        borderTop: '1px solid rgba(195, 198, 215, 0.4)',
        padding: '2.5rem 2.5rem',
        marginTop: 'auto'
      }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
          <div style={{ marginBottom: '1.25rem' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#191C1E', fontFamily: 'var(--font-heading)' }}>
              Jalur Peminatan Industri yang Dianalisis
            </h2>
            <p style={{ fontSize: '0.9rem', color: '#434655', marginTop: '0.25rem' }}>
              Pemetaan kompetensi real-time terhadap peran teknologi teratas dengan model Cross-Encoder & XAI.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.25rem' }}>
            <div className="glass-panel glow-hover" style={{ padding: '1.25rem', borderRadius: '1rem', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem', background: '#FFFFFF' }}>
              <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'rgba(0, 74, 198, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#004AC6' }}>
                <Cpu size={24} />
              </div>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#191C1E' }}>Machine Learning & AI</h3>
            </div>

            <div className="glass-panel glow-hover" style={{ padding: '1.25rem', borderRadius: '1rem', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem', background: '#FFFFFF' }}>
              <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'rgba(0, 108, 73, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#006C49' }}>
                <Terminal size={24} />
              </div>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#191C1E' }}>Web & Full-Stack</h3>
            </div>

            <div className="glass-panel glow-hover" style={{ padding: '1.25rem', borderRadius: '1rem', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem', background: '#FFFFFF' }}>
              <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'rgba(37, 99, 235, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#2563EB' }}>
                <Cloud size={24} />
              </div>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#191C1E' }}>Cloud & DevOps</h3>
            </div>

            <div className="glass-panel glow-hover" style={{ padding: '1.25rem', borderRadius: '1rem', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem', background: '#FFFFFF' }}>
              <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'rgba(153, 97, 0, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#996100' }}>
                <Building size={24} />
              </div>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#191C1E' }}>SAP & Enterprise</h3>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        padding: '1.5rem 2.5rem',
        borderTop: '1px solid #E0E3E5',
        background: '#F2F4F6',
        fontSize: '0.82rem',
        color: '#737686',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        maxWidth: '1280px',
        margin: '0 auto',
        width: '100%'
      }}>
        <div>
          <strong>TalentXAI PRO</strong> — Pusat Riset Sains Data dan Informasi, BRIN © 2026.
        </div>
        <div style={{ display: 'flex', gap: '1.5rem' }}>
          <span>Outcome-Based Education</span>
          <span>•</span>
          <span>Explainable AI (XAI)</span>
          <span>•</span>
          <span>SBERT Cross-Encoder</span>
        </div>
      </footer>
    </div>
  );
}
