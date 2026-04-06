"""Import Sunni hadith collections into hive-mind.db.

Reads the 6 canonical Sunni collections (Kutub al-Sittah) from
data/hadith/sunni/*.json and inserts them into the hadiths table.

Source format (hadith-json GitHub):
  {"hadiths": [{"id": 1, "idInBook": 1, "chapterId": 1, "bookId": 1,
                "arabic": "...", "english": {"narrator": "...", "text": "..."}}]}

Grading policy:
  - Bukhari & Muslim: grade='sahih' (entire collections accepted as sahih)
  - Abu Dawud, Tirmidhi, Nasa'i, Ibn Majah: grade='hasan' (conservative default)
"""

import os
import sys
import json
import sqlite3

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'db', 'hive-mind.db')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'hadith', 'sunni')

# Mapping: filename slug -> (source_book canonical name, grade)
BOOK_MAP = {
    'bukhari':  ('sahih_bukhari',    'sahih'),
    'muslim':   ('sahih_muslim',     'sahih'),
    'abudawud': ('sunan_abu_dawud',  'hasan'),
    'tirmidhi': ('jami_tirmidhi',    'hasan'),
    'nasai':    ('sunan_nasai',      'hasan'),
    'ibnmajah': ('sunan_ibn_majah',  'hasan'),
}


def import_sunni_hadith(db_path=DB_PATH, data_dir=DATA_DIR):
    """Import all Sunni hadiths into the database.

    Idempotent: clears existing sunni hadiths before importing.
    Returns total number of hadiths imported.
    """
    db_path = os.path.abspath(db_path)
    data_dir = os.path.abspath(data_dir)

    if not os.path.isdir(data_dir):
        print(f"  [skip] Data directory not found: {data_dir}")
        return 0

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Clear existing sunni hadiths (idempotent)
    c.execute("DELETE FROM hadiths WHERE tradition = 'sunni'")
    deleted = c.rowcount
    if deleted > 0:
        print(f"  Cleared {deleted} existing sunni hadiths")

    total_imported = 0

    for slug, (source_book, grade) in BOOK_MAP.items():
        filepath = os.path.join(data_dir, f"{slug}.json")
        if not os.path.exists(filepath):
            print(f"  [skip] {slug}.json not found")
            continue

        print(f"  Importing {slug}...")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        hadiths = data.get('hadiths', [])
        if not hadiths:
            print(f"  [warn] {slug}: no hadiths found in file")
            continue

        # Get chapter info for book_chapter mapping
        chapters = {}
        for ch in data.get('chapters', []):
            chapters[ch.get('id')] = ch.get('arabic', ch.get('english', ''))

        rows = []
        for h in hadiths:
            hadith_id = h.get('id')
            id_in_book = h.get('idInBook')
            chapter_id = h.get('chapterId')
            book_id = h.get('bookId')

            arabic = (h.get('arabic') or '').strip()

            # English may be a dict with narrator+text or a simple string
            eng = h.get('english', {})
            if isinstance(eng, dict):
                narrator = (eng.get('narrator') or '').strip()
                eng_text = (eng.get('text') or '').strip()
                # Combine narrator + text for matn_english
                if narrator and eng_text:
                    matn_english = f"{narrator} {eng_text}"
                else:
                    matn_english = narrator or eng_text
            elif isinstance(eng, str):
                matn_english = eng.strip()
                narrator = ''
            else:
                matn_english = ''
                narrator = ''

            # Skip hadiths with no content at all
            if not arabic and not matn_english:
                continue

            chapter_name = chapters.get(chapter_id, '')

            rows.append((
                source_book,            # source_book
                'sunni',                # tradition
                str(book_id) if book_id else None,  # book_volume
                chapter_name or None,   # book_chapter
                str(id_in_book) if id_in_book is not None else str(hadith_id),  # hadith_number
                None,                   # isnad (not separated in this dataset)
                narrator or None,       # isnad_english (narrator line)
                arabic or None,         # matn_arabic
                matn_english or None,   # matn_english
                grade,                  # grade
                'collection_level',     # grade_source
                None,                   # topics
                None,                   # related_quran_verses
                None,                   # source_url
                str(hadith_id),         # source_id
                None,                   # notes
            ))

        if rows:
            c.executemany("""
                INSERT INTO hadiths (
                    source_book, tradition, book_volume, book_chapter,
                    hadith_number, isnad, isnad_english,
                    matn_arabic, matn_english,
                    grade, grade_source, topics, related_quran_verses,
                    source_url, source_id, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rows)
            conn.commit()

        count = len(rows)
        total_imported += count
        print(f"  [done] {slug}: {count} hadiths imported (grade={grade})")

    conn.close()
    print(f"\n  Total Sunni hadiths imported: {total_imported}")
    return total_imported


if __name__ == '__main__':
    print("=" * 50)
    print("  Importing Sunni Hadith Collections")
    print("=" * 50)
    total = import_sunni_hadith()
    print(f"\nDone. {total} hadiths imported.")
