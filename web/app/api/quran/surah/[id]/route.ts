import { NextResponse } from 'next/server';
import { getSurah, getSurahVerses } from '@/lib/quran';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const surahId = parseInt(id, 10);

  if (isNaN(surahId) || surahId < 1 || surahId > 114) {
    return NextResponse.json({ error: 'Invalid surah ID. Must be 1-114.' }, { status: 400 });
  }

  const surah = await getSurah(surahId);
  if (!surah) {
    return NextResponse.json({ error: 'Surah not found.' }, { status: 404 });
  }

  const verses = await getSurahVerses(surahId);
  return NextResponse.json({ surah, verses });
}
