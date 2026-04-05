import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { getSurah, getSurahVerses, getSurahStats } from '@/lib/quran';
import QuranVerse from '@/components/quran/QuranVerse';

interface Props {
  params: Promise<{ id: string }>;
}

export async function generateStaticParams() {
  const surahs = await getSurahStats();
  return surahs.map((s) => ({ id: String(s.id) }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const surah = await getSurah(parseInt(id, 10));
  if (!surah) return { title: 'Surah Not Found' };

  return {
    title: `Surah ${surah.name_english} (${surah.name_transliteration})`,
    description: `Read Surah ${surah.name_english} — ${surah.verse_count} verses, ${surah.revelation_type}. Full Arabic text with English translation and transliteration.`,
  };
}

export default async function SurahPage({ params }: Props) {
  const { id } = await params;
  const surahId = parseInt(id, 10);
  const surah = await getSurah(surahId);

  if (!surah) notFound();

  const verses = await getSurahVerses(surahId);

  return (
    <main className="max-w-3xl mx-auto px-4 py-12">
      <div className="text-center mb-10">
        <div dir="rtl" className="text-4xl text-white mb-2" style={{ fontFamily: "'Amiri', serif", lineHeight: '2.2em' }}>
          {surah.name_arabic}
        </div>
        <h1 className="text-2xl font-semibold text-text-primary">
          {surah.name_english}
        </h1>
        <p className="text-text-secondary">
          {surah.name_transliteration} · {surah.verse_count} verses ·{' '}
          <span className={surah.revelation_type === 'meccan' ? 'text-teal-400' : 'text-amber-400'}>
            {surah.revelation_type === 'meccan' ? 'Meccan' : 'Medinan'}
          </span>
        </p>
      </div>

      {surah.bismillah && surah.id !== 1 && (
        <div dir="rtl" className="text-center text-2xl text-white mb-8 py-4" style={{ fontFamily: "'Amiri', serif", lineHeight: '2.2em' }}>
          بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ
        </div>
      )}

      <div className="divide-y divide-border-subtle">
        {verses.map((verse) => (
          <QuranVerse key={verse.id} verse={verse} />
        ))}
      </div>
    </main>
  );
}
