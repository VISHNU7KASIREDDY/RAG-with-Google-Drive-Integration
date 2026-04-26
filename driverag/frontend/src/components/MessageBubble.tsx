/**
 * DriveRAG — MessageBubble Component
 */

import { useState } from 'react';
import { Copy, Check, User, Bot, RotateCcw } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message } from '../types';
import SourceCard from './SourceCard';

interface MessageBubbleProps {
  message: Message;
  onRetry?: () => void;
}

export default function MessageBubble({ message, onRetry }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);
  const [showSources, setShowSources] = useState(true);
  const isUser = message.role === 'user';
  const isError = message.content.startsWith('⚠️');

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch { /* */ }
  };

  const time = new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <div
      className={isUser ? 'anim-slide-r' : 'anim-slide-l'}
      style={{
        display: 'flex', gap: 12, width: '100%',
        flexDirection: isUser ? 'row-reverse' : 'row',
        alignItems: 'flex-start',
      }}
      id={`message-${message.id}`}
    >
      {/* Avatar */}
      <div style={{
        width: 34, height: 34, borderRadius: 11, flexShrink: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: isUser ? 'rgba(99,102,241,0.12)' : 'rgba(55,65,81,0.4)',
        border: `1px solid ${isUser ? 'rgba(99,102,241,0.2)' : 'rgba(75,85,99,0.3)'}`,
      }}>
        {isUser ? <User size={15} color="#818cf8" /> : <Bot size={15} color="#d1d5db" />}
      </div>

      {/* Content column */}
      <div style={{
        display: 'flex', flexDirection: 'column', gap: 6, minWidth: 0,
        alignItems: isUser ? 'flex-end' : 'flex-start',
      }}>
        {/* Bubble */}
        <div className={isUser ? 'bubble-user' : isError ? 'bubble-error' : 'bubble-assistant'}>
          {message.isLoading ? (
            <div className="typing-dots"><span /><span /><span /></div>
          ) : isUser ? (
            <p style={{ fontSize: 14, lineHeight: 1.6, whiteSpace: 'pre-wrap' as const, margin: 0 }}>{message.content}</p>
          ) : (
            <div className="md-body">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Actions row */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, paddingLeft: 4, paddingRight: 4 }}>
          <span style={{ fontSize: 10, color: '#4b5563' }}>{time}</span>

          {!isUser && !message.isLoading && !isError && (
            <button onClick={handleCopy} className="btn-ghost" style={{ padding: '3px 6px', fontSize: 10 }} title="Copy">
              {copied ? <Check size={11} color="#4ade80" /> : <Copy size={11} />}
            </button>
          )}

          {isError && onRetry && (
            <button onClick={onRetry} className="btn-ghost" style={{
              padding: '3px 8px', fontSize: 11, color: '#f87171',
              background: 'rgba(239,68,68,0.06)', border: '1px solid rgba(239,68,68,0.12)', borderRadius: 8,
            }}>
              <RotateCcw size={11} /> Retry
            </button>
          )}
        </div>

        {/* Sources */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div style={{ width: '100%', marginTop: 2 }}>
            <button
              onClick={() => setShowSources(!showSources)}
              style={{
                fontSize: 12, color: '#818cf8', background: 'none', border: 'none',
                cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4, marginBottom: 6,
              }}
              id="toggle-sources-btn"
            >
              📎 {message.sources.length} source{message.sources.length !== 1 ? 's' : ''}
              <span style={{ fontSize: 9 }}>{showSources ? '▾' : '▸'}</span>
            </button>
            {showSources && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {message.sources.map((source, i) => (
                  <SourceCard key={`${source.doc_id}-${i}`} source={source} index={i} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
