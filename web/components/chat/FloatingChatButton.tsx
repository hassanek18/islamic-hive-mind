'use client';
import { useState } from 'react';
import ChatPanel from './ChatPanel';

export default function FloatingChatButton() {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <>
      <ChatPanel isOpen={isOpen} onClose={() => setIsOpen(false)} />
      {!isOpen && (
        <button onClick={() => setIsOpen(true)} className="fixed bottom-6 right-6 z-30 w-14 h-14 bg-accent-gold rounded-full shadow-lg shadow-accent-gold/20 flex items-center justify-center hover:bg-accent-gold-dim transition-colors" title="Ask The Scholar">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#0a0e1a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-6 h-6">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </button>
      )}
    </>
  );
}
