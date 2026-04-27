import { useState } from 'react';
import { FileText, FileType, File, Trash2, Search, AlertTriangle } from 'lucide-react';
import type { Document } from '../types';
import StatusBadge from './StatusBadge';

interface DocumentListProps {
  documents: Document[];
  onDelete: (docId: string) => void;
}

function getFileIcon(mime?: string | null) {
  if (!mime) return <File size={17} color="#6b7280" />;
  if (mime.includes('pdf')) return <FileText size={17} color="#f87171" />;
  if (mime.includes('document')) return <FileType size={17} color="#60a5fa" />;
  return <File size={17} color="#6b7280" />;
}

function timeAgo(d: string | null): string {
  if (!d) return 'Never';
  const s = Math.floor((Date.now() - new Date(d).getTime()) / 1000);
  if (s < 60) return 'Just now';
  const m = Math.floor(s / 60); if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

export default function DocumentList({ documents, onDelete }: DocumentListProps) {
  const [query, setQuery] = useState('');
  const [delId, setDelId] = useState<string | null>(null);

  const filtered = documents.filter(d => d.file_name.toLowerCase().includes(query.toLowerCase()));

  const handleDelete = (id: string) => {
    if (delId === id) { onDelete(id); setDelId(null); }
    else { setDelId(id); setTimeout(() => setDelId(null), 3000); }
  };

  return (
    <div id="document-list">
      <div style={{ position: 'relative', marginBottom: 16 }}>
        <Search size={15} color="#6b7280" style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)' }} />
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search documents..."
          className="input-base"
          style={{ paddingLeft: 40 }}
          id="doc-search-input"
        />
      </div>

      {filtered.length === 0 ? (
        <div className="anim-fade-up" style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          padding: '64px 0', textAlign: 'center',
        }}>
          <div style={{
            width: 64, height: 64, borderRadius: 18,
            background: 'rgba(26,34,54,0.5)', border: '1px solid rgba(255,255,255,0.06)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 16,
          }}>
            <FileText size={28} color="#4b5563" />
          </div>
          <p style={{ fontSize: 14, fontWeight: 500, color: '#9ca3af', marginBottom: 4 }}>
            {query ? 'No matching documents' : 'No documents synced yet'}
          </p>
          <p style={{ fontSize: 12, color: '#4b5563' }}>
            {query ? 'Try a different search term' : 'Click "Sync Drive" in the sidebar to get started'}
          </p>
        </div>
      ) : (
        <div style={{ borderRadius: 14, overflow: 'hidden', border: '1px solid rgba(255,255,255,0.04)' }}>
          <table className="doc-table">
            <thead>
              <tr>
                <th>File</th>
                <th>Status</th>
                <th style={{ textAlign: 'center' }}>Chunks</th>
                <th>Synced</th>
                <th style={{ textAlign: 'center', width: 60 }}></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((doc, i) => (
                <tr key={doc.id} className="anim-fade-up" style={{ animationDelay: `${i * 30}ms` }}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      {getFileIcon(doc.mime_type)}
                      <span style={{ fontWeight: 500, color: '#e5e7eb', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' as const, maxWidth: 280 }}>
                        {doc.file_name}
                      </span>
                    </div>
                  </td>
                  <td><StatusBadge status={doc.status} errorMessage={doc.error_message} /></td>
                  <td style={{ textAlign: 'center', fontVariantNumeric: 'tabular-nums', color: '#9ca3af', fontSize: 12 }}>
                    {doc.chunk_count}
                  </td>
                  <td style={{ fontSize: 12, color: '#6b7280' }}>{timeAgo(doc.last_synced)}</td>
                  <td style={{ textAlign: 'center' }}>
                    <button
                      onClick={() => handleDelete(doc.id)}
                      title={delId === doc.id ? 'Click again to confirm' : 'Delete'}
                      style={{
                        width: 32, height: 32, borderRadius: 8, border: 'none', cursor: 'pointer',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        background: delId === doc.id ? 'rgba(239,68,68,0.12)' : 'transparent',
                        color: delId === doc.id ? '#f87171' : '#6b7280',
                        transition: 'all 0.15s ease',
                      }}
                      id={`delete-doc-${doc.id}`}
                    >
                      {delId === doc.id ? <AlertTriangle size={14} /> : <Trash2 size={14} />}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
