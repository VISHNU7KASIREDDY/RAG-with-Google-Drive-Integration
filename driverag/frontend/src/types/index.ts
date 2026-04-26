/* ─── TypeScript Types for DriveRAG ────────────────────── */

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  timestamp: Date;
  isLoading?: boolean;
}

export interface Source {
  file_name: string;
  doc_id: string;
  chunk_text: string;
  score: number;
  page?: number | null;
}

export interface Document {
  id: string;
  file_name: string;
  status: 'pending' | 'processing' | 'indexed' | 'failed';
  chunk_count: number;
  last_synced: string | null;
  mime_type?: string | null;
  error_message?: string | null;
}

export interface Stats {
  total_docs: number;
  total_chunks: number;
  last_sync_time: string | null;
}

export interface SyncResponse {
  message: string;
  total_files: number;
  new_files: number;
  updated_files: number;
  skipped_files: number;
  failed_files: number;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
  query: string;
}

export interface DeleteResponse {
  message: string;
  doc_id: string;
  chunks_removed: number;
}
