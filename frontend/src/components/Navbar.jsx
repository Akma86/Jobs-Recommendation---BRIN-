import React from 'react';
import { 
  Briefcase, 
  Sparkles, 
  UserCheck, 
  Compass, 
  FileText, 
  Bookmark, 
  CheckCircle2,
  ChevronDown,
  User,
  FlaskConical,
  Edit3
} from 'lucide-react';

export default function Navbar({ 
  students, 
  selectedStudentId, 
  onSelectStudent, 
  activeTab, 
  setActiveTab,
  accountMode,
  setAccountMode,
  authUser,
  onOpenAuthModal,
  onLogout,
  onOpenProfileModal,
  onOpenUploadModal,
  savedCount,
  hasRecommendations = true
}) {
  const currentStudent = students.find(s => s.id === selectedStudentId);
  const demoStudents = students.filter(s => s.is_demo !== false);
  const customStudents = students.filter(s => s.is_demo === false);

  const handleModeToggle = (mode) => {
    setAccountMode(mode);
    if (mode === 'demo') {
      const firstDemo = demoStudents[0];
      if (firstDemo) onSelectStudent(firstDemo.id);
    } else {
      const firstCustom = customStudents[0] || students.find(s => s.id === 'user-dummy');
      if (firstCustom) onSelectStudent(firstCustom.id);
      else onOpenUploadModal();
    }
  };

  return (
    <header className="navbar">
      {/* Brand */}
      <div className="brand-logo" onClick={() => setActiveTab(hasRecommendations ? 'recommend' : 'explore_all')}>
        <div className="logo-icon-box">
          <Briefcase size={22} />
        </div>
        <div className="brand-text">
          <div className="brand-name">
            TalentXAI
            <span style={{ fontSize: '0.65rem', background: '#DBEAFE', color: '#1E40AF', padding: '0.1rem 0.4rem', borderRadius: '6px', fontWeight: 800 }}>PRO</span>
          </div>
          <div className="brand-tag">
            <span className="pulse-dot"></span>
            Career Intelligence Platform
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <nav className="nav-links">
        {hasRecommendations ? (
          <button 
            className={`nav-btn ${activeTab === 'recommend' ? 'active' : ''}`}
            onClick={() => setActiveTab('recommend')}
          >
            <Sparkles size={16} />
            🎯 Rekomendasi Karir
          </button>
        ) : (
          <button 
            className="nav-btn"
            onClick={onOpenUploadModal}
            style={{ background: '#ECFDF5', color: '#065F46', border: '1px dashed #A7F3D0' }}
            title="Klik untuk input KHS & menghasilkan rekomendasi karir"
          >
            <Sparkles size={16} color="#059669" />
            ✨ Buat Rekomendasi (Input KHS)
          </button>
        )}

        <button 
          className={`nav-btn ${activeTab === 'explore_all' ? 'active' : ''}`}
          onClick={() => setActiveTab('explore_all')}
        >
          <Briefcase size={16} />
          🌐 Eksplor Katalog (4.570+)
        </button>

        <button 
          className={`nav-btn ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={onOpenProfileModal}
        >
          <FileText size={16} />
          📚 KHS & Sertifikat
        </button>
      </nav>

      {/* Right Controls: Mode Toggle & Student Selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
        {/* Account Mode Switcher (Demo vs Custom User) */}
        <div style={{
          display: 'flex',
          background: '#F1F5F9',
          padding: '3px',
          borderRadius: '12px',
          border: '1px solid #E2E8F0'
        }}>
          <button
            onClick={() => handleModeToggle('demo')}
            style={{
              padding: '0.35rem 0.65rem',
              fontSize: '0.78rem',
              fontWeight: 700,
              borderRadius: '9px',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              background: accountMode === 'demo' ? '#FFFFFF' : 'transparent',
              color: accountMode === 'demo' ? '#1E293B' : '#64748B',
              boxShadow: accountMode === 'demo' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
              transition: 'all 0.15s ease'
            }}
          >
            <FlaskConical size={14} color={accountMode === 'demo' ? '#2563EB' : '#64748B'} />
            Akun Demo
          </button>

          <button
            onClick={() => handleModeToggle('custom')}
            style={{
              padding: '0.35rem 0.65rem',
              fontSize: '0.78rem',
              fontWeight: 700,
              borderRadius: '9px',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              background: accountMode === 'custom' ? '#FFFFFF' : 'transparent',
              color: accountMode === 'custom' ? '#1E293B' : '#64748B',
              boxShadow: accountMode === 'custom' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
              transition: 'all 0.15s ease'
            }}
          >
            <User size={14} color={accountMode === 'custom' ? '#10B981' : '#64748B'} />
            Akun Pengguna
          </button>
        </div>

        {/* Dynamic Action Button / Selector based on Mode */}
        {accountMode === 'custom' ? (
          <button 
            className="btn-primary"
            onClick={onOpenUploadModal}
            style={{ 
              fontSize: '0.82rem', 
              padding: '0.45rem 0.85rem', 
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #10B981, #059669)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem'
            }}
          >
            <Edit3 size={15} />
            Input KHS Mandiri
          </button>
        ) : (
          <div className="student-selector-bar">
            <div style={{
              width: '28px', 
              height: '28px', 
              borderRadius: '8px', 
              background: currentStudent?.is_good ? '#10B981' : '#EF4444',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.75rem',
              fontWeight: 800
            }}>
              {currentStudent?.name?.charAt(0) || 'U'}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ fontSize: '0.65rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase' }}>
                Profil: {currentStudent?.track || 'Student'}
              </span>
              <select 
                className="student-select"
                value={selectedStudentId}
                onChange={(e) => onSelectStudent(e.target.value)}
              >
                {demoStudents.map((st) => (
                  <option key={st.id} value={st.id}>
                    {st.name} ({st.track} — {st.profile_type})
                  </option>
                ))}
              </select>
            </div>
            <ChevronDown size={14} color="#64748B" />
          </div>
        )}

        {/* Auth User Profile Pill / Login Button */}
        {authUser ? (
          <div 
            onClick={onLogout}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.35rem 0.65rem',
              borderRadius: '10px',
              background: '#F8FAFC',
              border: '1px solid #E2E8F0',
              cursor: 'pointer',
              fontSize: '0.8rem',
              fontWeight: 700,
              color: '#334155'
            }}
            title="Klik untuk Keluar / Ganti Akun"
          >
            <div style={{
              width: '24px',
              height: '24px',
              borderRadius: '50%',
              background: authUser.is_demo ? '#2563EB' : '#10B981',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.7rem',
              fontWeight: 800
            }}>
              {authUser.name?.charAt(0) || 'U'}
            </div>
            <span>{authUser.username}</span>
            <span style={{ fontSize: '0.68rem', color: '#94A3B8' }}>(Keluar)</span>
          </div>
        ) : (
          <button
            onClick={onOpenAuthModal}
            className="btn-outline"
            style={{
              fontSize: '0.82rem',
              padding: '0.45rem 0.75rem',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem'
            }}
          >
            <User size={15} />
            Masuk / Login
          </button>
        )}
      </div>
    </header>
  );
}
