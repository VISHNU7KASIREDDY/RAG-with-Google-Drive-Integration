import axios from 'axios';
import type { SyncResponse, AskResponse, Document, Stats, DeleteResponse } from '../types';

// Fixed demo session – every visitor shares the same pre-synced Drive data
export const SESSION_ID = 'demo';

const api = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL || ''}/api`,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
    'X-Session-ID': SESSION_ID,
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred';

    console.error('[API Error]', message);
    return Promise.reject(new Error(message));
  }
);

export async function syncDrive(forceResync = false): Promise<SyncResponse> {
  const { data } = await api.post<SyncResponse>('/sync-drive', {
    force_resync: forceResync,
  });
  return data;
}

export async function getSyncStatus(): Promise<{
  is_syncing: boolean;
  current_file: string | null;
  files_processed: number;
  total_files: number;
}> {
  const { data } = await api.get('/sync-drive/status');
  return data;
}

export async function askQuestion(
  query: string,
  topK = 5
): Promise<AskResponse> {
  const { data } = await api.post<AskResponse>('/ask', {
    query,
    top_k: topK,
  });
  return data;
}

export async function getDocuments(): Promise<Document[]> {
  const { data } = await api.get<Document[]>('/documents');
  return data;
}

export async function getStats(): Promise<Stats> {
  const { data } = await api.get<Stats>('/documents/stats');
  return data;
}

export async function deleteDocument(docId: string): Promise<DeleteResponse> {
  const { data } = await api.delete<DeleteResponse>(`/documents/${docId}`);
  return data;
}

export async function getAuthStatus(): Promise<{ connected: boolean }> {
  const { data } = await api.get<{ connected: boolean }>('/auth/status');
  return data;
}

export async function disconnectDrive(): Promise<{ message: string }> {
  const { data } = await api.post<{ message: string }>('/auth/disconnect');
  return data;
}

export default api;
