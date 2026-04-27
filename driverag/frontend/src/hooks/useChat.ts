import { useState, useCallback, useRef } from 'react';
import type { Message } from '../types';
import { askQuestion } from '../api/client';

function generateId(): string {
  return `msg_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef(false);

  const sendMessage = useCallback(async (query: string) => {
    if (!query.trim() || isLoading) return;

    setError(null);
    abortRef.current = false;

    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: query.trim(),
      timestamp: new Date(),
    };

    const loadingMessage: Message = {
      id: generateId(),
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isLoading: true,
    };

    setMessages((prev) => [...prev, userMessage, loadingMessage]);
    setIsLoading(true);

    try {
      const response = await askQuestion(query.trim());

      if (abortRef.current) return;

      const assistantMessage: Message = {
        id: loadingMessage.id,
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        timestamp: new Date(),
        isLoading: false,
      };

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === loadingMessage.id ? assistantMessage : msg
        )
      );
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to get answer';
      setError(errorMsg);

      const errorMessage: Message = {
        id: loadingMessage.id,
        role: 'assistant',
        content: `Error: ${errorMsg}`,
        timestamp: new Date(),
        isLoading: false,
      };

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === loadingMessage.id ? errorMessage : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const retryLast = useCallback(() => {
    const lastUserMsg = [...messages].reverse().find((m) => m.role === 'user');
    if (lastUserMsg) {
      setMessages((prev) => prev.slice(0, -1));
      sendMessage(lastUserMsg.content);
    }
  }, [messages, sendMessage]);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    retryLast,
  };
}
