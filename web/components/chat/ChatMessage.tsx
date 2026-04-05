import type { ChatMessage as ChatMessageType } from '@/types';

export default function ChatMessage({ message }: { message: ChatMessageType }) {
  const isUser = message.role === 'user';
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[85%] rounded-xl px-4 py-3 ${
        isUser ? 'bg-accent-gold/20 border border-accent-gold/30 text-text-primary'
               : 'bg-bg-secondary border border-border-subtle text-text-primary'
      }`}>
        <div className="whitespace-pre-wrap text-sm leading-relaxed">{message.content || '...'}</div>
        {!isUser && message.model && (
          <div className="mt-2 text-xs text-text-secondary">{message.model === 'sonnet' ? 'Sonnet' : 'Haiku'}</div>
        )}
      </div>
    </div>
  );
}
