import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Ask The Scholar',
  description: 'Ask questions about the Quran and Islam. Powered by AI, grounded in the Quran database.',
};

export default function AskLayout({ children }: { children: React.ReactNode }) {
  return children;
}
