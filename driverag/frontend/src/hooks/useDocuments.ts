/**
 * DriveRAG — Documents Hook
 *
 * Manages document list fetching, stats, and deletion.
 */

import { useState, useEffect, useCallback } from 'react';
import type { Document, Stats } from '../types';
import {
  getDocuments,
  getStats,
  deleteDocument as apiDeleteDocument,
} from '../api/client';

export function useDocuments() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [stats, setStats] = useState<Stats>({
    total_docs: 0,
    total_chunks: 0,
    last_sync_time: null,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const [docs, docStats] = await Promise.all([
        getDocuments(),
        getStats(),
      ]);
      setDocuments(docs);
      setStats(docStats);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch documents';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deleteDoc = useCallback(async (docId: string) => {
    try {
      await apiDeleteDocument(docId);
      // Optimistically remove from local state
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
      // Refresh stats
      const docStats = await getStats();
      setStats(docStats);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete document';
      setError(message);
      throw err;
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  return {
    documents,
    stats,
    isLoading,
    error,
    refresh: fetchDocuments,
    deleteDocument: deleteDoc,
  };
}
