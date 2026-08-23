import React, { useState } from 'react';
import { 
  X, 
  GraduationCap, 
  Award, 
  BookOpen, 
  CheckCircle2, 
  FileText,
  Calendar,
  Clock
} from 'lucide-react';

export default function StudentProfileModal({ student, onClose }) {
  const [profileTab, setProfileTab] = useState('khs');

  if (!student) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #E2E8F0', paddingBottom: '1.25rem', marginBottom: '1.25rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#0F172A' }}>
                {student.name}
              </h2>
              <span style={{ 
                background: student.is_good ? '#ECFDF5' : '#FEF2F2',
                color: student.is_good ? '#065F46' : '#991B1B',
                border: `1px solid ${student.is_good ? '#A7F3D0' : '#FECACA'}`,
                padding: '0.2rem 0.6rem',
                borderRadius: '9999px',
                fontSize: '0.75rem',
                fontWeight: 700
              }}>
                {student.is_good ? '🟢 Akademik Unggul' : '🔴 Perlu Penguatan'}
              </span>
            </div>
            <p style={{ color: '#64748B', fontSize: '0.88rem', marginTop: '0.25rem' }}>
              S1 Sistem Informasi — Peminatan <strong>{student.track}</strong> • IPK: <strong>{student.ipk}</strong> • Total SKS: <strong>{student.total_sks}</strong>
            </p>
          </div>

          <button 
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: '#94A3B8', padding: '4px' }}
          >
            <X size={22} />
          </button>
        </div>

        {/* Profile Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid #E2E8F0', marginBottom: '1.25rem', paddingBottom: '0.5rem', flexWrap: 'wrap' }}>
          <button 
            className={`xai-tab-btn ${profileTab === 'khs' ? 'active' : ''}`}
            onClick={() => setProfileTab('khs')}
          >
            <BookOpen size={16} />
            📚 Kartu Hasil Studi ({student.courses?.length || 0} MK)
          </button>

          <button 
            className={`xai-tab-btn ${profileTab === 'certs' ? 'active' : ''}`}
            onClick={() => setProfileTab('certs')}
          >
            <Award size={16} />
            📜 Portofolio Sertifikasi ({student.certificates?.length || 0})
          </button>

          <button 
            className={`xai-tab-btn ${profileTab === 'abtest' ? 'active' : ''}`}
            onClick={() => setProfileTab('abtest')}
          >
            <CheckCircle2 size={16} />
            ⚖️ Evaluasi A/B (+Sertifikat)
          </button>
        </div>

        {/* TAB 1: KHS */}
        {profileTab === 'khs' && (
          <div>
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>No</th>
                    <th>Kode MK</th>
                    <th>Nama Mata Kuliah</th>
                    <th>SKS</th>
                    <th>Semester</th>
                    <th>Nilai</th>
                  </tr>
                </thead>
                <tbody>
                  {student.courses?.map((c, idx) => (
                    <tr key={idx}>
                      <td style={{ color: '#64748B' }}>{c.no}</td>
                      <td style={{ fontFamily: 'monospace', color: '#475569', fontWeight: 600 }}>{c.kode_mk}</td>
                      <td style={{ fontWeight: 700, color: '#1E293B' }}>{c.nama_mk}</td>
                      <td style={{ color: '#475569' }}>{c.sks}</td>
                      <td style={{ color: '#64748B' }}>{c.semester}</td>
                      <td>
                        <span style={{ 
                          fontWeight: 800, 
                          color: (c.grade === 'A' || c.grade === 'AB') ? '#059669' : (c.grade === 'B' || c.grade === 'BC' ? '#2563EB' : '#DC2626'),
                          background: (c.grade === 'A' || c.grade === 'AB') ? '#ECFDF5' : (c.grade === 'B' || c.grade === 'BC' ? '#EFF6FF' : '#FEF2F2'),
                          padding: '0.15rem 0.5rem',
                          borderRadius: '6px'
                        }}>
                          {c.grade}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 2: Certificates */}
        {profileTab === 'certs' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {student.certificates?.map((cert, idx) => (
              <div key={idx} style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '1.1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.4rem' }}>
                  <div>
                    <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#0F172A' }}>
                      {cert.title}
                    </h4>
                    <div style={{ fontSize: '0.84rem', color: '#64748B', marginTop: '0.15rem' }}>
                      Penerbit: <strong>{cert.issuer}</strong> • ID: <span style={{ fontFamily: 'monospace' }}>{cert.cred_id}</span>
                    </div>
                  </div>
                  <span style={{ background: '#EFF6FF', color: '#1E40AF', padding: '0.25rem 0.6rem', borderRadius: '6px', fontSize: '0.76rem', fontWeight: 700 }}>
                    {cert.tier_label}
                  </span>
                </div>

                <div style={{ display: 'flex', gap: '1.25rem', fontSize: '0.8rem', color: '#475569', margin: '0.5rem 0' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Calendar size={13} /> Terbit: {cert.issue_date}
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Clock size={13} /> Durasi: {cert.duration}
                  </span>
                  <span>Skor: <strong>{cert.score}</strong></span>
                </div>

                {cert.topics && cert.topics.length > 0 && (
                  <div style={{ marginTop: '0.5rem', background: '#FFFFFF', padding: '0.75rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                      Cakupan Materi & Kompetensi:
                    </div>
                    <ul style={{ paddingLeft: '1.2rem', fontSize: '0.82rem', color: '#334155', lineHeight: 1.4 }}>
                      {cert.topics.map((t, tIdx) => (
                        <li key={tIdx}>{t}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
        {/* TAB 3: A/B Testing Evaluation */}
        {profileTab === 'abtest' && (
          <div>
            <p style={{ fontSize: '0.86rem', color: '#64748B', marginBottom: '1rem' }}>
              Perbandingan hasil rekomendasi karir sebelum vs sesudah penambahan <strong>{student.num_certs} sertifikat industri</strong>:
            </p>

            <div style={{ overflowX: 'auto', marginBottom: '1.25rem' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Kondisi A (KHS Saja)</th>
                    <th>Skor A</th>
                    <th>Kondisi B (+ 5 Sertifikat)</th>
                    <th>Skor B</th>
                    <th>Delta Boost</th>
                  </tr>
                </thead>
                <tbody>
                  {(student.recommended_jobs_after || student.recommended_jobs || []).slice(0, 5).map((jobA, idx) => {
                    const jobB = (student.recommended_jobs_before || [])[idx] || {};
                    return (
                      <tr key={idx}>
                        <td style={{ fontWeight: 700, color: '#64748B' }}>#{idx + 1}</td>
                        <td style={{ color: '#334155' }}>{jobB.title || '-'}</td>
                        <td style={{ fontWeight: 600, color: '#475569' }}>{jobB.score_before || '-'}</td>
                        <td style={{ fontWeight: 800, color: '#1E40AF' }}>{jobA.title}</td>
                        <td style={{ fontWeight: 800, color: '#1E40AF' }}>{jobA.score_after}</td>
                        <td>
                          <span style={{
                            padding: '0.2rem 0.55rem',
                            borderRadius: '6px',
                            fontWeight: 800,
                            fontSize: '0.78rem',
                            background: jobA.delta > 0.3 ? '#ECFDF5' : '#F1F5F9',
                            color: jobA.delta > 0.3 ? '#065F46' : '#64748B'
                          }}>
                            {jobA.delta > 0 ? `+${jobA.delta.toFixed(2)}` : '0.00'}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <div style={{ background: '#EFF6FF', border: '1px solid #BFDBFE', borderRadius: '12px', padding: '1rem' }}>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#1E40AF', marginBottom: '0.25rem' }}>
                📌 Ringkasan Hasil Eksperimen:
              </div>
              <p style={{ fontSize: '0.82rem', color: '#1E3A8A', margin: 0, lineHeight: 1.5 }}>
                Integrasi sertifikasi industri kredibel (Tier A/B) terbukti secara empiris meningkatkan skor kelayakan pada posisi linear dan mempertajam spesifikasi karir target lulusan secara signifikan.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
