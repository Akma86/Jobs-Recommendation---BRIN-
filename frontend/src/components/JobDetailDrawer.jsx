import React, { useState } from 'react';
import confetti from 'canvas-confetti';
import FormattedText from './FormattedText';
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
  Award, 
  BookOpen, 
  Info,
  Layers,
  ArrowUpRight
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

  const beforePct = job.match_pct_before || Math.max(15.0, Number((job.match_pct - (job.delta > 0.1 ? job.delta * 4.5 : 0)).toFixed(1)));
  const deltaPct = job.delta_pct || Math.max(0.0, Number((job.match_pct - beforePct).toFixed(1)));

  // Separate components for Smart Explanation
  const allComponents = job.narrative?.components || [];
  const certComponents = allComponents.filter(c => c.type === 'Sertifikat Industri' || c.name.toLowerCase().includes('certificate') || c.name.toLowerCase().includes('associate') || c.name.toLowerCase().includes('specialization'));
  const courseComponents = allComponents.filter(c => c.type === 'Mata Kuliah Kurikulum' || !certComponents.includes(c));

  return (
    <div className="job-detail-panel">
      {/* Header */}
      <div className="detail-header">
        <div className="detail-title-box">
          <div className="detail-logo" style={{ background: avatarBg }}>
            {initial}
          </div>
          <div>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#0F172A', lineHeight: 1.2 }}>
              {job.title}
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.35rem', color: '#64748B', fontSize: '0.88rem' }}>
              <span style={{ fontWeight: 700, color: '#1E293B' }}>{job.company}</span>
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

      {/* Jobright-style AI Match Overview Hero */}
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
              <span style={{ fontSize: '1.15rem', lineHeight: 1 }}>{job.match_pct}%</span>
              <span style={{ fontSize: '0.55rem', opacity: 0.9, textTransform: 'uppercase', letterSpacing: '0.04em' }}>MATCH</span>
            </div>

            <div>
              <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#0F172A', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Sparkles size={16} color="#2563EB" />
                Alasan Keselarasan Profil (Why You Match)
              </div>
              <div style={{ fontSize: '0.82rem', color: '#64748B', marginTop: '0.15rem' }}>
                Indeks Kelayakan: <strong>{job.score_after} / 10.0</strong> • Peringkat Rekomendasi: <strong>#{job.rank}</strong>
              </div>
            </div>
          </div>

          <div style={{ textAlign: 'right' }}>
            {job.delta > 0.1 && (
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', background: '#DCFCE7', color: '#166534', padding: '0.35rem 0.75rem', borderRadius: '8px', fontWeight: 700, fontSize: '0.82rem', border: '1px solid #BBF7D0' }}>
                <TrendingUp size={14} />
                +{deltaPct}% Lonjakan Sertifikat
              </div>
            )}
            <div style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '0.35rem' }}>
              Before (KHS Saja): <strong>{beforePct}% ({job.score_before})</strong>
            </div>
          </div>
        </div>

        {/* Quick Highlights */}
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
                <strong>Dukungan Sertifikasi Industri:</strong> Portofolio kredensial mendongkrak kelayakan Anda sebesar <strong>+{deltaPct}% (+{job.delta.toFixed(2)} poin)</strong> ({job.impact_status}).
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

      {/* XAI Navigation Tabs (Clean 4 Tabs) */}
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
          ⚖️ Before & After Certificate
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
      </div>

      {/* TAB 1: Smart Narrative Explanation */}
      {activeTab === 'narrative' && (
        <div>
          {/* Main Synthesis Narrative */}
          <div className="narrative-card" style={{ marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#1E40AF', fontWeight: 800, fontSize: '0.86rem', marginBottom: '0.4rem' }}>
              <Sparkles size={16} />
              Rangkuman Analisis Explainable AI (XAI):
            </div>
            <p className="narrative-text" style={{ fontSize: '0.92rem', lineHeight: 1.6, color: '#334155' }}>
              <FormattedText 
                text={job.narrative?.narrative_text || "Profil Anda memiliki keselarasan tinggi dengan lowongan pekerjaan ini berdasarkan integrasi mata kuliah kurikulum dan sertifikasi industri."} 
              />
            </p>
          </div>

          {/* Section A: Matching Industry Certificates */}
          {certComponents.length > 0 && (
            <div style={{ marginBottom: '1.25rem' }}>
              <h4 style={{ fontSize: '0.92rem', fontWeight: 800, color: '#1E293B', marginBottom: '0.65rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Award size={16} color="#2563EB" />
                📜 Sertifikasi Industri yang Relevan & Mendongkrak Skor:
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
                {certComponents.map((comp, cIdx) => (
                  <div key={cIdx} className="component-item" style={{ borderLeft: '3px solid #2563EB' }}>
                    <div>
                      <div className="component-type" style={{ color: '#2563EB' }}>Sertifikat Industri Resmi</div>
                      <div className="component-name">
                        <FormattedText text={comp.name} />
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <span className="component-match-pill" style={{ background: '#EFF6FF', color: '#1E40AF', border: '1px solid #BFDBFE' }}>
                        Kecocokan {comp.relevance_match_pct}%
                      </span>
                      <div style={{ fontSize: '0.72rem', color: '#64748B', marginTop: '0.2rem' }}>
                        Menyumbang {comp.contribution_share_pct}% kelayakan
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section B: Helpful Curriculum Courses */}
          {courseComponents.length > 0 && (
            <div style={{ marginBottom: '1rem' }}>
              <h4 style={{ fontSize: '0.92rem', fontWeight: 800, color: '#1E293B', marginBottom: '0.65rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <BookOpen size={16} color="#059669" />
                📚 Mata Kuliah Kurikulum KHS yang Mendukung:
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
                {courseComponents.map((comp, cIdx) => (
                  <div key={cIdx} className="component-item" style={{ borderLeft: '3px solid #10B981' }}>
                    <div>
                      <div className="component-type" style={{ color: '#059669' }}>Capaian Kurikulum (CLO)</div>
                      <div className="component-name">
                        <FormattedText text={comp.name} />
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <span className="component-match-pill">
                        Kecocokan {comp.relevance_match_pct}%
                      </span>
                      <div style={{ fontSize: '0.72rem', color: '#64748B', marginTop: '0.2rem' }}>
                        Menyumbang {comp.contribution_share_pct}% kelayakan
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: Before & After Certificate Impact */}
      {activeTab === 'abtest' && (
        <div>
          <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '0.85rem 1rem', marginBottom: '1.25rem', fontSize: '0.85rem', color: '#475569' }}>
            <strong style={{ color: '#0F172A' }}>⚖️ Evaluasi Komparatif Before vs After:</strong> Mengukur peningkatan daya saing dan keselarasan profil Anda terhadap lowongan <strong>{job.title}</strong> sebelum dan sesudah memperhitungkan portofolio sertifikasi industri.
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
            {/* Condition A: Before */}
            <div style={{ background: '#F8FAFC', border: '1px solid #CBD5E1', borderRadius: '14px', padding: '1.25rem' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.03em' }}>
                🎓 Kondisi A (Before Sertifikat)
              </div>
              <div style={{ fontSize: '1.75rem', fontWeight: 900, color: '#334155', marginTop: '0.35rem', fontFamily: 'var(--font-heading)' }}>
                {beforePct}% <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#64748B' }}>Match</span>
              </div>
              <div style={{ fontSize: '0.82rem', color: '#475569', marginTop: '0.35rem', fontWeight: 600 }}>
                Indeks Skor: {job.score_before} / 10.0
              </div>
              <div style={{ fontSize: '0.78rem', color: '#64748B', marginTop: '0.25rem', borderTop: '1px solid #E2E8F0', paddingTop: '0.5rem' }}>
                Murni Capaian Transkrip KHS Kurikulum
              </div>
            </div>

            {/* Condition B: After */}
            <div style={{ background: '#EFF6FF', border: '1.5px solid #93C5FD', borderRadius: '14px', padding: '1.25rem' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#1E40AF', textTransform: 'uppercase', letterSpacing: '0.03em' }}>
                🚀 Kondisi B (After + 5 Sertifikat)
              </div>
              <div style={{ fontSize: '1.75rem', fontWeight: 900, color: '#1E40AF', marginTop: '0.35rem', fontFamily: 'var(--font-heading)' }}>
                {job.match_pct}% <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#2563EB' }}>Match</span>
              </div>
              <div style={{ fontSize: '0.82rem', color: '#1E40AF', marginTop: '0.35rem', fontWeight: 700 }}>
                Indeks Skor: {job.score_after} / 10.0
              </div>
              <div style={{ fontSize: '0.78rem', color: '#1E40AF', marginTop: '0.25rem', borderTop: '1px solid #BFDBFE', paddingTop: '0.5rem', fontWeight: 700 }}>
                +{deltaPct}% Lonjakan (+{job.delta.toFixed(2)} Poin Portofolio)
              </div>
            </div>
          </div>

          <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '14px', padding: '1.15rem' }}>
            <h4 style={{ fontSize: '0.9rem', fontWeight: 800, color: '#0F172A', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <Info size={16} color="#2563EB" />
              Kesimpulan Dampak Portofolio Kredensial:
            </h4>
            <p style={{ fontSize: '0.85rem', color: '#475569', lineHeight: 1.55 }}>
              {job.delta > 1.0 ? (
                <>Penambahan sertifikasi industri resmi (Tier A/B) memberikan <strong>lonjakan masif (+{deltaPct}% / +{job.delta.toFixed(2)} poin)</strong> pada posisi ini. Kredensial industri berhasil memvalidasi kesiapan kerja praktis yang melengkapi fondasi teori akademik di perkuliahan.</>
              ) : job.delta > 0.1 ? (
                <>Penambahan sertifikasi industri memberikan <strong>penguatan terarah (+{deltaPct}% / +{job.delta.toFixed(2)} poin)</strong>, mempertajam spesialisasi teknis Anda pada lowongan target ini.</>
              ) : (
                <>Skor kelayakan pada lowongan ini didominasi oleh fondasi capaian mata kuliah kurikulum KHS yang sudah sangat selaras (skor stabil).</>
              )}
            </p>
          </div>
        </div>
      )}

      {/* TAB 3: SHAP Feature Attribution with Narrative */}
      {activeTab === 'shap' && (
        <div>
          {/* SHAP Narrative Explanation Box */}
          <div style={{ background: '#F8FAFC', borderLeft: '4px solid #8B5CF6', borderRadius: '12px', padding: '1rem 1.15rem', marginBottom: '1.25rem' }}>
            <div style={{ fontWeight: 800, fontSize: '0.86rem', color: '#6D28D9', display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.3rem' }}>
              <BarChart3 size={16} />
              Interpretasi Atribusi Fitur SHAP (SHapley Additive exPlanations):
            </div>
            <p style={{ fontSize: '0.84rem', color: '#334155', lineHeight: 1.5, margin: 0 }}>
              Grafik SHAP di bawah ini mengukur kontribusi kuantitatif dari setiap mata kuliah kurikulum dan sertifikasi industri dalam mendongkrak skor kelayakan Anda. 
              Fitur dengan batang <strong>hijau (+)</strong> menunjukkan pendorong kelayakan utama, sedangkan sertifikasi resmi dengan bobot Tier A/B menyumbangkan nilai kontribusi tertinggi.
            </p>
          </div>

          <h4 style={{ fontSize: '0.9rem', fontWeight: 800, color: '#1E293B', marginBottom: '0.85rem' }}>
            📊 Bobot Kontribusi Fitur Profil Terhadap Lowongan Ini:
          </h4>

          {job.shap_features && job.shap_features.length > 0 ? (
            job.shap_features.map((feat, fIdx) => {
              const val = feat.value;
              const isPos = val >= 0;
              const absPct = Math.min(100, Math.round(Math.abs(val) * 35));
              return (
                <div key={fIdx} className="shap-row">
                  <div className="shap-label-box">
                    <span style={{ color: '#1E293B', fontWeight: 600 }}>
                      <FormattedText text={feat.feature} />
                    </span>
                    <span style={{ color: isPos ? '#059669' : '#DC2626', fontWeight: 800 }}>
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

      {/* TAB 4: DiCE Roadmap with Narrative */}
      {activeTab === 'dice' && (
        <div>
          {/* DiCE Narrative Explanation Box */}
          <div style={{ background: '#F8FAFC', borderLeft: '4px solid #2563EB', borderRadius: '12px', padding: '1rem 1.15rem', marginBottom: '1.25rem' }}>
            <div style={{ fontWeight: 800, fontSize: '0.86rem', color: '#1E40AF', display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.3rem' }}>
              <Compass size={16} />
              Interpretasi Rekomendasi DiCE (Diverse Counterfactual Explanations):
            </div>
            <p style={{ fontSize: '0.84rem', color: '#334155', lineHeight: 1.5, margin: 0 }}>
              Sistem AI menganalisis basis data <strong>1.139 katalog kursus & sertifikasi industri resmi</strong> (Google, AWS, Meta, IBM, Cisco, DeepLearning.AI, SAP) untuk menemukan intervensi minimal paling efektif. 
              Mengambil kursus yang direkomendasikan di bawah ini akan secara langsung <strong>menutup kesenjangan kompetensi (skill gap)</strong> dan meningkatkan skor kecocokan karir Anda.
            </p>
          </div>

          <h4 style={{ fontSize: '0.9rem', fontWeight: 800, color: '#1E293B', marginBottom: '0.85rem' }}>
            🧭 Rekomendasi Intervensi Kursus untuk Memaksimalkan Skor:
          </h4>

          {job.dice_recommendations && job.dice_recommendations.length > 0 ? (
            job.dice_recommendations.map((dice, dIdx) => (
              <div key={dIdx} className="dice-course-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.35rem' }}>
                  <div style={{ fontWeight: 800, fontSize: '0.95rem', color: '#0F172A' }}>
                    <FormattedText text={dice.course_name} />
                  </div>
                  <span style={{ background: '#EFF6FF', color: '#1E40AF', padding: '0.25rem 0.6rem', borderRadius: '8px', fontSize: '0.78rem', fontWeight: 800, border: '1px solid #BFDBFE' }}>
                    +{dice.score_delta.toFixed(2)} Est. Boost
                  </span>
                </div>
                <p style={{ fontSize: '0.84rem', color: '#475569', lineHeight: 1.45 }}>
                  <FormattedText text={dice.detail} />
                </p>
              </div>
            ))
          ) : (
            <p style={{ color: '#94A3B8', fontSize: '0.88rem' }}>Tidak ada rekomendasi intervensi tambahan untuk lowongan ini.</p>
          )}
        </div>
      )}
    </div>
  );
}
