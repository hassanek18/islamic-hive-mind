import { NextResponse } from 'next/server';
import { getVerse, getVerseWords, getSurah } from '@/lib/quran';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ surah: string; verse: string }> }
) {
  const { surah: surahStr, verse: verseStr } = await params;
  const surahId = parseInt(surahStr, 10);
  const verseNum = parseInt(verseStr, 10);

  if (isNaN(surahId) || isNaN(verseNum)) {
    return NextResponse.json({ error: 'Invalid surah or verse number.' }, { status: 400 });
  }

  const surah = await getSurah(surahId);
  if (!surah) {
    return NextResponse.json({ error: 'Surah not found.' }, { status: 404 });
  }

  if (verseNum < 1 || verseNum > surah.verse_count) {
    return NextResponse.json({
      error: `Verse ${verseNum} does not exist in Surah ${surah.name_english}. This surah has ${surah.verse_count} verses.`
    }, { status: 404 });
  }

  const verse = await getVerse(surahId, verseNum);
  const words = await getVerseWords(surahId, verseNum);
  return NextResponse.json({ surah, verse, words });
}
