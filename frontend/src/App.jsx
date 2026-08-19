import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import JobCard from './components/JobCard';
import JobDetailDrawer from './components/JobDetailDrawer';
import StudentProfileModal from './components/StudentProfileModal';
import DreamJobExplorer from './components/DreamJobExplorer';
import UploadModal from './components/UploadModal';
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
  Upload
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
  const [selectedStudentId, setSelectedStudentId] = useState('budi-santoso-web-bagus');
  const [studentData, setStudentData] = useState(null);
  const [activeJob, setActiveJob] = useState(null);
  const [activeTab, setActiveTab] = useState('explore');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
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
          if (json.data.recommended_jobs && json.data.recommended_jobs.length > 0) {
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

  // Filter Jobs
  const filteredJobs = (studentData?.recommended_jobs || []).filter(job => {
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

  return (
    <div className="app-container">
      {/* Navbar */}
      <Navbar 
        students={students}
        selectedStudentId={selectedStudentId}
        onSelectStudent={setSelectedStudentId}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
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
            <div className="stat-value">2.102</div>
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
        <div className="candidate-bar">
          <div className="candidate-left">
            <div className="candidate-avatar">
              {studentData.name.charAt(0)}
            </div>
            <div className="candidate-info">
              <h3>
                {studentData.name}
                <span style={{
                  fontSize: '0.72rem',
                  background: studentData.is_good ? '#ECFDF5' : '#FEF2F2',
                  color: studentData.is_good ? '#065F46' : '#991B1B',
                  border: `1px solid ${studentData.is_good ? '#A7F3D0' : '#FECACA'}`,
                  padding: '0.15rem 0.5rem',
                  borderRadius: '9999px',
                  fontWeight: 700
                }}>
                  {studentData.is_good ? '🟢 Akademik Unggul' : '🔴 Perlu Penguatan'}
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
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.6rem' }}>
            <button 
              className="btn-primary"
              onClick={() => setShowUploadModal(true)}
              style={{ background: '#059669', border: 'none' }}
            >
              <Upload size={16} /> Input / Ganti Profil Saya
            </button>
            <button 
              className="btn-outline"
              onClick={() => setShowProfileModal(true)}
            >
              <FileText size={16} /> Lihat KHS & Sertifikat
            </button>
            <button 
              className="btn-primary"
              onClick={() => setShowDreamModal(true)}
            >
              <Compass size={16} /> Eksplor Profesi Impian
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
            placeholder="Cari lowongan pekerjaan atau nama perusahaan..."
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

      {/* Main Split Job Board */}
      <main className="main-job-board">
        {/* Left: Job Feed */}
        <div className="job-list-panel">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem', padding: '0 0.25rem' }}>
            <span style={{ fontSize: '0.86rem', fontWeight: 700, color: '#475569' }}>
              Menampilkan {filteredJobs.length} Rekomendasi Karir Teratas
            </span>
          </div>

          {filteredJobs.length > 0 ? (
            filteredJobs.map((job) => (
              <JobCard 
                key={job.job_id}
                job={job}
                isSelected={activeJob?.job_id === job.job_id}
                onSelect={() => setActiveJob(job)}
                isSaved={savedJobs.includes(job.job_id)}
                onToggleSave={handleToggleSave}
              />
            ))
          ) : (
            <div style={{ background: '#FFFFFF', padding: '2rem', borderRadius: '16px', textAlign: 'center', color: '#94A3B8', border: '1px solid #E2E8F0' }}>
              Tidak ada lowongan yang cocok dengan filter pencarian.
            </div>
          )}
        </div>

        {/* Right: Interactive Job & XAI Detail Hub */}
        <JobDetailDrawer 
          job={activeJob}
          isSaved={activeJob && savedJobs.includes(activeJob.job_id)}
          onToggleSave={handleToggleSave}
          hasApplied={activeJob && appliedJobs.includes(activeJob.job_id)}
          onApply={handleApply}
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
    </div>
  );
}
