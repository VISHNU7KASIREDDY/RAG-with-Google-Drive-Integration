import { useState, useEffect, useRef } from 'react';
import { RefreshCw, CheckCircle, AlertCircle, HardDrive } from 'lucide-react';
import { syncDrive, getSyncStatus } from '../api/client';

interface SyncButtonProps {
  onSyncComplete?: () => void;
}

type SyncState = 'idle' | 'syncing' | 'success' | 'error';

export default function SyncButton({ onSyncComplete }: SyncButtonProps) {
  const [state, setState] = useState<SyncState>('idle');
  const [status, setStatus] = useState<{ current_file: string | null; files_processed: number; total_files: number }>({ current_file: null, files_processed: 0, total_files: 0 });
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = () => {
    if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null; }
  };

  const pollStatus = () => {
    pollRef.current = setInterval(async () => {
      try {
        const s = await getSyncStatus();
        setStatus(s);
        if (!s.is_syncing && state === 'syncing') {
          stopPolling();
          setState('success');
          onSyncComplete?.();
          setTimeout(() => setState('idle'), 4000);
        }
      } catch { /* ignore */ }
    }, 2000);
  };

  useEffect(() => () => stopPolling(), []);

  const handleSync = async () => {
    if (state === 'syncing') return;
    setState('syncing');
    setError(null);
    try {
      await syncDrive(false);
      pollStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sync failed');
      setState('error');
      setTimeout(() => setState('idle'), 5000);
    }
  };

  const progress = status.total_files > 0
    ? Math.round((status.files_processed / status.total_files) * 100)
    : 0;

  const btnStyle: React.CSSProperties = {
    width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center',
    gap: 8, padding: '10px 16px', borderRadius: 12, fontSize: 13, fontWeight: 600,
    border: 'none', cursor: state === 'syncing' ? 'wait' : 'pointer', transition: 'all 0.15s ease',
    ...(state === 'idle' ? { background: '#4f46e5', color: '#fff' } :
      state === 'syncing' ? { background: 'rgba(99,102,241,0.15)', color: '#818cf8', border: '1px solid rgba(99,102,241,0.15)' } :
      state === 'success' ? { background: 'rgba(34,197,94,0.08)', color: '#4ade80', border: '1px solid rgba(34,197,94,0.15)' } :
      { background: 'rgba(239,68,68,0.08)', color: '#f87171', border: '1px solid rgba(239,68,68,0.15)' }),
  };

  return (
    <div id="sync-button-container">
      <button onClick={handleSync} disabled={state === 'syncing'} style={btnStyle} id="sync-drive-btn">
        {state === 'syncing' ? <><RefreshCw size={15} style={{ animation: 'spin 1s linear infinite' }} /> Syncing...</> :
         state === 'success' ? <><CheckCircle size={15} /> Synced!</> :
         state === 'error' ? <><AlertCircle size={15} /> Failed</> :
         <><HardDrive size={15} /> Sync Drive</>}
      </button>

      {state === 'syncing' && (
        <div className="anim-fade-up" style={{
          marginTop: 8, padding: '10px 12px', borderRadius: 10,
          background: 'rgba(99,102,241,0.04)', border: '1px solid rgba(99,102,241,0.1)',
          fontSize: 11, color: '#9ca3af',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
            <span style={{ color: '#818cf8', fontWeight: 600 }}>
              {status.current_file ? `Processing: ${status.current_file.slice(0, 25)}...` : 'Starting...'}
            </span>
            <span>{progress}%</span>
          </div>
          <div style={{ height: 4, borderRadius: 2, background: 'rgba(99,102,241,0.1)' }}>
            <div style={{ height: '100%', borderRadius: 2, background: '#6366f1', width: `${progress}%`, transition: 'width 0.3s' }} />
          </div>
          <div style={{ marginTop: 4, fontSize: 10 }}>
            {status.files_processed}/{status.total_files} files
          </div>
        </div>
      )}

      {state === 'success' && (
        <div className="anim-fade-up" style={{
          marginTop: 8, padding: '10px 12px', borderRadius: 10,
          background: 'rgba(34,197,94,0.04)', border: '1px solid rgba(34,197,94,0.1)',
          fontSize: 11, color: '#4ade80', fontWeight: 600,
        }}>
          Sync complete! {status.files_processed} files indexed.
        </div>
      )}

      {state === 'error' && error && (
        <div className="anim-fade-up" style={{
          marginTop: 8, padding: '8px 12px', borderRadius: 10,
          background: 'rgba(239,68,68,0.04)', border: '1px solid rgba(239,68,68,0.1)',
          fontSize: 11, color: '#f87171',
        }}>
          {error}
        </div>
      )}
    </div>
  );
}
