import { useState, useRef, useEffect, type KeyboardEvent } from 'react';
import { Send, Sparkles, MessageSquareText, FileSearch, BookOpen } from 'lucide-react';
import { useChat } from '../hooks/useChat';
import ChatWindow from '../components/ChatWindow';

const EXAMPLES = [
  { icon: FileSearch,       title: 'Search policies', query: 'What is the refund policy?' },
  { icon: BookOpen,         title: 'Summarize docs',  query: 'Summarize the key points from the onboarding guide' },
  { icon: MessageSquareText, title: 'Find info',       query: 'What are the requirements for the project proposal?' },
];

export default function Chat() {
  const { messages, isLoading, sendMessage, retryLast } = useChat();
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    sendMessage(input);
    setInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  useEffect(() => {
    const ta = textareaRef.current;
    if (ta) { ta.style.height = 'auto'; ta.style.height = `${Math.min(ta.scrollHeight, 160)}px`; }
  }, [input]);

  const empty = messages.length === 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }} id="chat-page">
      <div className="page-header">
        <h2 style={{ fontSize: 14, fontWeight: 600, color: '#d1d5db' }}>Chat</h2>
        {messages.length > 0 && (
          <span style={{ fontSize: 12, color: '#4b5563' }}>
            {messages.filter(m => m.role === 'user').length} questions
          </span>
        )}
      </div>

      {empty ? (
        <div className="anim-fade-up" style={{
          flex: 1, display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center', padding: '0 24px',
        }}>
          <div className="glow-accent" style={{
            width: 80, height: 80, borderRadius: 24, marginBottom: 24,
            background: 'linear-gradient(135deg, rgba(99,102,241,0.12), rgba(139,92,246,0.12))',
            border: '1px solid rgba(99,102,241,0.1)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Sparkles size={36} color="#818cf8" />
          </div>
          <h2 style={{ fontSize: 22, fontWeight: 700, color: '#f3f4f6', marginBottom: 8, textAlign: 'center', letterSpacing: '-0.02em' }}>
            Ask anything about your Drive documents
          </h2>
          <p style={{ fontSize: 14, color: '#6b7280', marginBottom: 32, textAlign: 'center', maxWidth: 420, lineHeight: 1.6 }}>
            I'll search through your synced Google Drive files and provide answers with source citations.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, width: '100%', maxWidth: 640 }}>
            {EXAMPLES.map(({ icon: Icon, title, query }, i) => (
              <button
                key={i}
                onClick={() => { setInput(query); textareaRef.current?.focus(); }}
                className="card hover-lift anim-fade-up"
                style={{
                  padding: '16px 18px', textAlign: 'left', cursor: 'pointer',
                  animationDelay: `${i * 100 + 200}ms`, border: '1px solid rgba(255,255,255,0.05)',
                  background: 'rgba(26,34,54,0.4)',
                }}
                id={`example-query-${i}`}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 8 }}>
                  <Icon size={14} color="#818cf8" />
                  <span style={{ fontSize: 12, fontWeight: 600, color: '#d1d5db' }}>{title}</span>
                </div>
                <p style={{ fontSize: 12, color: '#6b7280', lineHeight: 1.5, margin: 0 }}>"{query}"</p>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <ChatWindow messages={messages} onRetry={retryLast} />
      )}

      <div style={{
        padding: '12px 20px 16px', borderTop: '1px solid rgba(255,255,255,0.04)',
        background: 'rgba(3,7,18,0.85)', backdropFilter: 'blur(8px)',
      }}>
        <div style={{
          display: 'flex', alignItems: 'flex-end', gap: 10,
          maxWidth: 800, margin: '0 auto',
          background: 'rgba(26,34,54,0.5)', border: '1px solid rgba(255,255,255,0.06)',
          borderRadius: 18, padding: '10px 16px',
          transition: 'border-color 0.15s ease, box-shadow 0.15s ease',
        }}>
          <textarea
            ref={textareaRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your documents..."
            rows={1}
            disabled={isLoading}
            style={{
              flex: 1, background: 'none', border: 'none', outline: 'none', resize: 'none',
              fontSize: 14, color: '#e5e7eb', lineHeight: 1.6, padding: '2px 0', maxHeight: 160,
              fontFamily: 'inherit',
            }}
            id="chat-input"
          />
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0, paddingBottom: 2 }}>
            {input.length > 0 && (
              <span style={{ fontSize: 10, color: input.length > 1800 ? '#f87171' : '#4b5563', fontVariantNumeric: 'tabular-nums' }}>
                {input.length}/2000
              </span>
            )}
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              style={{
                width: 34, height: 34, borderRadius: 11, border: 'none', cursor: input.trim() && !isLoading ? 'pointer' : 'not-allowed',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: input.trim() && !isLoading ? '#4f46e5' : 'rgba(55,65,81,0.3)',
                color: input.trim() && !isLoading ? '#fff' : '#4b5563',
                transition: 'all 0.15s ease',
              }}
              id="send-btn"
            >
              <Send size={15} />
            </button>
          </div>
        </div>
        <p style={{ textAlign: 'center', fontSize: 10, color: '#374151', marginTop: 8 }}>
          Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
