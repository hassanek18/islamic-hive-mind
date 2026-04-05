"""Calculate word and letter count statistics at verse and surah levels."""

import sqlite3
import os
import re

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'hive-mind.db')

TASHKEEL = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E8\u06EA-\u06ED\u0640]')


def count_arabic_letters(text):
    """Count Arabic letters in text (excluding diacritics and spaces)."""
    stripped = TASHKEEL.sub('', text)
    count = 0
    for ch in stripped:
        if '\u0600' <= ch <= '\u06FF' and ch != '\u0640':  # Arabic range, exclude tatweel
            count += 1
    return count


def calculate_statistics(db_path=DB_PATH):
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 1. Update verse-level word counts from words table
    print("  Calculating verse-level word counts...")
    c.execute("""
        UPDATE ayat SET word_count = (
            SELECT COUNT(*) FROM words w WHERE w.ayah_id = ayat.id
        )
    """)

    # 2. Update verse-level letter counts from letters table
    print("  Calculating verse-level letter counts...")
    c.execute("""
        UPDATE ayat SET letter_count = (
            SELECT COUNT(*) FROM letters l WHERE l.ayah_id = ayat.id
        )
    """)

    # 3. Calculate letter_count_no_spaces from the Arabic text directly
    print("  Calculating letter counts (no spaces)...")
    c.execute("SELECT id, text_arabic_simple FROM ayat")
    rows = c.fetchall()
    for ayah_id, text in rows:
        if text:
            count = count_arabic_letters(text)
            c.execute("UPDATE ayat SET letter_count_no_spaces = ? WHERE id = ?", (count, ayah_id))

    # 4. Update surah-level statistics
    print("  Calculating surah-level statistics...")
    c.execute("""
        UPDATE surahs SET word_count = (
            SELECT COALESCE(SUM(a.word_count), 0)
            FROM ayat a WHERE a.surah_id = surahs.id
        )
    """)
    c.execute("""
        UPDATE surahs SET letter_count = (
            SELECT COALESCE(SUM(a.letter_count), 0)
            FROM ayat a WHERE a.surah_id = surahs.id
        )
    """)

    conn.commit()

    # Report
    c.execute("SELECT SUM(word_count) FROM surahs")
    total_words = c.fetchone()[0]
    c.execute("SELECT SUM(letter_count) FROM surahs")
    total_letters = c.fetchone()[0]
    c.execute("SELECT SUM(verse_count) FROM surahs")
    total_verses = c.fetchone()[0]

    conn.close()

    print(f"  Total verses: {total_verses}")
    print(f"  Total words: {total_words}")
    print(f"  Total letters: {total_letters}")
    return total_words is not None and total_words > 0


if __name__ == '__main__':
    print("Calculating statistics...")
    calculate_statistics()
