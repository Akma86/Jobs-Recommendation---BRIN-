import React, { useState, useEffect } from 'react';
import { 
  X, 
  Upload, 
  FileText, 
  Award, 
  Sparkles, 
  Plus, 
  Trash2, 
  CheckCircle2, 
  BookOpen, 
  User, 
  Briefcase,
  AlertCircle,
  HelpCircle,
  Zap
} from 'lucide-react';

const TRACK_OPTIONS = [
  { id: 'Machine Learning', label: '🤖 Machine Learning & AI' },
  { id: 'Web Development', label: '💻 Web & Fullstack Development' },
  { id: 'Networking & Cloud', label: '☁️ Cloud, DevOps & Network Security' },
  { id: 'SAP & Enterprise Systems', label: '🏢 SAP & Enterprise Systems' },
];

const ISSUER_OPTIONS = [
  'Google / Google Cloud',
  'AWS (Amazon Web Services)',
  'Meta (Facebook)',
  'Cisco Networking Academy',
  'DeepLearning.AI',
  'SAP Official',
  'IBM',
  'Microsoft Learn',
  'Coursera / Stanford Online',
  'Oracle'
];

export default function UploadModal({ onClose, onProfileAnalyzed }) {
  const [modalTab, setModalTab] = useState('upload'); // 'upload' | 'manual' | 'sample'
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Form states
  const [studentName, setStudentName] = useState('');
  const [selectedTrack, setSelectedTrack] = useState('Machine Learning');
  const [targetCareer, setTargetCareer] = useState('');
  
  // File upload states
  const [khsFile, setKhsFile] = useState(null);
  const [certFiles, setCertFiles] = useState([]);

  // Manual courses state
  const [courses, setCourses] = useState([]);
  
  // Manual certs state
  const [manualCerts, setManualCerts] = useState([
    {
      title: 'Google Data Analytics Professional',
      issuer: 'Google / Google Cloud',
      issue_date: '2024-06-15',
      duration: '180 jam',
      score: '92/100',
      topics: 'SQL, Tableau, R Programming, Data Cleaning'
    }
  ]);

  // Load presets on mount
  useEffect(() => {
    fetch('/api/presets')
      .then(res => res.json())
      .then(json => {
        if (json.status === 'success') {
          setCourses(json.standard_courses || []);
        }
      })
      .catch(err => console.error('Error loading presets:', err));
  }, []);

  // Preset grade changers
  const handleSetAllGrades = (grade) => {
    setCourses(courses.map(c => ({ ...c, grade })));
  };

  const handleCourseGradeChange = (index, grade) => {
    const next = [...courses];
    next[index].grade = grade;
    setCourses(next);
  };

  // Add & remove manual certs
  const handleAddCert = () => {
    setManualCerts([
      ...manualCerts,
      {
        title: '',
        issuer: 'Google / Google Cloud',
        issue_date: '2024',
        duration: '40 jam',
        score: '85/100',
        topics: ''
      }
    ]);
  };

  const handleRemoveCert = (index) => {
    setManualCerts(manualCerts.filter((_, i) => i !== index));
  };

  const handleCertChange = (index, field, value) => {
    const next = [...manualCerts];
    next[index][field] = value;
    setManualCerts(next);
  };

  // Submit File Upload
  const handleFileUploadSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage('');

    try {
      const formData = new FormData();
      formData.append('name', studentName || 'Mahasiswa Pengguna');
      formData.append('track', selectedTrack);
      if (targetCareer) formData.append('target_career', targetCareer);
      if (khsFile) formData.append('khs_file', khsFile);
      
      certFiles.forEach((file) => {
        formData.append('cert_files', file);
      });

      const res = await fetch('/api/upload/files', {
        method: 'POST',
        body: formData
      });

      const json = await res.json();
      if (json.status === 'success') {
        onProfileAnalyzed(json.data);
        onClose();
      } else {
        setErrorMessage(json.detail || 'Terjadi kesalahan saat menganalisis berkas.');
      }
    } catch (err) {
      console.error(err);
      setErrorMessage('Gagal menghubungi backend server: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Submit Manual Form
  const handleManualSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage('');

    try {
      const payload = {
        name: studentName || 'Mahasiswa Pengguna',
        track: selectedTrack,
        target_career: targetCareer,
        courses: courses,
        certificates: manualCerts.filter(c => c.title.trim() !== '')
      };

      const res = await fetch('/api/analyze/custom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const json = await res.json();
      if (json.status === 'success') {
        onProfileAnalyzed(json.data);
        onClose();
      } else {
        setErrorMessage(json.detail || 'Terjadi kesalahan saat memproses analisis.');
      }
    } catch (err) {
      console.error(err);
      setErrorMessage('Gagal menghubungi backend server: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // 1-Click Sample Loader
  const handleLoadSample = (sampleId) => {
    setIsLoading(true);
    fetch(`/api/student/${sampleId}`)
      .then(res => res.json())
      .then(json => {
        if (json.status === 'success') {
          onProfileAnalyzed(json.data);
          onClose();
        }
      })
      .catch(err => console.error(err))
      .finally(() => setIsLoading(false));
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" style={{ maxWidth: '900px' }} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #E2E8F0', paddingBottom: '1.25rem', marginBottom: '1.25rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <div style={{ background: '#EFF6FF', color: '#2563EB', padding: '0.4rem', borderRadius: '10px' }}>
                <Upload size={22} />
              </div>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0F172A' }}>
                Input & Analisis Portofolio Anda
              </h2>
            </div>
            <p style={{ color: '#64748B', fontSize: '0.88rem', marginTop: '0.35rem' }}>
              Unggah file transkrip KHS & sertifikat industri Anda atau gunakan formulir cepat untuk mendapatkan rekomendasi karir AI.
            </p>
          </div>

          <button 
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: '#94A3B8', padding: '4px' }}
          >
            <X size={22} />
          </button>
        </div>

        {/* Error Alert */}
        {errorMessage && (
          <div style={{ background: '#FEF2F2', border: '1px solid #FECACA', color: '#991B1B', padding: '0.75rem 1rem', borderRadius: '10px', fontSize: '0.88rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertCircle size={18} />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Modal Navigation Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid #E2E8F0', marginBottom: '1.25rem', paddingBottom: '0.5rem' }}>
          <button 
            className={`xai-tab-btn ${modalTab === 'upload' ? 'active' : ''}`}
            onClick={() => setModalTab('upload')}
          >
            <Upload size={16} />
            📁 Upload Berkas (PDF / Markdown / CSV)
          </button>

          <button 
            className={`xai-tab-btn ${modalTab === 'manual' ? 'active' : ''}`}
            onClick={() => setModalTab('manual')}
          >
            <FileText size={16} />
            ✍️ Input Form & Nilai KHS Manual
          </button>

          <button 
            className={`xai-tab-btn ${modalTab === 'sample' ? 'active' : ''}`}
            onClick={() => setModalTab('sample')}
          >
            <Zap size={16} />
            🚀 1-Click Load Contoh Nyata
          </button>
        </div>

        {/* TAB 1: Upload Files */}
        {modalTab === 'upload' && (
          <form onSubmit={handleFileUploadSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.84rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '0.35rem' }}>
                  Nama Lengkap Mahasiswa
                </label>
                <input 
                  type="text"
                  placeholder="Contoh: Akmal Yaasir Fauzaan"
                  value={studentName}
                  onChange={(e) => setStudentName(e.target.value)}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', borderRadius: '10px', border: '1px solid #CBD5E1', fontSize: '0.9rem', outline: 'none' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.84rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '0.35rem' }}>
                  Peminatan / Minat Bidang
                </label>
                <select 
                  value={selectedTrack}
                  onChange={(e) => setSelectedTrack(e.target.value)}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', borderRadius: '10px', border: '1px solid #CBD5E1', fontSize: '0.9rem', outline: 'none', background: 'white' }}
                >
                  {TRACK_OPTIONS.map(tr => (
                    <option key={tr.id} value={tr.id}>{tr.label}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Target Career (Optional) */}
            <div style={{ marginBottom: '1.25rem' }}>
              <label style={{ fontSize: '0.84rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '0.35rem' }}>
                Target Profesi / Karir Impian (Opsional)
              </label>
              <input 
                type="text"
                placeholder="Contoh: AI / Machine Learning Engineer, Frontend Developer, DevOps..."
                value={targetCareer}
                onChange={(e) => setTargetCareer(e.target.value)}
                style={{ width: '100%', padding: '0.65rem 0.85rem', borderRadius: '10px', border: '1px solid #CBD5E1', fontSize: '0.9rem', outline: 'none' }}
              />
            </div>

            {/* Dropzone 1: KHS */}
            <div style={{ marginBottom: '1.25rem' }}>
              <label style={{ fontSize: '0.84rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '0.35rem' }}>
                📄 Unggah Berkas KHS (Transkrip Nilai Akademik)
              </label>
              <div style={{
                border: '2px dashed #93C5FD',
                borderRadius: '12px',
                padding: '1.25rem',
                textAlign: 'center',
                background: '#F8FAFC',
                cursor: 'pointer'
              }}>
                <input 
                  type="file"
                  id="khs-upload"
                  accept=".md,.pdf,.csv,.txt"
                  onChange={(e) => setKhsFile(e.target.files[0])}
                  style={{ display: 'none' }}
                />
                <label htmlFor="khs-upload" style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.35rem' }}>
                  <FileText size={28} color="#2563EB" />
                  <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#1E293B' }}>
                    {khsFile ? `Terpilih: ${khsFile.name}` : 'Klik untuk memilih file KHS (.pdf, .md, .csv)'}
                  </span>
                  <span style={{ fontSize: '0.76rem', color: '#64748B' }}>
                    Mendukung transkrip kurikulum OBE Telkom University format Markdown, PDF, atau CSV
                  </span>
                </label>
              </div>
            </div>

            {/* Dropzone 2: Certificates */}
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ fontSize: '0.84rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '0.35rem' }}>
                📜 Unggah Sertifikasi Industri (Bisa Pilih Lebih dari 1 Berkas)
              </label>
              <div style={{
                border: '2px dashed #A7F3D0',
                borderRadius: '12px',
                padding: '1.25rem',
                textAlign: 'center',
                background: '#F8FAFC',
                cursor: 'pointer'
              }}>
                <input 
                  type="file"
                  id="cert-upload"
                  multiple
                  accept=".md,.pdf,.jpg,.jpeg,.png"
                  onChange={(e) => setCertFiles(Array.from(e.target.files))}
                  style={{ display: 'none' }}
                />
                <label htmlFor="cert-upload" style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.35rem' }}>
                  <Award size={28} color="#059669" />
                  <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#1E293B' }}>
                    {certFiles.length > 0 ? `Terpilih ${certFiles.length} file sertifikat` : 'Klik untuk memilih sertifikat (Google, AWS, Meta, Cisco, dll)'}
                  </span>
                  <span style={{ fontSize: '0.76rem', color: '#64748B' }}>
                    Format didukung: PDF, Markdown, JPG, PNG
                  </span>
                </label>
              </div>

              {certFiles.length > 0 && (
                <div style={{ marginTop: '0.6rem', display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                  {certFiles.map((f, fIdx) => (
                    <span key={fIdx} style={{ background: '#ECFDF5', color: '#065F46', border: '1px solid #A7F3D0', padding: '0.2rem 0.55rem', borderRadius: '6px', fontSize: '0.78rem', fontWeight: 600 }}>
                      ✓ {f.name}
                    </span>
                  ))}
                </div>
              )}
            </div>

            <button 
              type="submit" 
              className="btn-primary" 
              disabled={isLoading}
              style={{ width: '100%', padding: '0.85rem', justifyContent: 'center', fontSize: '1rem' }}
            >
              {isLoading ? '⚡ Sedang Menganalisis Profil...' : '⚡ Jalankan Analisis AI & Temukan Karir'}
            </button>
          </form>
        )}

        {/* TAB 2: Manual Form Entry */}
        {modalTab === 'manual' && (
          <form onSubmit={handleManualSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.84rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '0.35rem' }}>
                  Nama Lengkap Mahasiswa
                </label>
                <input 
                  type="text"
                  placeholder="Contoh: Akmal Yaasir Fauzaan"
                  value={studentName}
                  onChange={(e) => setStudentName(e.target.value)}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', borderRadius: '10px', border: '1px solid #CBD5E1', fontSize: '0.9rem', outline: 'none' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.84rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '0.35rem' }}>
                  Peminatan / Track
                </label>
                <select 
                  value={selectedTrack}
                  onChange={(e) => setSelectedTrack(e.target.value)}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', borderRadius: '10px', border: '1px solid #CBD5E1', fontSize: '0.9rem', outline: 'none', background: 'white' }}
                >
                  {TRACK_OPTIONS.map(tr => (
                    <option key={tr.id} value={tr.id}>{tr.label}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Courses Grade Editor */}
            <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '1rem', marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#1E293B' }}>
                  📚 Nilai Mata Kuliah Kurikulum OBE ({courses.length} MK)
                </h4>
                <div style={{ display: 'flex', gap: '0.35rem' }}>
                  <button 
                    type="button" 
                    onClick={() => handleSetAllGrades('A')}
                    style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem', background: '#ECFDF5', color: '#065F46', border: '1px solid #A7F3D0', borderRadius: '6px', cursor: 'pointer', fontWeight: 700 }}
                  >
                    Set Semua A
                  </button>
                  <button 
                    type="button" 
                    onClick={() => handleSetAllGrades('AB')}
                    style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem', background: '#EFF6FF', color: '#1E40AF', border: '1px solid #BFDBFE', borderRadius: '6px', cursor: 'pointer', fontWeight: 700 }}
                  >
                    Set Semua AB
                  </button>
                </div>
              </div>

              <div style={{ maxHeight: '180px', overflowY: 'auto', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                {courses.map((c, idx) => (
                  <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#FFFFFF', padding: '0.35rem 0.65rem', borderRadius: '8px', border: '1px solid #E2E8F0', fontSize: '0.82rem' }}>
                    <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '240px', color: '#334155', fontWeight: 600 }}>
                      {c.nama_mk}
                    </span>
                    <select 
                      value={c.grade}
                      onChange={(e) => handleCourseGradeChange(idx, e.target.value)}
                      style={{ padding: '0.15rem 0.35rem', borderRadius: '4px', border: '1px solid #CBD5E1', fontWeight: 700, fontSize: '0.8rem', background: 'white' }}
                    >
                      <option value="A">A</option>
                      <option value="AB">AB</option>
                      <option value="B">B</option>
                      <option value="BC">BC</option>
                      <option value="C">C</option>
                      <option value="D">D</option>
                      <option value="E">E</option>
                    </select>
                  </div>
                ))}
              </div>
            </div>

            {/* Certificates Editor */}
            <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '1rem', marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#1E293B' }}>
                  📜 Portofolio Sertifikasi Industri ({manualCerts.length})
                </h4>
                <button 
                  type="button" 
                  onClick={handleAddCert}
                  className="btn-outline"
                  style={{ fontSize: '0.78rem', padding: '0.3rem 0.65rem', borderRadius: '8px' }}
                >
                  <Plus size={14} /> Tambah Sertifikat
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '200px', overflowY: 'auto' }}>
                {manualCerts.map((cert, cIdx) => (
                  <div key={cIdx} style={{ background: '#FFFFFF', border: '1px solid #CBD5E1', borderRadius: '10px', padding: '0.75rem' }}>
                    <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.4rem' }}>
                      <input 
                        type="text"
                        placeholder="Judul Sertifikat (misal: AWS Solutions Architect, Meta React Developer)"
                        value={cert.title}
                        onChange={(e) => handleCertChange(cIdx, 'title', e.target.value)}
                        style={{ flex: 1, padding: '0.45rem 0.65rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem' }}
                      />
                      <select 
                        value={cert.issuer}
                        onChange={(e) => handleCertChange(cIdx, 'issuer', e.target.value)}
                        style={{ padding: '0.45rem 0.65rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: 'white' }}
                      >
                        {ISSUER_OPTIONS.map((iss, iIdx) => (
                          <option key={iIdx} value={iss}>{iss}</option>
                        ))}
                      </select>
                      <button 
                        type="button" 
                        onClick={() => handleRemoveCert(cIdx)}
                        style={{ background: '#FEE2E2', border: 'none', color: '#DC2626', padding: '0.45rem 0.65rem', borderRadius: '6px', cursor: 'pointer' }}
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>

                    <input 
                      type="text"
                      placeholder="Cakupan topik teknis (dipisahkan koma, misal: Deep Learning, CNN, PyTorch, Model Deployment)"
                      value={cert.topics}
                      onChange={(e) => handleCertChange(cIdx, 'topics', e.target.value)}
                      style={{ width: '100%', padding: '0.35rem 0.65rem', borderRadius: '6px', border: '1px solid #E2E8F0', fontSize: '0.8rem' }}
                    />
                  </div>
                ))}
              </div>
            </div>

            <button 
              type="submit" 
              className="btn-primary" 
              disabled={isLoading}
              style={{ width: '100%', padding: '0.85rem', justifyContent: 'center', fontSize: '1rem' }}
            >
              {isLoading ? '⚡ Sedang Menganalisis...' : '⚡ Jalankan Rekomendasi Karir & XAI'}
            </button>
          </form>
        )}

        {/* TAB 3: Sample 1-Click Profiles */}
        {modalTab === 'sample' && (
          <div>
            <p style={{ fontSize: '0.88rem', color: '#64748B', marginBottom: '1rem' }}>
              Pilih salah satu profil mahasiswa siap uji di bawah ini untuk mensimulasikan hasil analisis KHS & sertifikat secara instan:
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.85rem' }}>
              <div 
                onClick={() => handleLoadSample('siti-rahma-ml-bagus')}
                style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '1rem', cursor: 'pointer', transition: 'all 0.15s ease' }}
              >
                <div style={{ fontWeight: 700, color: '#0F172A', fontSize: '0.95rem' }}>
                  🤖 Siti Rahma — AI/ML Engineer
                </div>
                <div style={{ fontSize: '0.8rem', color: '#059669', fontWeight: 600, marginTop: '0.2rem' }}>
                  IPK 3.72 • 5 Sertifikasi (TensorFlow, NLP, Google Data, GenAI)
                </div>
              </div>

              <div 
                onClick={() => handleLoadSample('budi-santoso-web-bagus')}
                style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '1rem', cursor: 'pointer', transition: 'all 0.15s ease' }}
              >
                <div style={{ fontWeight: 700, color: '#0F172A', fontSize: '0.95rem' }}>
                  💻 Budi Santoso — Frontend Developer
                </div>
                <div style={{ fontSize: '0.8rem', color: '#059669', fontWeight: 600, marginTop: '0.2rem' }}>
                  IPK 3.75 • 4 Sertifikasi (AWS Dev, Meta Frontend, Docker)
                </div>
              </div>

              <div 
                onClick={() => handleLoadSample('andi-wijaya-net-bagus')}
                style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '1rem', cursor: 'pointer', transition: 'all 0.15s ease' }}
              >
                <div style={{ fontWeight: 700, color: '#0F172A', fontSize: '0.95rem' }}>
                  ☁️ Andi Wijaya — Cloud & Security
                </div>
                <div style={{ fontSize: '0.8rem', color: '#059669', fontWeight: 600, marginTop: '0.2rem' }}>
                  IPK 3.66 • 4 Sertifikasi (CCNA, AWS Cloud, CyberOps, Security+)
                </div>
              </div>

              <div 
                onClick={() => handleLoadSample('dewi-lestari-sap-bagus')}
                style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '1rem', cursor: 'pointer', transition: 'all 0.15s ease' }}
              >
                <div style={{ fontWeight: 700, color: '#0F172A', fontSize: '0.95rem' }}>
                  🏢 Dewi Lestari — SAP & Enterprise Systems
                </div>
                <div style={{ fontSize: '0.8rem', color: '#059669', fontWeight: 600, marginTop: '0.2rem' }}>
                  IPK 3.82 • 4 Sertifikasi (SAP S/4HANA, SAP Analytics Cloud, ERP)
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
