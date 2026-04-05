import { NextResponse } from 'next/server';
import { searchByRoot, searchByEnglish } from '@/lib/quran';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.get('q');
  const type = searchParams.get('type') || 'english';

  if (!query || query.trim().length === 0) {
    return NextResponse.json({ error: 'Query parameter "q" is required.' }, { status: 400 });
  }

  let results;
  if (type === 'root') {
    results = await searchByRoot(query.trim());
  } else {
    results = await searchByEnglish(query.trim());
  }

  return NextResponse.json({ results, count: results.length });
}
