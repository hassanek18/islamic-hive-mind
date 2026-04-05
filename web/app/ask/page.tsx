'use client';
import ChatPanel from '@/components/chat/ChatPanel';

export default function AskPage() {
  return (
    <main className="max-w-content mx-auto px-4 py-12">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-semibold text-text-primary mb-2">Ask The Scholar</h1>
        <p className="text-text-secondary">Ask questions about the Quran and Islam. Answers are grounded in our verified Quran database.</p>
      </div>
      <ChatPanel isOpen={true} onClose={() => {}} fullPage={true} />
    </main>
  );
}
