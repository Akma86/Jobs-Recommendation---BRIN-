import React, { useState, useEffect } from 'react';
import { 
  X, 
  Compass, 
  Search, 
  Sparkles, 
  BookOpen, 
  Building2, 
  TrendingUp, 
  Award,
  CheckCircle2,
  ArrowRight
} from 'lucide-react';

export default function DreamJobExplorer({ student, onClose }) {
  const [searchTerm, setSearchTerm] = useState('Machine Learning Engineer');
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDreamJob, setSelectedDreamJob] = useState(null);
  const [diceCandidates, setDiceCandidates] = useState([]);
  const [isDiceLoading, setIsDiceLoading] = useState(false);

  // Search jobs on mount and on search term submit
  const handleSearch = async () => {
    if (!searchTerm.trim()) return;
    setIsLoading(true);
    try {
      const res = await fetch(`/api/jobs?query=${encodeURIComponent(searchTerm)}&limit=12`);
      const json = await res.json();
      if (json.status === 'success') {
        setSearchResults(json.data);
        if (json.data.length > 0 && !selectedDreamJob) {
          handleSelectJob(json.data[0]);
        }
      }
    } catch (err) {
      console.error('Error fetching jobs:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    handleSearch();
  }, []);

  const handleSelectJob = async (job) => {
    setSelectedDreamJob(job);
    setIsDiceLoading(true);
    try {
      const res = await fetch(`/api/dice/candidates?job_id=${encodeURIComponent(job.job_id)}&job_title=${encodeURIComponent(job.title)}&top_n=6`);
      const json = await res.json();
      if (json.status === 'success') {
        setDiceCandidates(json.courses || []);
      }
    } catch (err) {
      console.error('Error fetching DiCE candidates:', err);
    } finally {
      setIsDiceLoading(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" style={{ maxWidth: '950px' }} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #E2E8F0', paddingBottom: '1.25rem', marginBottom: '1.25rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Compass size={22} color="#2563EB" />
              <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0F172A' }}>
                Target Dream Career Roadmap
              </h2>
            </div>
            <p style={{ color: '#64748B', fontSize: '0.88rem', marginTop: '0.25rem' }}>
              Pilih profesi impian Anda dari 4.570 lowongan pekerjaan untuk memetakan jalur belajar dan sertifikasi interaktif.
            </p>
          </div>

          <button 
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: '#94A3B8', padding: '4px' }}
          >
            <X size={22} />
          </button>
        </div>

        {/* Search Bar */}
        <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: '#94A3B8' }} />
            <input 
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Cari profesi impian (misal: AI Engineer, SAP Consultant, DevOps)..."
              style={{
                width: '100%',
                padding: '0.75rem 1rem 0.75rem 2.75rem',
                borderRadius: '12px',
                border: '1px solid #CBD5E1',
                fontSize: '0.92rem',
                outline: 'none'
              }}
            />
          </div>
          <button 
            className="btn-primary"
            onClick={handleSearch}
            disabled={isLoading}
          >
            {isLoading ? "Mencari..." : "Cari"}
          </button>
        </div>

        {/* Split Explorer Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: '1.25rem', alignItems: 'start' }}>
          {/* Left: Job Results List */}
          <div style={{ maxHeight: '480px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.6rem', paddingRight: '0.35rem' }}>
            {searchResults.map((job, idx) => {
              const isSelected = selectedDreamJob?.job_id === job.job_id;
              return (
                <div 
                  key={idx}
                  onClick={() => handleSelectJob(job)}
                  style={{
                    padding: '0.85rem 1rem',
                    borderRadius: '12px',
                    border: isSelected ? '1.5px solid #2563EB' : '1px solid #E2E8F0',
                    background: isSelected ? '#EFF6FF' : '#FFFFFF',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <div style={{ fontWeight: 700, fontSize: '0.92rem', color: '#0F172A', lineHeight: 1.3 }}>
                    {job.title}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#64748B', marginTop: '0.2rem' }}>
                    {job.company}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Right: DiCE Roadmap for Selected Dream Job */}
          <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '16px', padding: '1.25rem', maxHeight: '480px', overflowY: 'auto' }}>
            {selectedDreamJob ? (
              <div>
                <div style={{ marginBottom: '1rem', borderBottom: '1px solid #E2E8F0', paddingBottom: '0.75rem' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#2563EB', textTransform: 'uppercase' }}>
                    Target Karir Terpilih
                  </div>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0F172A', marginTop: '0.15rem' }}>
                    {selectedDreamJob.title}
                  </h3>
                  <div style={{ fontSize: '0.85rem', color: '#64748B' }}>
                    {selectedDreamJob.company}
                  </div>
                </div>

                <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#1E293B', marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <Sparkles size={16} color="#2563EB" />
                  Rekomendasi Kursus & Sertifikasi DiCE (1.139 Katalog Online):
                </h4>

                {isDiceLoading ? (
                  <p style={{ color: '#64748B', fontSize: '0.86rem' }}>Menganalisis katalog kursus...</p>
                ) : diceCandidates.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                    {diceCandidates.map((c, cIdx) => (
                      <div 
                        key={cIdx}
                        style={{
                          background: '#FFFFFF',
                          border: '1px solid #E2E8F0',
                          borderRadius: '12px',
                          padding: '0.85rem 1rem'
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <div>
                            <div style={{ fontWeight: 700, fontSize: '0.9rem', color: '#0F172A' }}>
                              {c.course_name}
                            </div>
                            <div style={{ fontSize: '0.78rem', color: '#64748B', marginTop: '0.15rem' }}>
                              Platform: <strong>{c.platform}</strong> • Level: <strong>{c.level}</strong>
                            </div>
                          </div>
                          <span style={{ background: '#ECFDF5', color: '#065F46', padding: '0.2rem 0.5rem', borderRadius: '6px', fontSize: '0.76rem', fontWeight: 700 }}>
                            +{c.score_delta.toFixed(2)} Boost
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ color: '#94A3B8', fontSize: '0.88rem' }}>Katalog kursus tidak ditemukan.</p>
                )}
              </div>
            ) : (
              <p style={{ color: '#94A3B8', fontSize: '0.88rem', textAlign: 'center', marginTop: '3rem' }}>
                Pilih salah satu lowongan di sebelah kiri untuk melihat jalur belajarnya.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
