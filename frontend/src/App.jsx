import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import JobCard from './components/JobCard';
import JobDetailDrawer from './components/JobDetailDrawer';
import StudentProfileModal from './components/StudentProfileModal';
import DreamJobExplorer from './components/DreamJobExplorer';
import UploadModal from './components/UploadModal';
import AuthModal from './components/AuthModal';
import LandingPortal from './components/LandingPortal';
import { 
  Sparkles, 
  Search, 
  BookOpen, 
  Award, 
  TrendingUp, 
  GraduationCap, 
  Briefcase,
  CheckCircle2,
  Compass,
  FileText,
  Upload,
  Edit3,
  User,
  FlaskConical,
  Lock,
  Sliders,
  Columns,
  Layout,
  Maximize2,
  Minimize2,
  PanelLeftClose,
  PanelLeftOpen
} from 'lucide-react';

const CATEGORIES = [
  { id: 'all', label: '🔥 Semua Rekomendasi' },
  { id: 'machine learning', label: '🤖 AI & Machine Learning' },
  { id: 'web', label: '💻 Web & Frontend' },
  { id: 'cloud', label: '☁️ Cloud & DevOps' },
  { id: 'network', label: '🔒 Jaringan & Security' },
  { id: 'data', label: '📊 Data Analytics & BI' },
  { id: 'sap', label: '🏢 Enterprise & SAP' },
];

export default function App() {
  const [students, setStudents] = useState([]);
  const [accountMode, setAccountMode] = useState('demo'); // 'demo' | 'custom'
  const [selectedStudentId, setSelectedStudentId] = useState('budi-santoso-web-bagus');
  const [studentData, setStudentData] = useState(null);
  const [activeJob, setActiveJob] = useState(null);
  const [activeTab, setActiveTab] = useState('recommend'); // 'recommend' | 'explore_all'
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [catalogJobs, setCatalogJobs] = useState([]);
  const [catalogTotal, setCatalogTotal] = useState(4570);
  const [isCatalogLoading, setIsCatalogLoading] = useState(false);

  // Resizable Panel & Density States
  const [panelWidth, setPanelWidth] = useState(460);
  const [isDragging, setIsDragging] = useState(false);
  const [cardDensity, setCardDensity] = useState('comfortable'); // 'comfortable' | 'compact'
  const [isListCollapsed, setIsListCollapsed] = useState(false);

  const handleMouseDown = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isDragging) return;
      const newWidth = Math.min(750, Math.max(300, e.clientX - 32));
      setPanelWidth(newWidth);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isDragging]);

  // Authentication State
  const [authUser, setAuthUser] = useState(() => {
    try {
      const saved = localStorage.getItem('talentxai_auth_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [showAuthModal, setShowAuthModal] = useState(false);

  const handleAuthSuccess = (user) => {
    setAuthUser(user);
    if (user.is_demo) {
      setAccountMode('demo');
      setSelectedStudentId(user.student_id || 'siti-rahma-ml-bagus');
    } else {
      setAccountMode('custom');
      setSelectedStudentId(user.student_id || 'user-dummy');
    }
    fetchStudents();
  };

  const handleLogout = () => {
    localStorage.removeItem('talentxai_auth_user');
    setAuthUser(null);
    setShowAuthModal(true);
  };

  // Fetch from /api/jobs for 'explore_all' catalog mode
  useEffect(() => {
    if (activeTab !== 'explore_all') return;
    setIsCatalogLoading(true);
    const timeout = setTimeout(() => {
      const q = encodeURIComponent(searchQuery);
      const cat = encodeURIComponent(selectedCategory);
      const stId = encodeURIComponent(selectedStudentId || '');
      fetch(`/api/jobs?query=${q}&category=${cat}&student_id=${stId}&limit=60`)
        .then(res => res.json())
        .then(json => {
          if (json.status === 'success') {
            setCatalogJobs(json.data || []);
            setCatalogTotal(json.total || 0);
            if (json.data && json.data.length > 0) {
              setActiveJob(json.data[0]);
            }
          }
        })
        .catch(err => console.error('Error fetching catalog jobs:', err))
        .finally(() => setIsCatalogLoading(false));
    }, 250);

    return () => clearTimeout(timeout);
  }, [activeTab, searchQuery, selectedCategory, selectedStudentId]);

  const [savedJobs, setSavedJobs] = useState(() => {
    try {
      const saved = localStorage.getItem('talentxai_saved_jobs');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [appliedJobs, setAppliedJobs] = useState([]);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showDreamModal, setShowDreamModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // 1. Fetch Students List
  const fetchStudents = () => {
    fetch('/api/students')
      .then(res => res.json())
      .then(json => {
        if (json.status === 'success' && json.data.length > 0) {
          setStudents(json.data);
        }
      })
      .catch(err => console.error('Error fetching students:', err));
  };

  useEffect(() => {
    fetchStudents();
  }, []);

  const handleProfileAnalyzed = (customStudent) => {
    setAccountMode('custom');
    setStudentData(customStudent);
    setSelectedStudentId(customStudent.id);
    if (customStudent.recommended_jobs && customStudent.recommended_jobs.length > 0) {
      setActiveJob(customStudent.recommended_jobs[0]);
    }
    fetchStudents();
  };

  // 2. Fetch Student Detail on Selection Change
  useEffect(() => {
    if (!selectedStudentId) return;
    setIsLoading(true);
    fetch(`/api/student/${selectedStudentId}`)
      .then(res => res.json())
      .then(json => {
        if (json.status === 'success') {
          setStudentData(json.data);
          if (activeTab === 'recommend' && json.data.recommended_jobs && json.data.recommended_jobs.length > 0) {
            setActiveJob(json.data.recommended_jobs[0]);
          }
        }
      })
      .catch(err => console.error('Error fetching student detail:', err))
      .finally(() => setIsLoading(false));
  }, [selectedStudentId]);

  // Handle Save Job
  const handleToggleSave = (jobId) => {
    let next;
    if (savedJobs.includes(jobId)) {
      next = savedJobs.filter(id => id !== jobId);
    } else {
      next = [...savedJobs, jobId];
    }
    setSavedJobs(next);
    localStorage.setItem('talentxai_saved_jobs', JSON.stringify(next));
  };

  // Handle Apply Job
  const handleApply = (jobId) => {
    if (!appliedJobs.includes(jobId)) {
      setAppliedJobs([...appliedJobs, jobId]);
    }
  };

  const [evaluationMode, setEvaluationMode] = useState('after'); // 'after' | 'before' | 'compare'

  // Recommended Jobs from recommendations.csv
  const currentRecommendedList = evaluationMode === 'before' 
    ? (studentData?.recommended_jobs_before || studentData?.recommended_jobs || [])
    : (studentData?.recommended_jobs_after || studentData?.recommended_jobs || []);

  const filteredRecommendedJobs = currentRecommendedList.filter(job => {
    const matchesSearch = searchQuery === '' || 
      job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.company.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesCategory = selectedCategory === 'all' || 
      job.title.toLowerCase().includes(selectedCategory) ||
      (selectedCategory === 'web' && (job.title.toLowerCase().includes('front') || job.title.toLowerCase().includes('web') || job.title.toLowerCase().includes('html'))) ||
      (selectedCategory === 'machine learning' && (job.title.toLowerCase().includes('ml') || job.title.toLowerCase().includes('ai') || job.title.toLowerCase().includes('learning'))) ||
      (selectedCategory === 'cloud' && (job.title.toLowerCase().includes('cloud') || job.title.toLowerCase().includes('devops') || job.title.toLowerCase().includes('aws'))) ||
      (selectedCategory === 'network' && (job.title.toLowerCase().includes('network') || job.title.toLowerCase().includes('security') || job.title.toLowerCase().includes('cisco'))) ||
      (selectedCategory === 'data' && (job.title.toLowerCase().includes('data') || job.title.toLowerCase().includes('analyst') || job.title.toLowerCase().includes('bi'))) ||
      (selectedCategory === 'sap' && (job.title.toLowerCase().includes('sap') || job.title.toLowerCase().includes('enterprise') || job.title.toLowerCase().includes('erp')));

    return matchesSearch && matchesCategory;
  });

  // If not logged in, render the Landing & Authentication Gateway Portal
  if (!authUser) {
    return <LandingPortal onLoginSuccess={handleAuthSuccess} />;
  }

  // Displayed jobs based on active tab
  const displayedJobs = activeTab === 'recommend' ? filteredRecommendedJobs : catalogJobs;

  return (
    <div className="app-container">
      {/* Navbar */}
      <Navbar 
        students={students}
        selectedStudentId={selectedStudentId}
        onSelectStudent={setSelectedStudentId}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        accountMode={accountMode}
        setAccountMode={setAccountMode}
        authUser={authUser}
        onOpenAuthModal={() => setShowAuthModal(true)}
        onLogout={handleLogout}
        onOpenProfileModal={() => setShowProfileModal(true)}
        onOpenDreamModal={() => setShowDreamModal(true)}
        onOpenUploadModal={() => setShowUploadModal(true)}
        savedCount={savedJobs.length}
      />

      {/* Hero Banner */}
      <section className="hero-banner">
        <div className="hero-left">
          <div className="hero-badge-pill">
            <Sparkles size={14} style={{ marginRight: '6px' }} />
            Next-Gen Explainable AI Career Platform
          </div>
          <h1 className="hero-title">
            Peluang Karir Terbaik Berbasis Capaian OBE & Sertifikasi Industri
          </h1>
          <p className="hero-subtitle">
            Menganalisis integrasi transkrip KHS kurikulum dan portofolio kredensial resmi menggunakan model <strong>Sentence-BERT Cross-Encoder</strong>, atribusi <strong>SHAP</strong>, dan bimbingan <strong>DiCE</strong>.
          </p>
        </div>

        <div className="hero-stats">
          <div className="stat-box">
            <div className="stat-value">4.570</div>
            <div className="stat-label">Lowongan Riil</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">1.139</div>
            <div className="stat-label">Katalog Kursus</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">&lt; 5ms</div>
            <div className="stat-label">Respon AI</div>
          </div>
        </div>
      </section>

      {/* Candidate Profile Bar */}
      {studentData && (
        <div className="candidate-bar" style={{
          border: accountMode === 'custom' ? '2px solid #10B981' : '1px solid #E2E8F0',
          background: accountMode === 'custom' ? 'linear-gradient(to right, #F0FDF4, #FFFFFF)' : '#FFFFFF'
        }}>
          <div className="candidate-left">
            <div className="candidate-avatar" style={{
              background: accountMode === 'custom' ? 'linear-gradient(135deg, #10B981, #059669)' : '#2563EB'
            }}>
              {studentData.name.charAt(0)}
            </div>
            <div className="candidate-info">
              <h3>
                {studentData.name}
                <span style={{
                  fontSize: '0.72rem',
                  background: accountMode === 'custom' ? '#D1FAE5' : (studentData.is_good ? '#ECFDF5' : '#FEF2F2'),
                  color: accountMode === 'custom' ? '#065F46' : (studentData.is_good ? '#065F46' : '#991B1B'),
                  border: `1px solid ${accountMode === 'custom' ? '#6EE7B7' : (studentData.is_good ? '#A7F3D0' : '#FECACA')}`,
                  padding: '0.15rem 0.5rem',
                  borderRadius: '9999px',
                  fontWeight: 700
                }}>
                  {accountMode === 'custom' ? '👤 Mode Pengguna Mandiri' : (studentData.is_good ? '🟢 Benchmark Unggul' : '🔴 Perlu Penguatan')}
                </span>
              </h3>
              <div className="candidate-meta">
                <span className="meta-pill">
                  <GraduationCap size={14} /> Peminatan: <strong>{studentData.track}</strong>
                </span>
                <span className="meta-pill">
                  <BookOpen size={14} /> IPK: <strong>{studentData.ipk}</strong>
                </span>
                <span className="meta-pill">
                  <Award size={14} /> Portofolio: <strong>{studentData.num_certs} Sertifikat Industri</strong>
                </span>
                {studentData.ab_test_summary && (
                  <span className="meta-pill" style={{ background: '#EFF6FF', color: '#1E40AF', borderColor: '#BFDBFE' }}>
                    <TrendingUp size={14} /> Lonjakan Portofolio: <strong>+{studentData.ab_test_summary.max_delta} Skor</strong>
                  </span>
                )}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center' }}>
            {accountMode === 'custom' ? (
              <button 
                className="btn-primary"
                onClick={() => setShowUploadModal(true)}
                style={{ background: '#10B981', border: 'none', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
              >
                <Edit3 size={16} /> Edit KHS & Sertifikat
              </button>
            ) : (
              <button 
                className="btn-primary"
                onClick={() => {
                  setAccountMode('custom');
                  setShowUploadModal(true);
                }}
                style={{ background: '#059669', border: 'none' }}
              >
                <Upload size={16} /> Input Profil Mandiri
              </button>
            )}
            <button 
              className="btn-outline"
              onClick={() => setShowProfileModal(true)}
            >
              <FileText size={16} /> KHS & Sertifikat
            </button>
            <button 
              className="btn-primary"
              onClick={() => setShowDreamModal(true)}
            >
              <Compass size={16} /> Profesi Impian
            </button>
          </div>
        </div>
      )}

      {/* Primary Section Switcher: Rekomendasi Profil vs Eksplor Semua Lowongan */}
      <div style={{
        display: 'flex',
        gap: '0.75rem',
        marginBottom: '1rem',
        borderBottom: '2px solid #E2E8F0',
        paddingBottom: '0.5rem'
      }}>
        <button
          onClick={() => setActiveTab('recommend')}
          style={{
            padding: '0.65rem 1.25rem',
            borderRadius: '12px',
            border: 'none',
            fontSize: '0.95rem',
            fontWeight: 800,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            background: activeTab === 'recommend' ? '#2563EB' : '#F1F5F9',
            color: activeTab === 'recommend' ? '#FFFFFF' : '#475569',
            boxShadow: activeTab === 'recommend' ? '0 4px 12px rgba(37,99,235,0.25)' : 'none',
            transition: 'all 0.2s'
          }}
        >
          <Sparkles size={18} />
          🎯 Rekomendasi Karir Terpilih ({filteredRecommendedJobs.length} Top Jobs)
        </button>

        <button
          onClick={() => setActiveTab('explore_all')}
          style={{
            padding: '0.65rem 1.25rem',
            borderRadius: '12px',
            border: 'none',
            fontSize: '0.95rem',
            fontWeight: 800,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            background: activeTab === 'explore_all' ? '#059669' : '#F1F5F9',
            color: activeTab === 'explore_all' ? '#FFFFFF' : '#475569',
            boxShadow: activeTab === 'explore_all' ? '0 4px 12px rgba(5,150,105,0.25)' : 'none',
            transition: 'all 0.2s'
          }}
        >
          <Briefcase size={18} />
          🌐 Eksplor Seluruh Katalog ({catalogTotal || 4570}+ Lowongan)
        </button>
      </div>

      {/* Mode A/B Evaluasi Switcher (Hanya Muncul saat di Tab Rekomendasi) */}
      {activeTab === 'recommend' && (
        <div style={{
          background: '#FFFFFF',
          borderRadius: '16px',
          padding: '0.75rem 1.25rem',
          marginBottom: '1rem',
          border: '1px solid #E2E8F0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '0.75rem',
          boxShadow: '0 2px 8px rgba(0,0,0,0.02)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 800, color: '#334155', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Mode Evaluasi A/B:
            </span>
            <span style={{ fontSize: '0.82rem', color: '#64748B' }}>
              {evaluationMode === 'after' && '🚀 Kondisi B: Rekomendasi Terintegrasi (KHS + 5 Sertifikat Industri)'}
              {evaluationMode === 'before' && '🎓 Kondisi A: Rekomendasi Murni Akademik (Hanya KHS Saja)'}
              {evaluationMode === 'compare' && '⚖️ Komparasi A/B: Perbandingan Lonjakan Skor Sebelum vs Sesudah Sertifikasi'}
            </span>
          </div>

          <div style={{ display: 'flex', background: '#F1F5F9', padding: '3px', borderRadius: '12px', gap: '4px' }}>
            <button
              onClick={() => {
                setEvaluationMode('after');
                const list = studentData?.recommended_jobs_after || studentData?.recommended_jobs || [];
                if (list.length > 0) setActiveJob(list[0]);
              }}
              style={{
                padding: '0.4rem 0.9rem',
                borderRadius: '9px',
                border: 'none',
                fontSize: '0.82rem',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                transition: 'all 0.2s',
                background: evaluationMode === 'after' ? '#2563EB' : 'transparent',
                color: evaluationMode === 'after' ? '#FFFFFF' : '#64748B',
                boxShadow: evaluationMode === 'after' ? '0 2px 6px rgba(37,99,235,0.3)' : 'none'
              }}
            >
              <Sparkles size={14} /> After (+ Sertifikat)
            </button>

            <button
              onClick={() => {
                setEvaluationMode('before');
                const list = studentData?.recommended_jobs_before || studentData?.recommended_jobs || [];
                if (list.length > 0) setActiveJob(list[0]);
              }}
              style={{
                padding: '0.4rem 0.9rem',
                borderRadius: '9px',
                border: 'none',
                fontSize: '0.82rem',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                transition: 'all 0.2s',
                background: evaluationMode === 'before' ? '#475569' : 'transparent',
                color: evaluationMode === 'before' ? '#FFFFFF' : '#64748B',
                boxShadow: evaluationMode === 'before' ? '0 2px 6px rgba(71,85,105,0.3)' : 'none'
              }}
            >
              <BookOpen size={14} /> Before (KHS Saja)
            </button>

            <button
              onClick={() => {
                setEvaluationMode('compare');
                const list = studentData?.recommended_jobs_after || studentData?.recommended_jobs || [];
                if (list.length > 0) setActiveJob(list[0]);
              }}
              style={{
                padding: '0.4rem 0.9rem',
                borderRadius: '9px',
                border: 'none',
                fontSize: '0.82rem',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                transition: 'all 0.2s',
                background: evaluationMode === 'compare' ? '#059669' : 'transparent',
                color: evaluationMode === 'compare' ? '#FFFFFF' : '#64748B',
                boxShadow: evaluationMode === 'compare' ? '0 2px 6px rgba(5,150,105,0.3)' : 'none'
              }}
            >
              <TrendingUp size={14} /> Komparasi A/B
            </button>
          </div>
        </div>
      )}

      {/* Search & Category Filter Section */}
      <section className="search-filter-section">
        <div className="search-input-wrapper">
          <Search size={20} className="search-icon" />
          <input 
            type="text"
            className="search-input"
            placeholder={activeTab === 'recommend' ? "Cari dalam daftar rekomendasi terpilih..." : "Cari di seluruh database 4.570 lowongan (misal: 'Frontend', 'Data Scientist', 'Network')..."}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="category-chips">
          {CATEGORIES.map(cat => (
            <button
              key={cat.id}
              className={`chip-btn ${selectedCategory === cat.id ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat.id)}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </section>

      {/* Main Split Job Board with Interactive Drag Resizing */}
      <main 
        className="main-job-board"
        style={{
          gridTemplateColumns: isListCollapsed 
            ? '64px 14px 1fr' 
            : `${panelWidth}px 14px 1fr`
        }}
      >
        {/* Left: Job Feed */}
        <div className="job-list-panel" style={{ display: isListCollapsed ? 'none' : 'flex' }}>
          {/* Header & Controls Bar */}
          <div className="board-controls-bar">
            <div className="board-control-group">
              <span style={{ fontSize: '0.76rem', fontWeight: 700, color: '#64748B' }}>
                Lebar Panel:
              </span>
              <button 
                className={`control-pill-btn ${panelWidth === 340 ? 'active' : ''}`}
                onClick={() => setPanelWidth(340)}
                title="Mode Fokus Detail (List 340px)"
              >
                Fokus (340px)
              </button>
              <button 
                className={`control-pill-btn ${panelWidth === 460 ? 'active' : ''}`}
                onClick={() => setPanelWidth(460)}
                title="Mode Standar (460px)"
              >
                Standar (460px)
              </button>
              <button 
                className={`control-pill-btn ${panelWidth === 600 ? 'active' : ''}`}
                onClick={() => setPanelWidth(600)}
                title="Mode List Lebar (600px)"
              >
                Lebar (600px)
              </button>
            </div>

            <div className="board-control-group">
              <span style={{ fontSize: '0.76rem', fontWeight: 700, color: '#64748B' }}>
                Tampilan:
              </span>
              <button 
                className={`control-pill-btn ${cardDensity === 'comfortable' ? 'active' : ''}`}
                onClick={() => setCardDensity('comfortable')}
                title="Tampilan Lengkap (Komprehensif)"
              >
                📑 Detail
              </button>
              <button 
                className={`control-pill-btn ${cardDensity === 'compact' ? 'active' : ''}`}
                onClick={() => setCardDensity('compact')}
                title="Tampilan Ringkas (Bisa lihat banyak lowongan sekaligus)"
              >
                📋 Ringkas
              </button>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem', padding: '0 0.25rem' }}>
            <span style={{ fontSize: '0.84rem', fontWeight: 700, color: '#475569' }}>
              {activeTab === 'recommend' 
                ? `🎯 ${displayedJobs.length} Rekomendasi Teratas Khusus ${studentData?.name || 'Mahasiswa'}`
                : `🌐 ${displayedJobs.length} dari ${catalogTotal} Katalog Lowongan`
              }
            </span>
            {isCatalogLoading && (
              <span style={{ fontSize: '0.75rem', color: '#2563EB', fontWeight: 700 }}>
                Memuat lowongan...
              </span>
            )}
          </div>

          {displayedJobs.length > 0 ? (
            displayedJobs.map((job) => (
              <JobCard 
                key={job.job_id}
                job={job}
                isSelected={activeJob?.job_id === job.job_id}
                onSelect={() => setActiveJob(job)}
                isSaved={savedJobs.includes(job.job_id)}
                onToggleSave={handleToggleSave}
                density={cardDensity}
              />
            ))
          ) : (
            <div style={{ background: '#FFFFFF', padding: '2rem', borderRadius: '16px', textAlign: 'center', color: '#94A3B8', border: '1px solid #E2E8F0' }}>
              {isCatalogLoading ? 'Memuat katalog lowongan...' : 'Tidak ada lowongan yang cocok dengan filter pencarian.'}
            </div>
          )}
        </div>

        {/* Draggable Resize Divider */}
        <div 
          className={`resize-divider ${isDragging ? 'dragging' : ''}`}
          onMouseDown={handleMouseDown}
          title="Geser ke kiri/kanan untuk memperbesar atau memperkecil lebar panel rekomendasi"
        >
          <div className="resize-handle-pill" />
        </div>

        {/* Right: Interactive Job & XAI Detail Hub */}
        <JobDetailDrawer 
          job={activeJob}
          isSaved={activeJob && savedJobs.includes(activeJob.job_id)}
          onToggleSave={handleToggleSave}
          hasApplied={activeJob && appliedJobs.includes(activeJob.job_id)}
          onApply={handleApply}
          evaluationMode={evaluationMode}
        />
      </main>

      {/* Modals */}
      {showUploadModal && (
        <UploadModal 
          onClose={() => setShowUploadModal(false)}
          onProfileAnalyzed={handleProfileAnalyzed}
        />
      )}

      {showProfileModal && (
        <StudentProfileModal 
          student={studentData}
          onClose={() => setShowProfileModal(false)}
        />
      )}

      {showDreamModal && (
        <DreamJobExplorer 
          student={studentData}
          onClose={() => setShowDreamModal(false)}
        />
      )}

      {showAuthModal && (
        <AuthModal 
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          onAuthSuccess={handleAuthSuccess}
        />
      )}
    </div>
  );
}
