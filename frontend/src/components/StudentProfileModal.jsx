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
        <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid #E2E8F0', marginBottom: '1.25rem', paddingBottom: '0.5rem' }}>
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
        </div>

        {/* TAB 1: KHS */}
        {profileTab === 'khs' && (
          <div>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.86rem', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: '#F1F5F9', borderBottom: '1px solid #CBD5E1', color: '#334155' }}>
                    <th style={{ padding: '0.6rem 0.8rem' }}>No</th>
                    <th style={{ padding: '0.6rem 0.8rem' }}>Kode MK</th>
                    <th style={{ padding: '0.6rem 0.8rem' }}>Nama Mata Kuliah</th>
                    <th style={{ padding: '0.6rem 0.8rem' }}>SKS</th>
                    <th style={{ padding: '0.6rem 0.8rem' }}>Semester</th>
                    <th style={{ padding: '0.6rem 0.8rem' }}>Nilai</th>
                  </tr>
                </thead>
                <tbody>
                  {student.courses?.map((c, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid #E2E8F0', background: idx % 2 === 0 ? '#FFFFFF' : '#F8FAFC' }}>
                      <td style={{ padding: '0.55rem 0.8rem', color: '#64748B' }}>{c.no}</td>
                      <td style={{ padding: '0.55rem 0.8rem', fontFamily: 'monospace', color: '#475569' }}>{c.kode_mk}</td>
                      <td style={{ padding: '0.55rem 0.8rem', fontWeight: 600, color: '#1E293B' }}>{c.nama_mk}</td>
                      <td style={{ padding: '0.55rem 0.8rem', color: '#475569' }}>{c.sks}</td>
                      <td style={{ padding: '0.55rem 0.8rem', color: '#64748B' }}>{c.semester}</td>
                      <td style={{ padding: '0.55rem 0.8rem' }}>
                        <span style={{ 
                          fontWeight: 800, 
                          color: (c.grade === 'A' || c.grade === 'AB') ? '#059669' : (c.grade === 'B' || c.grade === 'BC' ? '#2563EB' : '#DC2626')
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
      </div>
    </div>
  );
}
