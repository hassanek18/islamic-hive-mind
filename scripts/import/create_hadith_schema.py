"""Add hadith, duas, and narrators tables to hive-mind.db."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'hive-mind.db')


def create_hadith_schema(db_path=DB_PATH):
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS hadiths (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_book TEXT NOT NULL,
        tradition TEXT NOT NULL,
        book_volume TEXT,
        book_chapter TEXT,
        hadith_number TEXT,
        isnad TEXT,
        isnad_english TEXT,
        matn_arabic TEXT,
        matn_english TEXT,
        grade TEXT NOT NULL,
        grade_source TEXT,
        topics TEXT,
        related_quran_verses TEXT,
        source_url TEXT,
        source_id TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS duas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name_arabic TEXT NOT NULL,
        name_english TEXT NOT NULL,
        name_transliteration TEXT NOT NULL,
        source_book TEXT NOT NULL DEFAULT 'mafatih_al_jinan',
        text_arabic TEXT NOT NULL,
        text_english TEXT,
        text_transliteration TEXT,
        category TEXT NOT NULL,
        attributed_to TEXT NOT NULL,
        occasion TEXT,
        day_specific TEXT,
        prescribed_for TEXT,
        quran_verses_referenced TEXT,
        source_url TEXT,
        hadith_grade TEXT,
        section_in_source TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS narrators (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name_arabic TEXT NOT NULL,
        name_english TEXT,
        birth_year_hijri INTEGER,
        death_year_hijri INTEGER,
        reliability TEXT,
        tradition TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("CREATE INDEX IF NOT EXISTS idx_hadiths_book ON hadiths(source_book)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_hadiths_tradition ON hadiths(tradition)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_hadiths_grade ON hadiths(grade)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_duas_category ON duas(category)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_duas_attributed ON duas(attributed_to)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_duas_occasion ON duas(occasion)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_narrators_reliability ON narrators(reliability)")

    conn.commit()
    conn.close()
    print(f"Hadith schema created at {db_path}")
    print(f"  Tables: hadiths, duas, narrators")


if __name__ == '__main__':
    create_hadith_schema()
