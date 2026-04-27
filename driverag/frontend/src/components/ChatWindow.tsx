import { useEffect, useRef } from 'react';
import type { Message } from '../types';
import MessageBubble from './MessageBubble';

interface ChatWindowProps {
  messages: Message[];
  onRetry?: () => void;
}

export default function ChatWindow({ messages, onRetry }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div
      style={{
        flex: 1, overflowY: 'auto', padding: '24px 28px',
        display: 'flex', flexDirection: 'column', gap: 24,
      }}
      id="chat-window"
    >
      {messages.map((msg, i) => (
        <MessageBubble
          key={msg.id}
          message={msg}
          onRetry={msg.content.startsWith('Error:') && i === messages.length - 1 ? onRetry : undefined}
        />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
