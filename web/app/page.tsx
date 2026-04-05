import { getRandomVerse, getSurah } from '@/lib/quran';
import QuranVerse from '@/components/quran/QuranVerse';
import Button from '@/components/ui/Button';

export default async function HomePage() {
  const verse = await getRandomVerse();
  const surah = verse ? await getSurah(verse.surah_id) : null;

  return (
    <main>
      <section className="py-20 md:py-32 text-center px-4">
        <div dir="rtl" className="text-3xl md:text-5xl text-white mb-4" style={{ fontFamily: "'Amiri', serif", lineHeight: '2.2em' }}>
          الخلية الإسلامية
        </div>
        <h1 className="text-3xl md:text-5xl font-bold text-text-primary mb-4">
          Islamic Hive Mind
        </h1>
        <p className="text-text-secondary text-lg mb-8 max-w-xl mx-auto">
          A living Islamic knowledge base — explore the Quran, discover its depth, ask a scholar.
        </p>
        <div className="flex gap-4 justify-center flex-wrap">
          <Button href="/ask">Ask The Scholar</Button>
          <Button href="/quran" variant="secondary">Explore the Quran</Button>
        </div>
      </section>

      {verse && surah && (
        <section className="max-w-3xl mx-auto px-4 pb-20">
          <div className="bg-bg-secondary border border-border-subtle rounded-xl p-8">
            <QuranVerse verse={verse} surahName={surah.name_english} showVerseNumber={false} />
          </div>
        </section>
      )}
    </main>
  );
}
