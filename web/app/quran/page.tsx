import type { Metadata } from 'next';
import { getSurahStats } from '@/lib/quran';
import SurahCard from '@/components/quran/SurahCard';

export const metadata: Metadata = {
  title: 'Browse the Quran',
  description: 'Explore all 114 surahs of the Holy Quran with Arabic text, English translation, and transliteration.',
};

export default async function QuranPage() {
  const surahs = await getSurahStats();

  return (
    <main className="max-w-content mx-auto px-4 py-12">
      <h1 className="text-3xl font-semibold text-text-primary mb-2">The Holy Quran</h1>
      <p className="text-text-secondary mb-8">114 Surahs · 6,236 Ayat · Hafs ʿan ʿAsim</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {surahs.map((surah) => (
          <SurahCard key={surah.id} surah={surah} />
        ))}
      </div>
    </main>
  );
}
