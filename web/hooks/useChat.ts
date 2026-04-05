'use client';
import { useState, useCallback, useRef, useEffect } from 'react';
import type { ChatMessage } from '@/types';

const STORAGE_KEY = 'islamic-hive-mind-chat';

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2);
}

function loadMessages(): ChatMessage[] {
  if (typeof window === 'undefined') return [];
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch { return []; }
}

function saveMessages(messages: ChatMessage[]) {
  if (typeof window === 'undefined') return;
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(messages)); } catch {}
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [model, setModel] = useState<'haiku' | 'sonnet'>('haiku');
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => { setMessages(loadMessages()); }, []);
  useEffect(() => { if (messages.length > 0) saveMessages(messages); }, [messages]);

  const sendMessage = useCallback(async (content: string) => {
    const userMessage: ChatMessage = { id: generateId(), role: 'user', content, timestamp: Date.now() };
    const assistantMessage: ChatMessage = { id: generateId(), role: 'assistant', content: '', timestamp: Date.now(), model };

    setMessages(prev => [...prev, userMessage, assistantMessage]);
    setIsLoading(true);

    try {
      abortRef.current = new AbortController();
      const allMessages = [...messages, userMessage];
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: allMessages, model }),
        signal: abortRef.current.signal,
      });

      if (!response.ok) throw new Error(`Chat API error: ${response.status}`);
      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let accumulated = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          try {
            const data = JSON.parse(line.slice(6));
            if (data.type === 'text') {
              accumulated += data.text;
              setMessages(prev => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last.role === 'assistant') last.content = accumulated;
                return updated;
              });
            } else if (data.type === 'error') {
              accumulated += `\n\n*Error: ${data.message}*`;
              setMessages(prev => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last.role === 'assistant') last.content = accumulated;
                return updated;
              });
            }
          } catch {}
        }
      }
    } catch (error: unknown) {
      if (error instanceof Error && error.name !== 'AbortError') {
        setMessages(prev => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last.role === 'assistant') last.content = 'I encountered an error. Please try again.';
          return updated;
        });
      }
    } finally { setIsLoading(false); }
  }, [messages, model]);

  const clearChat = useCallback(() => { setMessages([]); localStorage.removeItem(STORAGE_KEY); }, []);
  const toggleModel = useCallback(() => { setModel(prev => prev === 'haiku' ? 'sonnet' : 'haiku'); }, []);

  return { messages, isLoading, model, sendMessage, clearChat, toggleModel };
}
