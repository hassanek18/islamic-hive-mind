import { getDb } from './db';
import type { Surah, Ayah, Word, Pattern, SearchResult, FrequencyResult } from '@/types';

export async function getSurah(id: number): Promise<Surah | null> {
  const db = getDb();
  return db.queryOne<Surah>('SELECT * FROM surahs WHERE id = ?', [id]);
}

export async function getSurahVerses(id: number): Promise<Ayah[]> {
  const db = getDb();
  const result = await db.query<Ayah>(
    'SELECT * FROM ayat WHERE surah_id = ? ORDER BY verse_number', [id]
  );
  return result.rows;
}

export async function getSurahStats(): Promise<Surah[]> {
  const db = getDb();
  const result = await db.query<Surah>('SELECT * FROM surahs ORDER BY id');
  return result.rows;
}

export async function getVerse(surah: number, verse: number): Promise<Ayah | null> {
  const db = getDb();
  return db.queryOne<Ayah>(
    'SELECT * FROM ayat WHERE surah_id = ? AND verse_number = ?', [surah, verse]
  );
}

export async function getVerseWords(surah: number, verse: number): Promise<Word[]> {
  const db = getDb();
  const result = await db.query<Word>(
    'SELECT * FROM words WHERE surah_id = ? AND verse_number = ? ORDER BY word_position',
    [surah, verse]
  );
  return result.rows;
}

export async function searchByRoot(root: string): Promise<SearchResult[]> {
  const db = getDb();
  const result = await db.query<SearchResult>(
    `SELECT w.surah_id, w.verse_number, s.name_english as surah_name_english,
            s.name_arabic as surah_name_arabic, a.text_arabic, a.text_english,
            a.text_transliteration
     FROM words w
     JOIN ayat a ON a.surah_id = w.surah_id AND a.verse_number = w.verse_number
     JOIN surahs s ON s.id = w.surah_id
     WHERE w.root = ?
     GROUP BY w.surah_id, w.verse_number
     ORDER BY w.surah_id, w.verse_number
     LIMIT 20`,
    [root]
  );
  return result.rows;
}

export async function searchByEnglish(query: string): Promise<SearchResult[]> {
  const db = getDb();
  const result = await db.query<SearchResult>(
    `SELECT a.surah_id, a.verse_number, s.name_english as surah_name_english,
            s.name_arabic as surah_name_arabic, a.text_arabic, a.text_english,
            a.text_transliteration
     FROM ayat a
     JOIN surahs s ON s.id = a.surah_id
     WHERE a.text_english LIKE ?
     ORDER BY a.surah_id, a.verse_number
     LIMIT 20`,
    [`%${query}%`]
  );
  return result.rows;
}

export async function getWordFrequency(root: string): Promise<FrequencyResult> {
  const db = getDb();
  const countResult = await db.queryOne<{ count: number }>(
    'SELECT COUNT(*) as count FROM words WHERE root = ?', [root]
  );
  const sampleResult = await db.query<Ayah>(
    `SELECT DISTINCT a.* FROM words w
     JOIN ayat a ON a.id = w.ayah_id
     WHERE w.root = ? LIMIT 5`,
    [root]
  );
  return {
    root,
    count: countResult?.count || 0,
    sample_verses: sampleResult.rows,
  };
}

export async function getPatterns(): Promise<Pattern[]> {
  const db = getDb();
  const result = await db.query<Pattern>('SELECT * FROM patterns ORDER BY category, name');
  return result.rows;
}

export async function getRandomVerse(): Promise<Ayah | null> {
  const db = getDb();
  const CURATED_VERSES = [
    [2, 255], [55, 13], [94, 5], [3, 139], [2, 286],
    [112, 1], [93, 3], [49, 13], [21, 87], [13, 28],
  ];
  const [surah, verse] = CURATED_VERSES[Math.floor(Math.random() * CURATED_VERSES.length)];
  return getVerse(surah, verse);
}
