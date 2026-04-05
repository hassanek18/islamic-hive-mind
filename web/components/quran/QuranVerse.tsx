import type { Ayah } from '@/types';

interface QuranVerseProps {
  verse: Ayah;
  showVerseNumber?: boolean;
  surahName?: string;
}

export default function QuranVerse({ verse, showVerseNumber = true, surahName }: QuranVerseProps) {
  return (
    <div className="py-6 border-b border-border-subtle last:border-b-0">
      {showVerseNumber && (
        <div className="flex justify-center mb-4">
          <span className="inline-flex items-center justify-center w-10 h-10 rounded-full border-2 border-accent-gold text-accent-gold text-sm font-mono">
            {verse.verse_number}
          </span>
        </div>
      )}

      <div dir="rtl" className="arabic-text text-center text-2xl md:text-3xl text-white mb-4 px-4 leading-[2.2em]" style={{ fontFamily: "'Amiri', serif" }}>
        {verse.text_arabic}
      </div>

      {verse.text_transliteration && (
        <p className="text-center text-sm text-text-secondary italic mb-2 px-4">
          {verse.text_transliteration}
        </p>
      )}

      {verse.text_english && (
        <p className="text-center text-text-primary px-4 max-w-3xl mx-auto">
          {verse.text_english}
        </p>
      )}

      {surahName && (
        <p className="text-center text-xs text-text-secondary mt-2">
          {surahName} ({verse.surah_id}:{verse.verse_number})
        </p>
      )}
    </div>
  );
}
