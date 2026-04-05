'use client';
import { useState, useRef, type KeyboardEvent } from 'react';

export default function ChatInput({ onSend, isLoading }: { onSend: (msg: string) => void; isLoading: boolean }) {
  const [input, setInput] = useState('');
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setInput('');
    inputRef.current?.focus();
  };

  return (
    <div className="flex gap-2 p-4 border-t border-border-subtle">
      <textarea ref={inputRef} value={input} onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e: KeyboardEvent<HTMLTextAreaElement>) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
        placeholder="Ask about the Quran..." rows={1}
        className="flex-1 bg-bg-primary border border-border-subtle rounded-lg px-4 py-3 text-text-primary text-sm resize-none focus:outline-none focus:border-accent-gold/50 placeholder:text-text-secondary"
        disabled={isLoading} />
      <button onClick={handleSend} disabled={isLoading || !input.trim()}
        className="px-4 py-3 bg-accent-gold text-bg-primary rounded-lg font-medium text-sm hover:bg-accent-gold-dim transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
        Send
      </button>
    </div>
  );
}
