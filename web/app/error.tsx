'use client';

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-primary">
      <div className="text-center max-w-md px-4">
        <h2 className="text-xl font-semibold text-text-primary mb-4">Something went wrong</h2>
        <p className="text-text-secondary mb-6">The Quran data is safe — please refresh the page.</p>
        <button onClick={reset} className="px-6 py-3 bg-accent-gold text-bg-primary rounded-lg font-medium hover:bg-accent-gold-dim transition-colors">
          Try again
        </button>
      </div>
    </div>
  );
}
