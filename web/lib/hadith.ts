import { getDb } from './db';

export interface Hadith {
  id: number;
  source_book: string;
  tradition: string;
  book_chapter: string | null;
  hadith_number: string | null;
  matn_arabic: string | null;
  matn_english: string | null;
  grade: string;
  grade_source: string | null;
}

export interface Dua {
  id: number;
  name_arabic: string;
  name_english: string;
  name_transliteration: string;
  source_book: string;
  text_arabic: string;
  text_english: string | null;
  category: string;
  attributed_to: string;
  occasion: string | null;
}

export async function searchHadithByTopic(topic: string): Promise<Hadith[]> {
  const db = getDb();
  const result = await db.query<Hadith>(
    `SELECT * FROM hadiths WHERE matn_english LIKE ? ORDER BY tradition, source_book LIMIT 10`,
    [`%${topic}%`]
  );
  return result.rows;
}

export async function getDuaByName(name: string): Promise<Dua | null> {
  const db = getDb();
  return db.queryOne<Dua>(
    `SELECT * FROM duas WHERE name_english LIKE ? OR name_transliteration LIKE ?`,
    [`%${name}%`, `%${name}%`]
  );
}

export async function getDuasByOccasion(occasion: string): Promise<Dua[]> {
  const db = getDb();
  const result = await db.query<Dua>(
    `SELECT * FROM duas WHERE occasion LIKE ? ORDER BY name_english`,
    [`%${occasion}%`]
  );
  return result.rows;
}
