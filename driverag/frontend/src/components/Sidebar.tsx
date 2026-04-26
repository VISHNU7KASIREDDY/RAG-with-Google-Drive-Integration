import { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { MessageSquare, FileText, Sparkles, Database, Layers, CloudOff, CloudCog } from 'lucide-react';
import SyncButton from './SyncButton';
import type { Stats } from '../types';
import { getStats, getAuthStatus } from '../api/client';

export default function Sidebar() {
  const [stats, setStats] = useState<Stats>({ total_docs: 0, total_chunks: 0, last_sync_time: null });
  const [connected, setConnected] = useState<boolean | null>(null);

  const fetchStats = async () => {
    try { setStats(await getStats()); } catch { /* */ }
  };

  const checkAuth = async () => {
    try { setConnected((await getAuthStatus()).connected); } catch { /* */ }
  };

  useEffect(() => {
    fetchStats();
    checkAuth();
    const interval = setInterval(() => { fetchStats(); checkAuth(); }, 15000);
    return () => clearInterval(interval);
  }, []);

  // Check URL params for auth callback
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('auth') === 'success') {
      setConnected(true);
      window.history.replaceState({}, '', '/');
    }
  }, []);

  const handleConnect = () => {
    window.location.href = '/api/auth/google';
  };

  return (
    <aside className="app-sidebar" id="sidebar">
      {/* Logo */}
      <div style={{ padding: '20px 20px 18px', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 38, height: 38, borderRadius: 12,
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 16px rgba(99,102,241,0.25)',
          }}>
            <Sparkles size={18} color="#fff" />
          </div>
          <div>
            <h1 style={{ fontSize: 16, fontWeight: 700, color: '#fff', letterSpacing: '-0.02em', lineHeight: 1.2 }}>
              DriveRAG
            </h1>
            <p style={{ fontSize: 10, color: '#6b7280', fontWeight: 500, letterSpacing: '0.06em', textTransform: 'uppercase' as const }}>
              AI Document Assistant
            </p>
          </div>
        </div>
      </div>

      {/* Connect Google Drive */}
      <div style={{ padding: '16px 12px 8px' }}>
        {connected === false ? (
          <button
            onClick={handleConnect}
            id="connect-drive-btn"
            style={{
              width: '100%', padding: '12px 16px', border: 'none', borderRadius: 10, cursor: 'pointer',
              background: 'linear-gradient(135deg, #4285f4, #34a853)',
              color: '#fff', fontSize: 13, fontWeight: 600, display: 'flex', alignItems: 'center',
              justifyContent: 'center', gap: 8, transition: 'all 0.2s',
            }}
            onMouseOver={(e) => (e.currentTarget.style.transform = 'translateY(-1px)')}
            onMouseOut={(e) => (e.currentTarget.style.transform = 'translateY(0)')}
          >
            <CloudOff size={16} />
            Connect Google Drive
          </button>
        ) : connected === true ? (
          <div style={{
            padding: '10px 14px', borderRadius: 10,
            background: 'rgba(52,168,83,0.1)', border: '1px solid rgba(52,168,83,0.2)',
            display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, color: '#34a853', fontWeight: 500,
          }}>
            <CloudCog size={15} />
            Google Drive Connected
          </div>
        ) : null}
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: '8px 12px', display: 'flex', flexDirection: 'column' as const, gap: 4 }}>
        <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} id="nav-chat">
          <MessageSquare size={18} /> Chat
        </NavLink>
        <NavLink to="/documents" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} id="nav-documents">
          <FileText size={18} /> Documents
        </NavLink>
      </nav>

      {/* Sync */}
      <div style={{ padding: '0 12px 12px' }}>
        <SyncButton onSyncComplete={fetchStats} />
      </div>

      {/* Stats */}
      <div style={{ padding: '0 12px 16px' }}>
        <div className="card-sm" style={{ padding: '14px 16px' }}>
          <p style={{ fontSize: 10, color: '#6b7280', fontWeight: 600, textTransform: 'uppercase' as const, letterSpacing: '0.06em', marginBottom: 10 }}>
            Index Stats
          </p>
          <div style={{ display: 'flex', flexDirection: 'column' as const, gap: 8 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 12, color: '#9ca3af' }}>
                <Database size={13} /> Documents
              </span>
              <span style={{ fontSize: 12, fontWeight: 600, color: '#e5e7eb', fontVariantNumeric: 'tabular-nums' }}>
                {stats.total_docs}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 12, color: '#9ca3af' }}>
                <Layers size={13} /> Chunks
              </span>
              <span style={{ fontSize: 12, fontWeight: 600, color: '#e5e7eb', fontVariantNumeric: 'tabular-nums' }}>
                {stats.total_chunks.toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
