"""Calculate Abjad (gematria) values at word, verse, and surah levels."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'hive-mind.db')


def calculate_abjad(db_path=DB_PATH):
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 1. Update word-level Abjad values (sum of letter values per word)
    print("  Calculating word-level Abjad values...")
    c.execute("""
        UPDATE words SET abjad_value = (
            SELECT COALESCE(SUM(l.abjad_value), 0)
            FROM letters l WHERE l.word_id = words.id
        )
    """)
    word_count = c.rowcount
    print(f"    Updated {word_count} words")

    # 2. Update word-level letter counts
    c.execute("""
        UPDATE words SET letter_count = (
            SELECT COUNT(*)
            FROM letters l WHERE l.word_id = words.id
        )
    """)

    # 3. Update verse-level Abjad values (sum of word values per verse)
    print("  Calculating verse-level Abjad values...")
    c.execute("""
        UPDATE ayat SET abjad_value = (
            SELECT COALESCE(SUM(w.abjad_value), 0)
            FROM words w WHERE w.ayah_id = ayat.id
        )
    """)
    verse_count = c.rowcount
    print(f"    Updated {verse_count} verses")

    conn.commit()

    # Verify some values
    c.execute("SELECT COUNT(*) FROM words WHERE abjad_value > 0")
    words_with_val = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ayat WHERE abjad_value > 0")
    verses_with_val = c.fetchone()[0]
    c.execute("SELECT SUM(abjad_value) FROM ayat")
    total_abjad = c.fetchone()[0]

    conn.close()

    print(f"  Words with Abjad values: {words_with_val}")
    print(f"  Verses with Abjad values: {verses_with_val}")
    print(f"  Total Quran Abjad value: {total_abjad}")
    return words_with_val > 0


if __name__ == '__main__':
    print("Calculating Abjad values...")
    calculate_abjad()
