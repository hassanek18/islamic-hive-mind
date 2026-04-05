"""Create the Islamic Hive Mind SQLite database schema."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'hive-mind.db')


def create_schema(db_path=DB_PATH):
    db_path = os.path.abspath(db_path)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Enable WAL mode for better concurrent reads
    c.execute("PRAGMA journal_mode=WAL")

    # --- Surahs ---
    c.execute("""
    CREATE TABLE IF NOT EXISTS surahs (
        id INTEGER PRIMARY KEY,  -- 1-114
        name_arabic TEXT NOT NULL,
        name_english TEXT NOT NULL,
        name_transliteration TEXT NOT NULL,
        revelation_type TEXT NOT NULL,  -- 'meccan' or 'medinan'
        revelation_order INTEGER,
        verse_count INTEGER NOT NULL,
        word_count INTEGER,
        letter_count INTEGER,
        bismillah BOOLEAN DEFAULT 1  -- all except surah 9
    )
    """)

    # --- Ayat (verses) ---
    c.execute("""
    CREATE TABLE IF NOT EXISTS ayat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        surah_id INTEGER REFERENCES surahs(id),
        verse_number INTEGER NOT NULL,
        text_arabic TEXT NOT NULL,          -- Uthmani script
        text_arabic_simple TEXT NOT NULL,   -- simplified, no diacritics
        text_english TEXT,
        text_transliteration TEXT,
        word_count INTEGER,
        letter_count INTEGER,
        letter_count_no_spaces INTEGER,
        abjad_value INTEGER,
        juz INTEGER,
        hizb INTEGER,
        page INTEGER,
        sajdah BOOLEAN DEFAULT 0,
        UNIQUE(surah_id, verse_number)
    )
    """)

    # --- Words ---
    c.execute("""
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ayah_id INTEGER REFERENCES ayat(id),
        surah_id INTEGER,
        verse_number INTEGER,
        word_position INTEGER,  -- 1-based position in verse
        text_arabic TEXT NOT NULL,
        text_simple TEXT NOT NULL,
        text_english TEXT,
        text_transliteration TEXT,
        root TEXT,          -- Arabic 3/4-letter root
        lemma TEXT,
        part_of_speech TEXT,
        morphology TEXT,
        abjad_value INTEGER,
        letter_count INTEGER
    )
    """)

    # --- Letters ---
    c.execute("""
    CREATE TABLE IF NOT EXISTS letters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ayah_id INTEGER REFERENCES ayat(id),
        word_id INTEGER REFERENCES words(id),
        surah_id INTEGER,
        verse_number INTEGER,
        word_position INTEGER,
        letter_position INTEGER,  -- position within word
        letter_arabic TEXT NOT NULL,
        letter_name TEXT,
        abjad_value INTEGER,
        is_sun_letter BOOLEAN,
        is_moon_letter BOOLEAN
    )
    """)

    # --- Abjad values reference ---
    c.execute("""
    CREATE TABLE IF NOT EXISTS abjad_values (
        letter TEXT PRIMARY KEY,
        letter_name TEXT NOT NULL,
        value INTEGER NOT NULL,
        order_position INTEGER NOT NULL
    )
    """)

    # --- Patterns ---
    c.execute("""
    CREATE TABLE IF NOT EXISTS patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        claim TEXT,
        method TEXT,
        result TEXT,
        verified BOOLEAN,
        significance TEXT,
        data TEXT,  -- JSON
        notes TEXT,
        source TEXT,
        discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # --- Analysis runs ---
    c.execute("""
    CREATE TABLE IF NOT EXISTS analysis_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        analysis_type TEXT NOT NULL,
        parameters TEXT,  -- JSON
        results TEXT,     -- JSON
        interesting_findings TEXT,
        run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # --- Indexes ---
    c.execute("CREATE INDEX IF NOT EXISTS idx_ayat_surah ON ayat(surah_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_words_ayah ON words(ayah_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_words_surah ON words(surah_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_words_root ON words(root)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_letters_ayah ON letters(ayah_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_letters_word ON letters(word_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_letters_surah ON letters(surah_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_patterns_category ON patterns(category)")

    # --- Populate Abjad values ---
    abjad_data = [
        ('ا', 'Alif', 1, 1), ('ب', 'Ba', 2, 2), ('ج', 'Jeem', 3, 3),
        ('د', 'Dal', 4, 4), ('ه', 'Ha', 5, 5), ('و', 'Waw', 6, 6),
        ('ز', 'Zayn', 7, 7), ('ح', 'Hha', 8, 8), ('ط', 'Tta', 9, 9),
        ('ي', 'Ya', 10, 10), ('ك', 'Kaf', 20, 11), ('ل', 'Lam', 30, 12),
        ('م', 'Mim', 40, 13), ('ن', 'Nun', 50, 14), ('س', 'Sin', 60, 15),
        ('ع', 'Ayn', 70, 16), ('ف', 'Fa', 80, 17), ('ص', 'Sad', 90, 18),
        ('ق', 'Qaf', 100, 19), ('ر', 'Ra', 200, 20), ('ش', 'Shin', 300, 21),
        ('ت', 'Ta', 400, 22), ('ث', 'Tha', 500, 23), ('خ', 'Kha', 600, 24),
        ('ذ', 'Dhal', 700, 25), ('ض', 'Dad', 800, 26), ('ظ', 'Dha', 900, 27),
        ('غ', 'Ghayn', 1000, 28),
    ]
    c.executemany(
        "INSERT OR IGNORE INTO abjad_values (letter, letter_name, value, order_position) VALUES (?, ?, ?, ?)",
        abjad_data
    )

    conn.commit()
    conn.close()
    print(f"Database created at {db_path}")
    print(f"  Tables: surahs, ayat, words, letters, abjad_values, patterns, analysis_runs")
    print(f"  Abjad values: {len(abjad_data)} letters populated")


if __name__ == '__main__':
    create_schema()
