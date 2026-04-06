"""Import Shia hadith collections into hive-mind.db.

Reads Al-Kafi and Man La Yahduruh al-Faqih volumes from
data/hadith/shia/*.json (downloaded from ThaqalaynAPI) and inserts
strong-graded hadiths into the hadiths table.

Source format (ThaqalaynAPI, array per volume):
  [{"id": 5, "bookId": "Al-Kafi-Volume-1-Kulayni", "book": "Al-Kāfi",
    "category": "...", "chapter": "...", "arabicText": "...",
    "englishText": "...", "majlisiGrading": "صحيح",
    "thaqalaynSanad": "...", "thaqalaynMatn": "...",
    "gradingsFull": [...], "URL": "...", "volume": 1}]

Grading policy (import ONLY strong hadiths):
  - Include if majlisiGrading contains: صحيح (sahih), حسن (hasan),
    موثق (reliable), قوي (strong)
  - Exclude if contains: ضعيف (weak), مرسل (mursal), مجهول (unknown narrator)
  - Skip if no grading available
"""

import os
import sys
import json
import re
import sqlite3

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'db', 'hive-mind.db')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'hadith', 'shia')

# Arabic grading keywords
STRONG_KEYWORDS = ['صحيح', 'حسن', 'موثق', 'قوي']
WEAK_KEYWORDS = ['ضعيف', 'مرسل', 'مجهول']

# Book name normalization
BOOK_NAME_MAP = {
    'Al-Kāfi': 'al_kafi',
    'Al-Kafi': 'al_kafi',
    "Man Lā Yaḥḍuruh al-Faqīh": 'man_la_yahduruhu',
    "Man La Yahduruh al-Faqih": 'man_la_yahduruhu',
}


def _normalize_book_name(book_name, book_id):
    """Map book display name to canonical source_book value."""
    # Try direct match first
    for key, value in BOOK_NAME_MAP.items():
        if key.lower() in book_name.lower():
            return value

    # Fallback: infer from bookId
    book_id_lower = book_id.lower() if book_id else ''
    if 'kafi' in book_id_lower:
        return 'al_kafi'
    elif 'faqih' in book_id_lower:
        return 'man_la_yahduruhu'

    # Last resort: slugify
    return re.sub(r'[^a-z0-9]+', '_', book_name.lower()).strip('_')


def _classify_grading(majlisi_grading):
    """Classify a majlisiGrading string as 'sahih', 'hasan', or None (skip).

    Returns:
        'sahih' if contains sahih/reliable/strong keywords
        'hasan' if contains hasan keyword
        None if contains weak keywords or no grading
    """
    if not majlisi_grading or not majlisi_grading.strip():
        return None

    grading = majlisi_grading.strip()

    # Check for weak keywords first (exclusion takes priority)
    for weak in WEAK_KEYWORDS:
        if weak in grading:
            return None

    # Check for strong keywords
    if 'صحيح' in grading or 'موثق' in grading or 'قوي' in grading:
        return 'sahih'
    if 'حسن' in grading:
        return 'hasan'

    return None


def import_shia_hadith(db_path=DB_PATH, data_dir=DATA_DIR):
    """Import strong Shia hadiths into the database.

    Idempotent: clears existing shia hadiths before importing.
    Returns total number of hadiths imported.
    """
    db_path = os.path.abspath(db_path)
    data_dir = os.path.abspath(data_dir)

    if not os.path.isdir(data_dir):
        print(f"  [skip] Data directory not found: {data_dir}")
        return 0

    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    if not json_files:
        print(f"  [skip] No JSON files in {data_dir} (data not downloaded yet?)")
        return 0

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Clear existing shia hadiths (idempotent)
    c.execute("DELETE FROM hadiths WHERE tradition = 'shia'")
    deleted = c.rowcount
    if deleted > 0:
        print(f"  Cleared {deleted} existing shia hadiths")

    total_imported = 0
    total_skipped_weak = 0
    total_skipped_no_grade = 0
    total_skipped_no_content = 0

    for filename in sorted(json_files):
        filepath = os.path.join(data_dir, filename)
        print(f"  Processing {filename}...")

        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                hadiths = json.load(f)
            except json.JSONDecodeError as e:
                print(f"  [error] {filename}: invalid JSON - {e}")
                continue

        if not isinstance(hadiths, list):
            print(f"  [warn] {filename}: expected array, got {type(hadiths).__name__}")
            continue

        rows = []
        skipped_weak = 0
        skipped_no_grade = 0
        skipped_no_content = 0

        for h in hadiths:
            # Classify grading
            majlisi_grading = h.get('majlisiGrading', '')
            grade = _classify_grading(majlisi_grading)

            if grade is None:
                if majlisi_grading and majlisi_grading.strip():
                    skipped_weak += 1
                else:
                    skipped_no_grade += 1
                continue

            # Extract text fields
            arabic_text = (h.get('arabicText') or '').strip()
            english_text = (h.get('englishText') or '').strip()
            thaqalayn_matn = (h.get('thaqalaynMatn') or '').strip()
            thaqalayn_sanad = (h.get('thaqalaynSanad') or '').strip()

            # Use thaqalaynMatn if available, else englishText
            matn_english = thaqalayn_matn or english_text

            # Skip hadiths with no content at all
            if not arabic_text and not matn_english:
                skipped_no_content += 1
                continue

            book_name = h.get('book', '')
            book_id = h.get('bookId', '')
            source_book = _normalize_book_name(book_name, book_id)

            volume = h.get('volume')
            category = h.get('category', '')
            chapter = h.get('chapter', '')
            hadith_id = h.get('id')
            url = h.get('URL', '')

            # Build grade_source from grading details
            gradings_full = h.get('gradingsFull', [])
            grade_source_parts = [majlisi_grading]
            if isinstance(gradings_full, list):
                for g in gradings_full:
                    if isinstance(g, dict):
                        grader = g.get('grader', '')
                        grading_text = g.get('grading', '')
                        if grader and grading_text:
                            grade_source_parts.append(f"{grader}: {grading_text}")
            grade_source = '; '.join(filter(None, grade_source_parts))

            rows.append((
                source_book,                # source_book
                'shia',                     # tradition
                str(volume) if volume else None,  # book_volume
                chapter or category or None,      # book_chapter
                str(hadith_id) if hadith_id else None,  # hadith_number
                thaqalayn_sanad or None,    # isnad (Arabic chain)
                None,                       # isnad_english
                arabic_text or None,        # matn_arabic
                matn_english or None,       # matn_english
                grade,                      # grade
                grade_source or 'majlisi',  # grade_source
                category or None,           # topics
                None,                       # related_quran_verses
                url or None,                # source_url
                str(hadith_id) if hadith_id else None,  # source_id
                None,                       # notes
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
        total_skipped_weak += skipped_weak
        total_skipped_no_grade += skipped_no_grade
        total_skipped_no_content += skipped_no_content

        print(f"  [done] {filename}: {count} imported, "
              f"{skipped_weak} weak, {skipped_no_grade} no grade, "
              f"{skipped_no_content} no content")

    conn.close()

    print(f"\n  Total Shia hadiths imported: {total_imported}")
    print(f"  Skipped - weak grading: {total_skipped_weak}")
    print(f"  Skipped - no grading: {total_skipped_no_grade}")
    print(f"  Skipped - no content: {total_skipped_no_content}")
    return total_imported


if __name__ == '__main__':
    print("=" * 50)
    print("  Importing Shia Hadith Collections")
    print("=" * 50)
    total = import_shia_hadith()
    print(f"\nDone. {total} hadiths imported.")
