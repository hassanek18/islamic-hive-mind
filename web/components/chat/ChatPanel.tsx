'use client';
import { useRef, useEffect } from 'react';
import { useChat } from '@/hooks/useChat';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import SuggestedQuestions from './SuggestedQuestions';
import ChatErrorBoundary from './ChatErrorBoundary';
import LoadingDots from '@/components/ui/LoadingDots';

interface Props { isOpen: boolean; onClose: () => void; fullPage?: boolean; }

export default function ChatPanel({ isOpen, onClose, fullPage = false }: Props) {
  const { messages, isLoading, model, sendMessage, clearChat, toggleModel } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  if (!isOpen && !fullPage) return null;

  const panelClasses = fullPage ? 'w-full max-w-3xl mx-auto' : 'fixed right-0 top-0 h-full w-full sm:w-[480px] z-50';

  return (
    <ChatErrorBoundary>
      {!fullPage && <div className="fixed inset-0 bg-black/50 z-40" onClick={onClose} />}
      <div className={`${panelClasses} bg-bg-chat flex flex-col ${fullPage ? 'min-h-[600px]' : 'h-full'}`}>
        <div className="flex items-center justify-between p-4 border-b border-border-subtle">
          <div>
            <h2 className="text-text-primary font-semibold">The Scholar</h2>
            <p className="text-text-secondary text-xs">Ask me about the Quran and Islam</p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={toggleModel} className="text-xs px-2 py-1 rounded border border-border-subtle text-text-secondary hover:text-accent-gold hover:border-accent-gold/30 transition-colors" title={`Using ${model}. Click to switch.`}>
              {model === 'sonnet' ? 'Sonnet' : 'Haiku'}
            </button>
            <button onClick={clearChat} className="text-xs text-text-secondary hover:text-red-400 transition-colors" title="Clear chat history">Clear</button>
            {!fullPage && <button onClick={onClose} className="text-text-secondary hover:text-text-primary text-lg ml-2">&times;</button>}
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          {messages.length === 0 && <SuggestedQuestions onSelect={sendMessage} />}
          {messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)}
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-bg-secondary border border-border-subtle rounded-xl px-4 py-3"><LoadingDots /></div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <ChatInput onSend={sendMessage} isLoading={isLoading} />
      </div>
    </ChatErrorBoundary>
  );
}
