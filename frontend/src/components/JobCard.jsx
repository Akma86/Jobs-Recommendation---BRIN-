import React from 'react';
import { 
  Building2, 
  MapPin, 
  Sparkles, 
  TrendingUp, 
  Bookmark, 
  Award,
  BookOpen
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
  onToggleSave 
}) {
  const charCode = job.company ? job.company.charCodeAt(0) : 65;
  const avatarBg = AVATAR_COLORS[charCode % AVATAR_COLORS.length];
  const initial = job.company ? job.company.charAt(0).toUpperCase() : 'J';

  return (
    <div 
      className={`job-card ${isSelected ? 'active' : ''}`}
      onClick={onSelect}
    >
      <div className="job-card-header">
        <div className="company-logo" style={{ background: avatarBg }}>
          {initial}
        </div>

        <div className="job-card-title-box">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <h3 className="job-card-title">{job.title}</h3>
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
              <Bookmark size={18} fill={isSaved ? "#2563EB" : "none"} />
            </button>
          </div>
          <div className="job-card-company">{job.company}</div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.8rem', color: '#64748B', marginBottom: '0.5rem' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
          <MapPin size={13} /> {job.location || 'Indonesia / Remote'}
        </span>
        <span>•</span>
        <span>Peringkat #{job.rank}</span>
      </div>

      {/* Badges */}
      <div className="job-card-badges">
        {/* Match Percentage */}
        <span className="badge-match">
          <Sparkles size={12} />
          {job.match_pct}% Match
        </span>

        {/* Certificate Delta Boost */}
        {job.delta > 0.1 && (
          <span className="badge-boost">
            <TrendingUp size={12} />
            +{job.delta.toFixed(2)} Sertifikat
          </span>
        )}

        {/* Credibility / OBE Tag */}
        <span className="badge-tag">
          <Award size={11} style={{ marginRight: '3px' }} />
          Tier A/B Validated
        </span>
      </div>
    </div>
  );
}
