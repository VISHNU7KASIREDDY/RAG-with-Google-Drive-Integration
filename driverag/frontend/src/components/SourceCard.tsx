/**
 * DriveRAG — SourceCard Component
 */

import { useState } from 'react';
import { FileText, ChevronDown, ChevronUp } from 'lucide-react';
import type { Source } from '../types';

interface SourceCardProps {
  source: Source;
  index: number;
}

function scoreColor(s: number) {
  return s >= 0.8 ? '#4ade80' : s >= 0.6 ? '#facc15' : '#f87171';
}
function scoreBg(s: number) {
  return s >= 0.8 ? 'rgba(34,197,94,0.1)' : s >= 0.6 ? 'rgba(234,179,8,0.1)' : 'rgba(239,68,68,0.1)';
}

export default function SourceCard({ source, index }: SourceCardProps) {
  const [open, setOpen] = useState(false);

  return (
    <div
      className="card-sm tr-colors anim-fade-up"
      style={{ cursor: 'pointer', animationDelay: `${index * 60}ms`, overflow: 'hidden' }}
      onClick={() => setOpen(!open)}
      id={`source-card-${index}`}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 0 }}>
          <div style={{
            width: 28, height: 28, borderRadius: 8,
            background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.15)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
          }}>
            <FileText size={13} color="#818cf8" />
          </div>
          <span style={{ fontSize: 13, fontWeight: 500, color: '#e5e7eb', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' as const }}>
            {source.file_name}
          </span>
          {source.page && <span style={{ fontSize: 11, color: '#6b7280', flexShrink: 0 }}>p.{source.page}</span>}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
          <span style={{
            fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 9999,
            color: scoreColor(source.score), background: scoreBg(source.score),
          }}>
            {(source.score * 100).toFixed(0)}%
          </span>
          {open ? <ChevronUp size={13} color="#6b7280" /> : <ChevronDown size={13} color="#6b7280" />}
        </div>
      </div>
      {open && (
        <div style={{ padding: '0 14px 12px' }}>
          <div style={{
            background: 'rgba(10,15,26,0.5)', borderRadius: 8, padding: 12,
            border: '1px solid rgba(255,255,255,0.04)',
            fontSize: 12, lineHeight: 1.6, color: '#9ca3af', whiteSpace: 'pre-wrap' as const,
          }}>
            {source.chunk_text}
          </div>
        </div>
      )}
    </div>
  );
}
