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
  FlaskConical, 
  ArrowRight, 
  CheckCircle2, 
  Zap, 
  BarChart3, 
  Eye, 
  EyeOff,
  AlertCircle,
  Layers,
  Search
} from 'lucide-react';

export default function LandingPortal({ onLoginSuccess }) {
  const [authMode, setAuthMode] = useState('demo'); // 'demo' | 'student' | 'register'
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
    } else if (mode === 'student') {
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
      setErrorMessage('Gagal terhubung ke backend: ' + err.message);
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
        setErrorMessage(json.detail || 'Terjadi kesalahan pendaftaran.');
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
      background: 'radial-gradient(circle at 10% 20%, #0F172A 0%, #1E293B 40%, #0B1E48 100%)',
      color: '#FFFFFF',
      fontFamily: 'var(--font-main)',
      display: 'flex',
      flexDirection: 'column',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Background Glow Decorations */}
      <div style={{
        position: 'absolute',
        top: '-15%',
        right: '-10%',
        width: '600px',
        height: '600px',
        background: 'radial-gradient(circle, rgba(37,99,235,0.28) 0%, rgba(0,0,0,0) 70%)',
        pointerEvents: 'none'
      }} />
      <div style={{
        position: 'absolute',
        bottom: '-15%',
        left: '-10%',
        width: '500px',
        height: '500px',
        background: 'radial-gradient(circle, rgba(16,185,129,0.2) 0%, rgba(0,0,0,0) 70%)',
        pointerEvents: 'none'
      }} />

      {/* Top Brand Bar */}
      <header className="landing-header" style={{
        padding: '1.25rem 3rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(10px)',
        zIndex: 10
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 900,
            fontSize: '1.3rem',
            boxShadow: '0 4px 14px rgba(37, 99, 235, 0.4)'
          }}>
            <Briefcase size={22} />
          </div>
          <div>
            <div style={{ fontSize: '1.3rem', fontWeight: 900, letterSpacing: '-0.03em', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              TalentXAI
              <span style={{ fontSize: '0.65rem', background: 'rgba(59,130,246,0.3)', color: '#93C5FD', padding: '0.15rem 0.45rem', borderRadius: '6px', border: '1px solid rgba(147,197,253,0.3)' }}>PRO</span>
            </div>
            <div style={{ fontSize: '0.72rem', color: '#94A3B8', fontWeight: 600, letterSpacing: '0.02em' }}>
              Badan Riset dan Inovasi Nasional (BRIN)
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            background: 'rgba(255,255,255,0.08)',
            padding: '0.4rem 0.85rem',
            borderRadius: '9999px',
            fontSize: '0.8rem',
            color: '#E2E8F0',
            border: '1px solid rgba(255,255,255,0.12)'
          }}>
            <ShieldCheck size={15} color="#10B981" />
            <span>Riset OBE & Explainable AI (XAI)</span>
          </div>
        </div>
      </header>

      {/* Main Split Content */}
      <main className="landing-main-grid" style={{
        flex: 1,
        display: 'grid',
        gridTemplateColumns: '1.15fr 0.85fr',
        gap: '3rem',
        padding: '3.5rem 3.5rem 2.5rem 3.5rem',
        maxWidth: '1400px',
        margin: '0 auto',
        width: '100%',
        alignItems: 'center',
        zIndex: 10
      }}>
        {/* Left Side: Hero Value Proposition */}
        <div>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            background: 'rgba(37,99,235,0.15)',
            border: '1px solid rgba(59,130,246,0.4)',
            padding: '0.35rem 0.9rem',
            borderRadius: '9999px',
            fontSize: '0.82rem',
            fontWeight: 700,
            color: '#60A5FA',
            marginBottom: '1.25rem'
          }}>
            <Sparkles size={15} />
            Next-Gen Explainable AI Career Platform
          </div>

          <h1 className="landing-hero-title" style={{
            fontSize: '2.85rem',
            fontWeight: 900,
            lineHeight: 1.15,
            letterSpacing: '-0.035em',
            marginBottom: '1.25rem',
            background: 'linear-gradient(135deg, #FFFFFF 0%, #E2E8F0 60%, #93C5FD 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            Pintu Masuk Karir Cerdas Berbasis Capaian OBE & Portofolio Industri
          </h1>

          <p className="landing-hero-desc" style={{
            fontSize: '1.05rem',
            color: '#CBD5E1',
            lineHeight: 1.6,
            marginBottom: '2rem',
            maxWidth: '620px'
          }}>
            Platform cerdas yang mengintegrasikan transkrip <strong>KHS multi-semester (138 SKS)</strong>, 
            kredibilitas <strong>sertifikasi industri (Tier A/B)</strong>, serta transparansi 
            rekomendasi berbasis <strong>Cross-Encoder Neural Matching, SHAP Attribution</strong>, dan bimbingan <strong>DiCE Counterfactuals</strong>.
          </p>

          {/* 3 Core Value Cards */}
          <div className="landing-cards-row" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '2.5rem' }}>
            <div style={{
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '16px',
              padding: '1.1rem',
              backdropFilter: 'blur(8px)'
            }}>
              <div style={{ color: '#38BDF8', marginBottom: '0.4rem' }}>
                <Zap size={22} />
              </div>
              <div style={{ fontSize: '0.92rem', fontWeight: 800, marginBottom: '0.2rem' }}>
                Neural Re-Ranking
              </div>
              <div style={{ fontSize: '0.78rem', color: '#94A3B8', lineHeight: 1.4 }}>
                SBERT + Cross-Encoder mMARCO miniLMv2
              </div>
            </div>

            <div style={{
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '16px',
              padding: '1.1rem',
              backdropFilter: 'blur(8px)'
            }}>
              <div style={{ color: '#10B981', marginBottom: '0.4rem' }}>
                <Award size={22} />
              </div>
              <div style={{ fontSize: '0.92rem', fontWeight: 800, marginBottom: '0.2rem' }}>
                Tier A/B Credibility
              </div>
              <div style={{ fontSize: '0.78rem', color: '#94A3B8', lineHeight: 1.4 }}>
                Bobot resmi Google, AWS, Meta, SAP, Cisco
              </div>
            </div>

            <div style={{
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '16px',
              padding: '1.1rem',
              backdropFilter: 'blur(8px)'
            }}>
              <div style={{ color: '#A78BFA', marginBottom: '0.4rem' }}>
                <BarChart3 size={22} />
              </div>
              <div style={{ fontSize: '0.92rem', fontWeight: 800, marginBottom: '0.2rem' }}>
                Explainable AI (XAI)
              </div>
              <div style={{ fontSize: '0.78rem', color: '#94A3B8', lineHeight: 1.4 }}>
                Atribusi SHAP & Counterfactuals DiCE
              </div>
            </div>
          </div>

          {/* Platform Live Stats */}
          <div className="landing-stats-row" style={{
            display: 'flex',
            alignItems: 'center',
            gap: '2rem',
            paddingTop: '1.5rem',
            borderTop: '1px solid rgba(255,255,255,0.1)'
          }}>
            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: 900, color: '#38BDF8', fontFamily: 'var(--font-heading)' }}>
                4.570+
              </div>
              <div style={{ fontSize: '0.75rem', color: '#94A3B8', textTransform: 'uppercase', fontWeight: 600 }}>
                Lowongan Riil Unified
              </div>
            </div>

            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: 900, color: '#10B981', fontFamily: 'var(--font-heading)' }}>
                10 Mahasiswa
              </div>
              <div style={{ fontSize: '0.75rem', color: '#94A3B8', textTransform: 'uppercase', fontWeight: 600 }}>
                Benchmark 5 Track EKS13
              </div>
            </div>

            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: 900, color: '#F59E0B', fontFamily: 'var(--font-heading)' }}>
                1.139
              </div>
              <div style={{ fontSize: '0.75rem', color: '#94A3B8', textTransform: 'uppercase', fontWeight: 600 }}>
                Katalog Kursus DiCE
              </div>
            </div>
          </div>
        </div>

        {/* Right Side: Interactive Login Portal Card */}
        <div className="landing-login-card" style={{
          background: 'rgba(255, 255, 255, 0.96)',
          borderRadius: '24px',
          padding: '2.5rem',
          color: '#0F172A',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 40px rgba(37,99,235,0.2)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          position: 'relative'
        }}>
          {/* Card Title */}
          <div style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
            <div style={{
              width: '52px',
              height: '52px',
              borderRadius: '16px',
              background: authMode === 'demo' ? 'linear-gradient(135deg, #2563EB, #1D4ED8)' : 'linear-gradient(135deg, #10B981, #059669)',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 0.75rem auto',
              boxShadow: '0 8px 16px rgba(0,0,0,0.1)'
            }}>
              {authMode === 'demo' ? <FlaskConical size={26} /> : <User size={26} />}
            </div>
            <h2 style={{ fontSize: '1.55rem', fontWeight: 900, color: '#0F172A', letterSpacing: '-0.02em' }}>
              Autentikasi Akses Platform
            </h2>
            <p style={{ fontSize: '0.85rem', color: '#64748B', marginTop: '0.2rem' }}>
              Pilih mode akun untuk masuk ke dashboard TalentXAI
            </p>
          </div>

          {/* 3-Mode Selector */}
          <div style={{
            display: 'flex',
            background: '#F1F5F9',
            padding: '4px',
            borderRadius: '14px',
            marginBottom: '1.5rem',
            border: '1px solid #E2E8F0'
          }}>
            <button
              onClick={() => switchMode('demo')}
              style={{
                flex: 1,
                padding: '0.6rem 0.5rem',
                borderRadius: '11px',
                border: 'none',
                fontSize: '0.82rem',
                fontWeight: 800,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.35rem',
                background: authMode === 'demo' ? '#FFFFFF' : 'transparent',
                color: authMode === 'demo' ? '#1E293B' : '#64748B',
                boxShadow: authMode === 'demo' ? '0 2px 8px rgba(0,0,0,0.08)' : 'none',
                transition: 'all 0.15s ease'
              }}
            >
              <FlaskConical size={14} color={authMode === 'demo' ? '#2563EB' : '#64748B'} />
              Akun Demo (10 Riset)
            </button>

            <button
              onClick={() => switchMode('student')}
              style={{
                flex: 1,
                padding: '0.6rem 0.5rem',
                borderRadius: '11px',
                border: 'none',
                fontSize: '0.82rem',
                fontWeight: 800,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.35rem',
                background: authMode === 'student' ? '#FFFFFF' : 'transparent',
                color: authMode === 'student' ? '#1E293B' : '#64748B',
                boxShadow: authMode === 'student' ? '0 2px 8px rgba(0,0,0,0.08)' : 'none',
                transition: 'all 0.15s ease'
              }}
            >
              <User size={14} color={authMode === 'student' ? '#10B981' : '#64748B'} />
              Akun Mahasiswa
            </button>

            <button
              onClick={() => switchMode('register')}
              style={{
                flex: 1,
                padding: '0.6rem 0.5rem',
                borderRadius: '11px',
                border: 'none',
                fontSize: '0.82rem',
                fontWeight: 800,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.35rem',
                background: authMode === 'register' ? '#FFFFFF' : 'transparent',
                color: authMode === 'register' ? '#1E293B' : '#64748B',
                boxShadow: authMode === 'register' ? '0 2px 8px rgba(0,0,0,0.08)' : 'none',
                transition: 'all 0.15s ease'
              }}
            >
              <Sparkles size={14} color={authMode === 'register' ? '#8B5CF6' : '#64748B'} />
              Daftar Baru
            </button>
          </div>

          {/* Error Banner */}
          {errorMessage && (
            <div style={{
              background: '#FEF2F2',
              border: '1px solid #FECACA',
              color: '#991B1B',
              padding: '0.75rem 1rem',
              borderRadius: '12px',
              fontSize: '0.84rem',
              marginBottom: '1.25rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <AlertCircle size={16} flexShrink={0} />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* FORM 1: LOGIN (Demo & Student) */}
          {(authMode === 'demo' || authMode === 'student') && (
            <form onSubmit={handleLogin}>
              <div style={{ marginBottom: '1.1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#334155', marginBottom: '0.35rem' }}>
                  Username
                </label>
                <div style={{ position: 'relative' }}>
                  <input 
                    type="text"
                    placeholder="Masukkan username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    style={{
                      width: '100%',
                      padding: '0.75rem 1rem 0.75rem 2.6rem',
                      borderRadius: '12px',
                      border: '1px solid #CBD5E1',
                      fontSize: '0.92rem',
                      outline: 'none',
                      color: '#0F172A',
                      background: '#FFFFFF'
                    }}
                  />
                  <User size={18} style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: '#94A3B8' }} />
                </div>
              </div>

              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#334155', marginBottom: '0.35rem' }}>
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
                      padding: '0.75rem 2.6rem 0.75rem 2.6rem',
                      borderRadius: '12px',
                      border: '1px solid #CBD5E1',
                      fontSize: '0.92rem',
                      outline: 'none',
                      color: '#0F172A',
                      background: '#FFFFFF'
                    }}
                  />
                  <Lock size={18} style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: '#94A3B8' }} />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    style={{ position: 'absolute', right: '0.85rem', top: '50%', transform: 'translateY(-50%)', background: 'transparent', border: 'none', cursor: 'pointer', color: '#94A3B8' }}
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                style={{
                  width: '100%',
                  padding: '0.85rem',
                  borderRadius: '14px',
                  border: 'none',
                  background: authMode === 'demo' ? 'linear-gradient(135deg, #2563EB, #1D4ED8)' : 'linear-gradient(135deg, #10B981, #059669)',
                  color: 'white',
                  fontWeight: 800,
                  fontSize: '1rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.5rem',
                  boxShadow: authMode === 'demo' ? '0 4px 14px rgba(37, 99, 235, 0.35)' : '0 4px 14px rgba(16, 185, 129, 0.35)',
                  transition: 'transform 0.15s ease'
                }}
              >
                {isLoading ? 'Memverifikasi...' : (
                  <>
                    <span>{authMode === 'demo' ? '🚀 Masuk ke Mode Demo (10 Riset)' : '🚀 Masuk ke Akun Mahasiswa'}</span>
                    <ArrowRight size={18} />
                  </>
                )}
              </button>

              {/* Mode Specific Footnote */}
              <div style={{
                marginTop: '1.25rem',
                padding: '0.85rem',
                borderRadius: '12px',
                background: authMode === 'demo' ? '#EFF6FF' : '#ECFDF5',
                border: authMode === 'demo' ? '1px solid #BFDBFE' : '1px solid #A7F3D0',
                fontSize: '0.78rem',
                color: authMode === 'demo' ? '#1E40AF' : '#065F46',
                lineHeight: 1.45
              }}>
                {authMode === 'demo' ? (
                  <div>
                    <strong>💡 Info Akun Demo:</strong> Kredensial bawaan <code>demo</code> / <code>123</code>. Anda dapat mengamati 10 profil mahasiswa hasil riset dengan komparasi A/B testing sebelum vs sesudah sertifikat.
                  </div>
                ) : (
                  <div>
                    <strong>💡 Info Akun Mahasiswa:</strong> Kredensial bawaan <code>akmal</code> / <code>123</code>. Anda dapat menginput daftar mata kuliah KHS dan sertifikasi industri Anda sendiri.
                  </div>
                )}
              </div>
            </form>
          )}

          {/* FORM 2: REGISTER */}
          {authMode === 'register' && (
            <form onSubmit={handleRegister}>
              <div style={{ marginBottom: '0.85rem' }}>
                <label style={{ display: 'block', fontSize: '0.84rem', fontWeight: 700, color: '#334155', marginBottom: '0.3rem' }}>
                  Nama Lengkap Mahasiswa
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
                  <label style={{ display: 'block', fontSize: '0.84rem', fontWeight: 700, color: '#334155', marginBottom: '0.3rem' }}>
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
                  <label style={{ display: 'block', fontSize: '0.84rem', fontWeight: 700, color: '#334155', marginBottom: '0.3rem' }}>
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
                <label style={{ display: 'block', fontSize: '0.84rem', fontWeight: 700, color: '#334155', marginBottom: '0.3rem' }}>
                  Peminatan / Minat Bidang
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
                style={{
                  width: '100%',
                  padding: '0.85rem',
                  borderRadius: '14px',
                  border: 'none',
                  background: 'linear-gradient(135deg, #10B981, #059669)',
                  color: 'white',
                  fontWeight: 800,
                  fontSize: '1rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.5rem',
                  boxShadow: '0 4px 14px rgba(16, 185, 129, 0.35)'
                }}
              >
                {isLoading ? 'Mendaftarkan...' : '✨ Daftarkan Akun & Masuk Dashboard'}
              </button>
            </form>
          )}
        </div>
      </main>

      {/* Bottom Footer */}
      <footer className="landing-footer" style={{
        padding: '1.25rem 3rem',
        borderTop: '1px solid rgba(255,255,255,0.08)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: '0.78rem',
        color: '#64748B',
        zIndex: 10
      }}>
        <div>
          © 2026 TalentXAI — Program Magang Riset Badan Riset dan Inovasi Nasional (BRIN).
        </div>
        <div style={{ display: 'flex', gap: '1.5rem' }}>
          <span>Outcome-Based Education (OBE)</span>
          <span>•</span>
          <span>Sentence-BERT Cross-Encoder</span>
          <span>•</span>
          <span>SHAP & DiCE Framework</span>
        </div>
      </footer>
    </div>
  );
}
