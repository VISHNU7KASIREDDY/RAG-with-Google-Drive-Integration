/**
 * DriveRAG — StatusBadge Component
 */

import { CheckCircle, Clock, Loader2, AlertCircle } from 'lucide-react';

interface StatusBadgeProps {
  status: 'pending' | 'processing' | 'indexed' | 'failed';
  errorMessage?: string | null;
}

const config: Record<string, { label: string; cls: string; Icon: typeof Clock; spin?: boolean }> = {
  pending:    { label: 'Pending',    cls: 'badge badge-pending',    Icon: Clock },
  processing: { label: 'Processing', cls: 'badge badge-processing', Icon: Loader2, spin: true },
  indexed:    { label: 'Indexed',    cls: 'badge badge-indexed',    Icon: CheckCircle },
  failed:     { label: 'Failed',     cls: 'badge badge-failed',     Icon: AlertCircle },
};

export default function StatusBadge({ status, errorMessage }: StatusBadgeProps) {
  const { label, cls, Icon, spin } = config[status] || config.pending;

  return (
    <span className={cls} title={status === 'failed' && errorMessage ? errorMessage : undefined}>
      <Icon size={11} style={spin ? { animation: 'spin 1s linear infinite' } : undefined} />
      {label}
    </span>
  );
}
