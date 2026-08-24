import React from 'react';
import FormattedText from './FormattedText';
import { 
  Building2, 
  MapPin, 
  Sparkles, 
  TrendingUp, 
  Bookmark, 
  Award, 
  BookOpen, 
  CheckCircle2
} from 'lucide-react';

const AVATAR_COLORS = [
  'linear-gradient(135deg, #3B82F6, #1D4ED8)',
  'linear-gradient(135deg, #10B981, #047857)',
  'linear-gradient(135deg, #8B5CF6, #6D28D9)',
  'linear-gradient(135deg, #F59E0B, #D97706)',
  'linear-gradient(135deg, #EC4899, #BE185D)',
  'linear-gradient(135deg, #06B6D4, #0E7490)',
];

export default function JobCard({ 
  job, 
  isSelected, 
  onSelect, 
  isSaved, 
  onToggleSave,
  density = 'comfortable'
}) {
  const charCode = job.company ? job.company.charCodeAt(0) : 65;
  const avatarBg = AVATAR_COLORS[charCode % AVATAR_COLORS.length];
  const initial = job.company ? job.company.charAt(0).toUpperCase() : 'J';

  // Match score color styling
  const matchPct = job.match_pct || 75.0;
  const isHighMatch = matchPct >= 85.0;
  const isMedMatch = matchPct >= 75.0;

  const matchBadgeBg = isHighMatch 
    ? 'linear-gradient(135deg, #ECFDF5, #D1FAE5)' 
    : (isMedMatch ? 'linear-gradient(135deg, #EFF6FF, #DBEAFE)' : '#F1F5F9');
  
  const matchBadgeColor = isHighMatch ? '#065F46' : (isMedMatch ? '#1E40AF' : '#475569');
  const matchBadgeBorder = isHighMatch ? '#A7F3D0' : (isMedMatch ? '#BFDBFE' : '#CBD5E1');

  // Extract top matching reason preview
  const topComponent = job.narrative?.components && job.narrative.components.length > 0 
    ? job.narrative.components[0] 
    : null;

  const isCompact = density === 'compact';

  return (
    <div 
      className={`job-card ${isCompact ? 'compact' : ''} ${isSelected ? 'active' : ''}`}
      onClick={onSelect}
      style={{
        borderLeft: isSelected ? '4px solid #2563EB' : '1px solid #E2E8F0',
        transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
        position: 'relative'
      }}
    >
      <div className="job-card-header" style={{ alignItems: 'flex-start' }}>
        <div className="company-logo" style={{ background: avatarBg, flexShrink: 0 }}>
          {initial}
        </div>

        <div className="job-card-title-box" style={{ flex: 1 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem' }}>
            <div>
              <h3 className="job-card-title" style={{ fontSize: isCompact ? '0.96rem' : '1.05rem', fontWeight: 800 }}>
                {job.title}
              </h3>
              <div className="job-card-company" style={{ fontSize: isCompact ? '0.78rem' : '0.86rem', color: '#475569', marginTop: '0.1rem' }}>
                {job.company}
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', flexShrink: 0 }}>
              {/* Match Score Badge */}
              <div style={{
                background: matchBadgeBg,
                color: matchBadgeColor,
                border: `1px solid ${matchBadgeBorder}`,
                padding: isCompact ? '0.15rem 0.5rem' : '0.25rem 0.65rem',
                borderRadius: '9999px',
                fontSize: isCompact ? '0.76rem' : '0.82rem',
                fontWeight: 800,
                display: 'flex',
                alignItems: 'center',
                gap: '0.25rem',
                boxShadow: isHighMatch ? '0 2px 6px rgba(16,185,129,0.15)' : 'none'
              }}>
                <Sparkles size={isCompact ? 11 : 13} />
                {matchPct}%
              </div>

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onToggleSave(job.job_id);
                }}
                style={{
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  color: isSaved ? '#2563EB' : '#94A3B8',
                  padding: '2px'
                }}
                title={isSaved ? "Hapus dari Simpanan" : "Simpan Lowongan"}
              >
                <Bookmark size={isCompact ? 16 : 18} fill={isSaved ? "#2563EB" : "none"} />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', fontSize: '0.78rem', color: '#64748B', margin: isCompact ? '0.25rem 0' : '0.5rem 0' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
          <MapPin size={12} /> {job.location || 'Indonesia / Remote'}
        </span>
        <span>•</span>
        <span>Peringkat #{job.rank}</span>
        {job.delta > 0.1 && (
          <>
            <span>•</span>
            <span style={{ color: '#059669', fontWeight: 700 }}>+{job.delta.toFixed(2)} Boost</span>
          </>
        )}
      </div>

      {/* Match Reason Summary Box (Shown only in comfortable mode or short chip in compact) */}
      {!isCompact && topComponent && (
        <div style={{
          background: '#F8FAFC',
          border: '1px dashed #CBD5E1',
          borderRadius: '8px',
          padding: '0.45rem 0.65rem',
          fontSize: '0.78rem',
          color: '#334155',
          marginBottom: '0.6rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.4rem'
        }}>
          <CheckCircle2 size={13} color="#059669" style={{ flexShrink: 0 }} />
          <span>
            <strong>Alasan Cocok:</strong> Keselarasan tinggi pada <strong><FormattedText text={topComponent.name} /></strong> ({topComponent.relevance_match_pct}% match)
          </span>
        </div>
      )}

      {/* Badges (Comfortable mode only) */}
      {!isCompact && (
        <div className="job-card-badges">
          {job.delta > 0.1 && (
            <span className="badge-boost">
              <TrendingUp size={12} />
              +{job.delta.toFixed(2)} Sertifikat Boost
            </span>
          )}
          <span className="badge-tag">
            <Award size={11} style={{ marginRight: '3px' }} />
            Tier A/B Validated
          </span>
        </div>
      )}
    </div>
  );
}
