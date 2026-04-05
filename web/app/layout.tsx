import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import FloatingChatButton from '@/components/chat/FloatingChatButton';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export const metadata: Metadata = {
  title: {
    default: 'Islamic Hive Mind — A Living Islamic Knowledge Base',
    template: '%s | Islamic Hive Mind',
  },
  description: 'Explore the Quran with full Arabic text, English translation, word-by-word analysis, and an AI-powered Islamic scholar.',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    siteName: 'Islamic Hive Mind',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <head>
        <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap" rel="stylesheet" />
      </head>
      <body className="bg-bg-primary text-text-primary min-h-screen">
        <Header />
        {children}
        <Footer />
        <FloatingChatButton />
      </body>
    </html>
  );
}
