import React, { useState } from 'react';
import confetti from 'canvas-confetti';
import { 
  Building2, 
  MapPin, 
  Sparkles, 
  TrendingUp, 
  Bookmark, 
  Send, 
  CheckCircle2, 
  MessageSquare, 
  BarChart3, 
  Compass, 
  PlayCircle,
  Award,
  BookOpen,
  DollarSign,
  Briefcase
} from 'lucide-react';

const AVATAR_COLORS = [
  'linear-gradient(135deg, #3B82F6, #1D4ED8)',
  'linear-gradient(135deg, #10B981, #047857)',
  'linear-gradient(135deg, #8B5CF6, #6D28D9)',
  'linear-gradient(135deg, #F59E0B, #D97706)',
  'linear-gradient(135deg, #EC4899, #BE185D)',
  'linear-gradient(135deg, #06B6D4, #0E7490)',
];

export default function JobDetailDrawer({ 
  job, 
  isSaved, 
  onToggleSave,
  hasApplied,
  onApply
}) {
  const [activeTab, setActiveTab] = useState('narrative');
  const [selectedCourses, setSelectedCourses] = useState([]);
  const [projectedBoost, setProjectedBoost] = useState(0);

  if (!job) {
    return (
      <div className="job-detail-panel" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px', color: '#94A3B8' }}>
        <p>Pilih salah satu lowongan di sebelah kiri untuk melihat analisis XAI mendalam.</p>
      </div>
    );
  }

  const charCode = job.company ? job.company.charCodeAt(0) : 65;
  const avatarBg = AVATAR_COLORS[charCode % AVATAR_COLORS.length];
  const initial = job.company ? job.company.charAt(0).toUpperCase() : 'J';

  const handleApplyClick = () => {
    confetti({
      particleCount: 80,
      spread: 60,
      origin: { y: 0.6 }
    });
    onApply(job.job_id);
  };

  const handleToggleCourse = (course) => {
    const exists = selectedCourses.some(c => c.course_name === course.course_name);
    let newSelection = [];
    if (exists) {
      newSelection = selectedCourses.filter(c => c.course_name !== course.course_name);
    } else {
      newSelection = [...selectedCourses, course];
    }
    setSelectedCourses(newSelection);

    // Calculate boost
    const boost = newSelection.reduce((acc, c) => acc + (c.score_delta || 0.5), 0);
    const decayed = boost / (1.0 + 0.15 * Math.max(0, newSelection.length - 1));
    setProjectedBoost(decayed);
  };

  const simulatedScore = Math.min(10.0, Number((job.score_after + projectedBoost).toFixed(2)));
  const simulatedPct = Math.min(100.0, Number(((simulatedScore / 10.0) * 100).toFixed(1)));

  return (
    <div className="job-detail-panel">
      {/* Header */}
      <div className="detail-header">
        <div className="detail-title-box">
          <div className="detail-logo" style={{ background: avatarBg }}>
            {initial}
          </div>
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0F172A', lineHeight: 1.2 }}>
              {job.title}
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.35rem', color: '#64748B', fontSize: '0.9rem' }}>
              <span style={{ fontWeight: 600, color: '#1E293B' }}>{job.company}</span>
              <span>•</span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                <MapPin size={14} /> {job.location || 'Indonesia / Remote'}
              </span>
            </div>
          </div>
        </div>

        <div className="detail-actions">
          <button 
            className="btn-outline"
            onClick={() => onToggleSave(job.job_id)}
          >
            <Bookmark size={16} fill={isSaved ? "#2563EB" : "none"} color={isSaved ? "#2563EB" : "currentColor"} />
            {isSaved ? "Tersimpan" : "Simpan"}
          </button>

          <button 
            className="btn-primary"
            onClick={handleApplyClick}
            disabled={hasApplied}
            style={hasApplied ? { background: '#10B981', cursor: 'default' } : {}}
          >
            {hasApplied ? (
              <>
                <CheckCircle2 size={16} /> Dilamar
              </>
            ) : (
              <>
                <Send size={16} /> Quick Apply
              </>
            )}
          </button>
        </div>
      </div>

      {/* Jobright-style AI Match Overview & Why You Match Hero */}
      <div className="match-overview-card" style={{
        background: 'linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%)',
        border: '1px solid #BFDBFE',
        borderRadius: '16px',
        padding: '1.25rem',
        marginBottom: '1.25rem'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid #E2E8F0', paddingBottom: '0.9rem', marginBottom: '0.9rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
            <div style={{
              width: '56px',
              height: '56px',
              borderRadius: '16px',
              background: (job.match_pct || 75) >= 85 ? 'linear-gradient(135deg, #10B981, #059669)' : 'linear-gradient(135deg, #2563EB, #1D4ED8)',
              color: '#FFFFFF',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 800,
              boxShadow: '0 4px 12px rgba(37,99,235,0.25)'
            }}>
              <span style={{ fontSize: '1.15rem', lineHeight: 1 }}>{projectedBoost > 0 ? simulatedPct : job.match_pct}%</span>
              <span style={{ fontSize: '0.55rem', opacity: 0.9, textTransform: 'uppercase', letterSpacing: '0.04em' }}>MATCH</span>
            </div>

            <div>
              <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#0F172A', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Sparkles size={16} color="#2563EB" />
                Alasan Anda Cocok (Why You Match)
              </div>
              <div style={{ fontSize: '0.82rem', color: '#64748B', marginTop: '0.15rem' }}>
                Indeks Kelayakan: <strong>{job.score_after}</strong> {projectedBoost > 0 && <span style={{ color: '#059669', fontWeight: 700 }}>(Simulasi: {simulatedScore})</span>} • Peringkat Rekomendasi: <strong>#{job.rank}</strong>
              </div>
            </div>
          </div>

          <div style={{ textAlign: 'right' }}>
            {job.delta > 0.1 && (
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', background: '#DCFCE7', color: '#166534', padding: '0.35rem 0.75rem', borderRadius: '8px', fontWeight: 700, fontSize: '0.82rem', border: '1px solid #BBF7D0' }}>
                <TrendingUp size={14} />
                +{job.delta.toFixed(2)} Lonjakan Sertifikat
              </div>
            )}
            <div style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '0.35rem' }}>
              Skor Before (KHS Saja): <strong>{job.score_before}</strong>
            </div>
          </div>
        </div>

        {/* Quick Bullet Highlights on Why You Match */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem', fontSize: '0.84rem', color: '#334155' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
            <CheckCircle2 size={15} color="#059669" style={{ flexShrink: 0 }} />
            <span>
              <strong>Kecocokan Profil Keseluruhan:</strong> Memenuhi <strong>{job.match_pct}%</strong> kualifikasi kompetensi untuk posisi <strong>{job.title}</strong>.
            </span>
          </div>

          {job.delta > 0.1 ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <TrendingUp size={15} color="#2563EB" style={{ flexShrink: 0 }} />
              <span>
                <strong>Dukungan Sertifikasi:</strong> Portofolio kredensial industri mendongkrak kelayakan Anda sebesar <strong>+{job.delta.toFixed(2)} poin</strong> ({job.impact_status}).
              </span>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <BookOpen size={15} color="#2563EB" style={{ flexShrink: 0 }} />
              <span>
                <strong>Fondasi Kurikulum:</strong> Capaian nilai KHS pada mata kuliah inti memberikan kecocokan akademik yang kuat.
              </span>
            </div>
          )}
        </div>
      </div>

      {/* XAI Navigation Tabs */}
      <div className="xai-tabs-nav">
        <button 
          className={`xai-tab-btn ${activeTab === 'narrative' ? 'active' : ''}`}
          onClick={() => setActiveTab('narrative')}
        >
          <MessageSquare size={15} />
          💬 Smart Explanation
        </button>

        <button 
          className={`xai-tab-btn ${activeTab === 'abtest' ? 'active' : ''}`}
          onClick={() => setActiveTab('abtest')}
        >
          <TrendingUp size={15} />
          ⚖️ Dampak A/B (+Sertifikat)
        </button>

        <button 
          className={`xai-tab-btn ${activeTab === 'shap' ? 'active' : ''}`}
          onClick={() => setActiveTab('shap')}
        >
          <BarChart3 size={15} />
          📊 SHAP Attribution
        </button>

        <button 
          className={`xai-tab-btn ${activeTab === 'dice' ? 'active' : ''}`}
          onClick={() => setActiveTab('dice')}
        >
          <Compass size={15} />
          🧭 DiCE Roadmap ({job.dice_recommendations?.length || 0})
        </button>

        <button 
          className={`xai-tab-btn ${activeTab === 'whatif' ? 'active' : ''}`}
          onClick={() => setActiveTab('whatif')}
        >
          <PlayCircle size={15} />
          🎯 What-If Simulator
        </button>
      </div>

      {/* TAB 1: Smart Narrative Explanation */}
      {activeTab === 'narrative' && (
        <div>
          <div className="narrative-card">
            <p className="narrative-text">
              {job.narrative?.narrative_text || "Profil Anda memiliki keselarasan tinggi dengan lowongan pekerjaan ini berdasarkan integrasi mata kuliah dan sertifikasi industri."}
            </p>
          </div>

          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#1E293B', marginBottom: '0.75rem' }}>
            📌 Rincian Persentase Kecocokan per Komponen:
          </h4>

          {job.narrative?.components && job.narrative.components.length > 0 ? (
            job.narrative.components.map((comp, cIdx) => (
              <div key={cIdx} className="component-item">
                <div>
                  <div className="component-type">
                    {comp.type === 'Sertifikat Industri' ? '📜 Sertifikasi Industri' : '📚 Mata Kuliah Kurikulum'}
                  </div>
                  <div className="component-name">{comp.name}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span className="component-match-pill">
                    Kecocokan {comp.relevance_match_pct}%
                  </span>
                  <div style={{ fontSize: '0.72rem', color: '#64748B', marginTop: '0.2rem' }}>
                    Menyumbang {comp.contribution_share_pct}% skor
                  </div>
                </div>
              </div>
            ))
          ) : (
            <p style={{ color: '#94A3B8', fontSize: '0.88rem' }}>Data komponen tidak tersedia.</p>
          )}
        </div>
      )}

      {/* TAB: A/B Test Impact */}
      {activeTab === 'abtest' && (
        <div>
          <p style={{ fontSize: '0.86rem', color: '#64748B', marginBottom: '1rem' }}>
            Analisis perbandingan komparatif A/B Testing untuk mengukur seberapa signifikan sertifikasi industri meningkatkan daya saing profil Anda terhadap lowongan <strong>{job.title}</strong>:
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1.25rem' }}>
            {/* Condition A */}
            <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '1rem' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase' }}>
                🎓 Kondisi A (Before)
              </div>
              <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#334155', marginTop: '0.25rem' }}>
                {job.score_before} <span style={{ fontSize: '0.8rem', fontWeight: 500 }}>/ 45.0</span>
              </div>
              <div style={{ fontSize: '0.8rem', color: '#64748B', marginTop: '0.25rem' }}>
                Murni Capaian KHS Kurikulum
              </div>
            </div>

            {/* Condition B */}
            <div style={{ background: '#EFF6FF', border: '1px solid #BFDBFE', borderRadius: '12px', padding: '1rem' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#1E40AF', textTransform: 'uppercase' }}>
                🚀 Kondisi B (After)
              </div>
              <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#1E40AF', marginTop: '0.25rem' }}>
                {job.score_after} <span style={{ fontSize: '0.8rem', fontWeight: 500 }}>/ 45.0</span>
              </div>
              <div style={{ fontSize: '0.8rem', color: '#1E40AF', marginTop: '0.25rem', fontWeight: 600 }}>
                +{job.delta.toFixed(2)} Lonjakan Sertifikat
              </div>
            </div>
          </div>

          <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '1rem' }}>
            <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#0F172A', marginBottom: '0.5rem' }}>
              💡 Kesimpulan Dampak Portofolio:
            </h4>
            <p style={{ fontSize: '0.85rem', color: '#475569', lineHeight: 1.5 }}>
              {job.delta > 1.0 ? (
                <>Sertifikasi industri memberikan <strong>lonjakan masif (+{job.delta.toFixed(2)} poin)</strong> pada posisi ini. Kepemilikan sertifikat kredibel (Tier A/B) berhasil memvalidasi keterampilan praktis tingkat lanjut yang melengkapi capaian teori akademik di kelas.</>
              ) : job.delta > 0.1 ? (
                <>Penambahan sertifikasi industri memberikan <strong>penguatan terarah (+{job.delta.toFixed(2)} poin)</strong>, meningkatkan kepastian kompetensi pada bidang keahlian target.</>
              ) : (
                <>Skor pada posisi ini didominasi oleh fondasi kurikulum akademik yang sudah sangat kuat (skor stabil).</>
              )}
            </p>
          </div>
        </div>
      )}

      {/* TAB 2: SHAP Feature Attribution */}
      {activeTab === 'shap' && (
        <div>
          <p style={{ fontSize: '0.86rem', color: '#64748B', marginBottom: '1rem' }}>
            SHAP (SHapley Additive exPlanations) mengukur kontribusi kuantitatif masing-masing fitur (mata kuliah kurikulum vs sertifikasi) dalam menaikkan skor kelayakan Anda.
          </p>

          {job.shap_features && job.shap_features.length > 0 ? (
            job.shap_features.map((feat, fIdx) => {
              const val = feat.value;
              const isPos = val >= 0;
              const absPct = Math.min(100, Math.round(Math.abs(val) * 35));
              return (
                <div key={fIdx} className="shap-row">
                  <div className="shap-label-box">
                    <span style={{ color: '#1E293B' }}>{feat.feature}</span>
                    <span style={{ color: isPos ? '#059669' : '#DC2626', fontWeight: 700 }}>
                      {isPos ? `+${val.toFixed(3)}` : val.toFixed(3)}
                    </span>
                  </div>
                  <div className="shap-bar-bg">
                    <div 
                      className={isPos ? "shap-bar-fill-pos" : "shap-bar-fill-neg"} 
                      style={{ 
                        width: `${absPct}%`,
                        background: isPos ? 'linear-gradient(90deg, #10B981, #059669)' : 'linear-gradient(90deg, #EF4444, #DC2626)'
                      }}
                    />
                  </div>
                </div>
              );
            })
          ) : (
            <p style={{ color: '#94A3B8', fontSize: '0.88rem' }}>Data atribusi SHAP tidak tersedia.</p>
          )}
        </div>
      )}

      {/* TAB 3: DiCE Roadmap */}
      {activeTab === 'dice' && (
        <div>
          <p style={{ fontSize: '0.86rem', color: '#64748B', marginBottom: '1rem' }}>
            DiCE (Diverse Counterfactual Explanations) merekomendasikan kursus riil dari 1.139 katalog online (Google, AWS, Meta, IBM, DeepLearning.AI) untuk menutup celah kompetensi Anda:
          </p>

          {job.dice_recommendations && job.dice_recommendations.length > 0 ? (
            job.dice_recommendations.map((dice, dIdx) => (
              <div key={dIdx} className="dice-course-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.35rem' }}>
                  <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#0F172A' }}>
                    {dice.course_name}
                  </div>
                  <span style={{ background: '#EFF6FF', color: '#1E40AF', padding: '0.2rem 0.5rem', borderRadius: '6px', fontSize: '0.76rem', fontWeight: 700 }}>
                    +{dice.score_delta.toFixed(2)} Est. Boost
                  </span>
                </div>
                <p style={{ fontSize: '0.84rem', color: '#475569', lineHeight: 1.4 }}>
                  {dice.detail}
                </p>
              </div>
            ))
          ) : (
            <p style={{ color: '#94A3B8', fontSize: '0.88rem' }}>Tidak ada rekomendasi intervensi tambahan untuk lowongan ini.</p>
          )}
        </div>
      )}

      {/* TAB 4: What-If Simulator */}
      {activeTab === 'whatif' && (
        <div>
          <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '1rem', marginBottom: '1rem' }}>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#1E293B', marginBottom: '0.25rem' }}>
              🎯 Simulasi Interaktif Perubahan Profil
            </h4>
            <p style={{ fontSize: '0.84rem', color: '#64748B' }}>
              Centang kursus di bawah ini untuk melihat simulasi seketika berapa lonjakan skor kelayakan Anda jika Anda menyelesaikan sertifikasi tersebut:
            </p>
          </div>

          {job.dice_recommendations && job.dice_recommendations.length > 0 ? (
            job.dice_recommendations.map((dice, dIdx) => {
              const isChecked = selectedCourses.some(c => c.course_name === dice.course_name);
              return (
                <div 
                  key={dIdx}
                  onClick={() => handleToggleCourse(dice)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.85rem',
                    padding: '0.85rem 1rem',
                    borderRadius: '12px',
                    border: isChecked ? '1.5px solid #2563EB' : '1px solid #E2E8F0',
                    background: isChecked ? '#EFF6FF' : '#FFFFFF',
                    marginBottom: '0.6rem',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <input 
                    type="checkbox"
                    checked={isChecked}
                    onChange={() => {}} // Handled by div onClick
                    style={{ width: '18px', height: '18px', cursor: 'pointer', accentColor: '#2563EB' }}
                  />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 700, fontSize: '0.9rem', color: '#1E293B' }}>
                      {dice.course_name}
                    </div>
                    <div style={{ fontSize: '0.78rem', color: '#64748B' }}>
                      Potensi tambahan skor: <strong>+{dice.score_delta.toFixed(2)} poin</strong>
                    </div>
                  </div>
                </div>
              );
            })
          ) : (
            <p style={{ color: '#94A3B8', fontSize: '0.88rem' }}>Pilih lowongan lain untuk mencoba simulator.</p>
          )}

          {selectedCourses.length > 0 && (
            <div style={{ background: '#ECFDF5', border: '1px solid #A7F3D0', borderRadius: '12px', padding: '1rem', marginTop: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 700, color: '#065F46', fontSize: '0.95rem' }}>
                  🚀 Proyeksi Lonjakan Skor: +{projectedBoost.toFixed(2)} Poin
                </div>
                <div style={{ fontSize: '0.8rem', color: '#047857' }}>
                  Skor baru: <strong>{simulatedScore} / 10.0 ({simulatedPct}% Match)</strong>
                </div>
              </div>
              <button 
                className="btn-primary" 
                style={{ background: '#059669', fontSize: '0.82rem', padding: '0.4rem 0.8rem' }}
                onClick={() => alert(`Target rencana belajar disimpan! Mengambil ${selectedCourses.length} kursus akan menaikkan skor Anda ke ${simulatedScore}.`)}
              >
                Simpan Target Belajar
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
