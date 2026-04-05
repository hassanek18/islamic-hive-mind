"""Import English translations and transliteration into ayat table."""

import sqlite3
import os
import json
import re

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'hive-mind.db')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'quran')


def clean_html(text):
    """Remove HTML tags from translation text (Quran.com sometimes includes them)."""
    text = re.sub(r'<sup.*?</sup>', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


def import_english(db_path=DB_PATH, data_dir=DATA_DIR):
    translations_file = os.path.join(data_dir, 'translations', 'en-sahih-international.json')
    if not os.path.exists(translations_file):
        print("  [skip] No English translation file found. Run download_translations.py first.")
        return False

    with open(translations_file, 'r', encoding='utf-8') as f:
        verses = json.load(f)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    updated = 0
    for v in verses:
        verse_key = v.get('verse_key', '')
        text = clean_html(v.get('text', ''))
        if ':' in verse_key and text:
            surah, verse = verse_key.split(':')
            c.execute(
                "UPDATE ayat SET text_english = ? WHERE surah_id = ? AND verse_number = ?",
                (text, int(surah), int(verse))
            )
            if c.rowcount > 0:
                updated += 1

    conn.commit()
    c.execute("SELECT COUNT(*) FROM ayat WHERE text_english IS NOT NULL")
    total = c.fetchone()[0]
    conn.close()

    print(f"  Updated {updated} verses with English translation (total with English: {total})")
    return total > 6000


def import_transliteration(db_path=DB_PATH, data_dir=DATA_DIR):
    translit_file = os.path.join(data_dir, 'transliteration', 'transliteration.json')
    if not os.path.exists(translit_file):
        print("  [skip] No transliteration file found. Run download_translations.py first.")
        return False

    with open(translit_file, 'r', encoding='utf-8') as f:
        verses = json.load(f)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    updated = 0
    for v in verses:
        verse_key = v.get('verse_key', '')
        text = clean_html(v.get('text', ''))
        if ':' in verse_key and text:
            surah, verse = verse_key.split(':')
            c.execute(
                "UPDATE ayat SET text_transliteration = ? WHERE surah_id = ? AND verse_number = ?",
                (text, int(surah), int(verse))
            )
            if c.rowcount > 0:
                updated += 1

    conn.commit()
    c.execute("SELECT COUNT(*) FROM ayat WHERE text_transliteration IS NOT NULL")
    total = c.fetchone()[0]
    conn.close()

    print(f"  Updated {updated} verses with transliteration (total: {total})")
    return total > 6000


if __name__ == '__main__':
    print("Importing translations...")
    import_english()
    import_transliteration()
