import Link from 'next/link';
import type { Surah } from '@/types';

interface SurahCardProps {
  surah: Surah;
}

export default function SurahCard({ surah }: SurahCardProps) {
  return (
    <Link href={`/quran/${surah.id}`}>
      <div className="bg-bg-secondary border border-border-subtle rounded-xl p-6 hover:border-accent-gold/30 transition-colors cursor-pointer group">
        <div className="flex items-start justify-between mb-3">
          <span className="inline-flex items-center justify-center w-8 h-8 rounded-full border border-accent-gold/40 text-accent-gold text-xs font-mono">
            {surah.id}
          </span>
          <span className={`text-xs px-2 py-1 rounded-full ${
            surah.revelation_type === 'meccan'
              ? 'bg-teal-900/30 text-teal-400'
              : 'bg-amber-900/30 text-amber-400'
          }`}>
            {surah.revelation_type === 'meccan' ? 'Meccan' : 'Medinan'}
          </span>
        </div>

        <div dir="rtl" className="text-right text-xl text-white mb-1" style={{ fontFamily: "'Amiri', serif" }}>
          {surah.name_arabic}
        </div>

        <h3 className="text-text-primary font-semibold group-hover:text-accent-gold transition-colors">
          {surah.name_english}
        </h3>
        <p className="text-text-secondary text-sm">{surah.name_transliteration}</p>

        <p className="text-text-secondary text-xs mt-3">
          {surah.verse_count} verses
        </p>
      </div>
    </Link>
  );
}
