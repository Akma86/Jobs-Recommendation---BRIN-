import React from 'react';
import { 
  Briefcase, 
  Sparkles, 
  UserCheck, 
  Compass, 
  FileText, 
  Bookmark, 
  CheckCircle2,
  ChevronDown
} from 'lucide-react';

export default function Navbar({ 
  students, 
  selectedStudentId, 
  onSelectStudent, 
  activeTab, 
  setActiveTab,
  onOpenProfileModal,
  onOpenDreamModal,
  savedCount
}) {
  const currentStudent = students.find(s => s.id === selectedStudentId);

  return (
    <header className="navbar">
      {/* Brand */}
      <div className="brand-logo" onClick={() => setActiveTab('explore')}>
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
        <button 
          className={`nav-btn ${activeTab === 'explore' ? 'active' : ''}`}
          onClick={() => setActiveTab('explore')}
        >
          <Briefcase size={16} />
          Explore Matches
        </button>

        <button 
          className={`nav-btn ${activeTab === 'dream' ? 'active' : ''}`}
          onClick={onOpenDreamModal}
        >
          <Compass size={16} />
          Target Dream Career
        </button>

        <button 
          className={`nav-btn ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={onOpenProfileModal}
        >
          <FileText size={16} />
          KHS & Certifications
        </button>
      </nav>

      {/* 1-Click Demo Student Switcher */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
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
              Aktif: {currentStudent?.track || 'Student'}
            </span>
            <select 
              className="student-select"
              value={selectedStudentId}
              onChange={(e) => onSelectStudent(e.target.value)}
            >
              {students.map((st) => (
                <option key={st.id} value={st.id}>
                  {st.name} ({st.track} — {st.profile_type})
                </option>
              ))}
            </select>
          </div>
          <ChevronDown size={14} color="#64748B" />
        </div>
      </div>
    </header>
  );
}
