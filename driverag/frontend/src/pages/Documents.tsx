/**
 * DriveRAG — Documents Page
 */

import { Database, Layers, Clock, RefreshCw } from 'lucide-react';
import { useDocuments } from '../hooks/useDocuments';
import DocumentList from '../components/DocumentList';

function formatDate(d: string | null): string {
  if (!d) return 'Never';
  return new Date(d).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

export default function Documents() {
  const { documents, stats, isLoading, error, deleteDocument, refresh } = useDocuments();

  const statCards = [
    { icon: Database, color: '#818cf8', label: 'Documents', value: stats.total_docs.toString() },
    { icon: Layers,   color: '#a78bfa', label: 'Total Chunks', value: stats.total_chunks.toLocaleString() },
    { icon: Clock,    color: '#4ade80', label: 'Last Sync', value: formatDate(stats.last_sync_time), small: true },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }} id="documents-page">
      {/* Header */}
      <div className="page-header">
        <h2 style={{ fontSize: 14, fontWeight: 600, color: '#d1d5db' }}>Documents</h2>
        <button onClick={refresh} className="btn-ghost" style={{ fontSize: 12 }}>
          <RefreshCw size={13} /> Refresh
        </button>
      </div>

      {/* Stats */}
      <div style={{ padding: '16px 24px', borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, maxWidth: 680 }}>
          {statCards.map(({ icon: Icon, color, label, value, small }, i) => (
            <div
              key={label}
              className="card anim-fade-up"
              style={{ padding: '14px 18px', animationDelay: `${i * 80}ms` }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 8 }}>
                <Icon size={14} color={color} />
                <span style={{ fontSize: 10, color: '#6b7280', fontWeight: 600, textTransform: 'uppercase' as const, letterSpacing: '0.05em' }}>
                  {label}
                </span>
              </div>
              <p style={{
                fontSize: small ? 14 : 24, fontWeight: 700, color: '#fff',
                fontVariantNumeric: 'tabular-nums', lineHeight: 1.2,
              }}>
                {value}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 24px' }}>
        {isLoading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {[...Array(5)].map((_, i) => (
              <div key={i} className="anim-shimmer" style={{ height: 52, borderRadius: 12, animationDelay: `${i * 100}ms` }} />
            ))}
          </div>
        ) : error ? (
          <div className="anim-fade-up" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '64px 0', textAlign: 'center' }}>
            <p style={{ fontSize: 14, color: '#f87171', marginBottom: 8 }}>Failed to load documents</p>
            <p style={{ fontSize: 12, color: '#4b5563', marginBottom: 16 }}>{error}</p>
            <button onClick={refresh} className="btn-primary" style={{ fontSize: 12, padding: '8px 18px' }}>Try Again</button>
          </div>
        ) : (
          <DocumentList documents={documents} onDelete={deleteDocument} />
        )}
      </div>
    </div>
  );
}
