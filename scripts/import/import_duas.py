"""Import duas into hive-mind.db.

Reads processed dua JSON files from data/duas/mafatih/ and data/duas/sahifa/
and inserts them into the duas table.

Source format (our processed format from download_duas.py):
  {"name_arabic": "...", "name_english": "...", "text_arabic": "...",
   "text_english": "...", "category": "mafatih", "attributed_to": "imam_ali",
   "occasion": "thursday_night", "source_url": "...",
   "source_book": "Mafatih al-Jinan"}

Also imports from data/duas/all/ which uses the raw duas.org API format:
  {"id": "...", "title": "...", "duas": [{"type": "dua", "segments": [...]}]}
"""

import os
import sys
import json
import sqlite3

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'db', 'hive-mind.db')
MAFATIH_DIR = os.path.join(PROJECT_ROOT, 'data', 'duas', 'mafatih')
SAHIFA_DIR = os.path.join(PROJECT_ROOT, 'data', 'duas', 'sahifa')
ALL_DIR = os.path.join(PROJECT_ROOT, 'data', 'duas', 'all')

# Source book name normalization
SOURCE_BOOK_MAP = {
    'Mafatih al-Jinan': 'mafatih_al_jinan',
    'mafatih al-jinan': 'mafatih_al_jinan',
    'Sahifa al-Sajjadiya': 'sahifa_al_sajjadiya',
    'sahifa al-sajjadiya': 'sahifa_al_sajjadiya',
}


def _normalize_source_book(source_book):
    """Normalize source book name to canonical form."""
    if not source_book:
        return 'unknown'
    for key, value in SOURCE_BOOK_MAP.items():
        if key.lower() == source_book.lower():
            return value
    # Fallback: slugify
    import re
    return re.sub(r'[^a-z0-9]+', '_', source_book.lower()).strip('_') or 'unknown'


def _import_processed_dua(filepath, conn, source_label):
    """Import a single dua from our processed format (mafatih/sahifa dirs).

    Returns 1 if imported, 0 if skipped.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"    [error] {os.path.basename(filepath)}: {e}")
        return 0

    if not isinstance(data, dict):
        return 0

    # Check for required text content
    text_arabic = (data.get('text_arabic') or '').strip()
    text_english = (data.get('text_english') or '').strip()

    if not text_arabic and not text_english:
        print(f"    [skip] {os.path.basename(filepath)}: no text content")
        return 0

    name_arabic = (data.get('name_arabic') or '').strip()
    name_english = (data.get('name_english') or '').strip()
    name_transliteration = (data.get('text_transliteration', '') or '').strip()[:200] if data.get('name_transliteration') is None else (data.get('name_transliteration') or '').strip()

    # name_english is required by schema
    if not name_english:
        # Try to derive from filename
        name_english = os.path.splitext(os.path.basename(filepath))[0].replace('-', ' ').replace('_', ' ').title()

    # name_arabic: use placeholder if missing (NOT NULL constraint)
    if not name_arabic:
        name_arabic = name_english

    # name_transliteration: use placeholder if missing (NOT NULL constraint)
    if not name_transliteration:
        name_transliteration = name_english

    category = (data.get('category') or source_label).strip()
    attributed_to = (data.get('attributed_to') or 'unknown').strip()
    occasion = (data.get('occasion') or '').strip()
    source_url = (data.get('source_url') or '').strip()
    source_book_raw = (data.get('source_book') or '').strip()
    source_book = _normalize_source_book(source_book_raw)

    text_transliteration = (data.get('text_transliteration') or '').strip()

    c = conn.cursor()
    c.execute("""
        INSERT INTO duas (
            name_arabic, name_english, name_transliteration,
            source_book, text_arabic, text_english, text_transliteration,
            category, attributed_to, occasion,
            source_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name_arabic,
        name_english,
        name_transliteration,
        source_book,
        text_arabic or '',  # NOT NULL column - use empty string if no Arabic
        text_english or None,
        text_transliteration or None,
        category,
        attributed_to,
        occasion or None,
        source_url or None,
    ))
    return 1


def _import_raw_api_dua(filepath, conn):
    """Import a single dua from the raw duas.org API format (all/ dir).

    Returns 1 if imported, 0 if skipped.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"    [error] {os.path.basename(filepath)}: {e}")
        return 0

    if not isinstance(data, dict):
        return 0

    # Extract text from segments across all dua blocks
    all_arabic = []
    all_english = []
    all_transliteration = []

    for dua_block in data.get('duas', []):
        if not isinstance(dua_block, dict):
            continue
        for seg in dua_block.get('segments', []):
            if not isinstance(seg, dict):
                continue
            ar = (seg.get('arabic') or '').strip()
            en = (seg.get('translation') or '').strip()
            tr = (seg.get('transliteration') or '').strip()
            if ar:
                all_arabic.append(ar)
            if en:
                all_english.append(en)
            if tr:
                all_transliteration.append(tr)

    text_arabic = '\n'.join(all_arabic)
    text_english = '\n'.join(all_english)
    text_transliteration = '\n'.join(all_transliteration)

    if not text_arabic and not text_english:
        return 0

    dua_id = data.get('id', '')
    title = data.get('title', '')
    name_english = title or dua_id.replace('-', ' ').title()
    name_arabic = name_english  # Arabic name not available in this format
    name_transliteration = name_english

    # Try to extract attribution from index metadata
    index_meta = data.get('_index_meta', {})
    category = 'dua'
    attributed_to = 'unknown'
    source_url = f"https://www.duas.org/{dua_id}.html" if dua_id else ''

    # Infer attribution and category from content/title
    title_lower = title.lower() if title else ''
    if 'ziyarat' in title_lower:
        category = 'ziyarat'
    elif 'salat' in title_lower or 'salaat' in title_lower:
        category = 'salat'
    elif 'amaal' in title_lower:
        category = 'amaal'

    if 'imam hussain' in title_lower or 'imam husain' in title_lower:
        attributed_to = 'imam_hussein'
    elif 'imam mahdi' in title_lower:
        attributed_to = 'imam_mahdi'
    elif 'imam sajjad' in title_lower or 'sajjadiya' in title_lower:
        attributed_to = 'imam_sajjad'
    elif 'imam baqir' in title_lower:
        attributed_to = 'imam_baqir'
    elif 'imam sadiq' in title_lower:
        attributed_to = 'imam_sadiq'
    elif 'holy prophet' in title_lower or 'prophet' in title_lower:
        attributed_to = 'prophet'

    # Infer occasion from title
    occasion = ''
    if 'ramadan' in title_lower:
        occasion = 'ramadan'
    elif 'shaban' in title_lower or 'shaaban' in title_lower:
        occasion = 'shaban'
    elif 'rajab' in title_lower:
        occasion = 'rajab'

    c = conn.cursor()
    c.execute("""
        INSERT INTO duas (
            name_arabic, name_english, name_transliteration,
            source_book, text_arabic, text_english, text_transliteration,
            category, attributed_to, occasion,
            source_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name_arabic,
        name_english,
        name_transliteration,
        'duas_org',
        text_arabic or '',  # NOT NULL column - use empty string if no Arabic
        text_english or None,
        text_transliteration or None,
        category,
        attributed_to,
        occasion or None,
        source_url or None,
    ))
    return 1


def import_duas(db_path=DB_PATH, mafatih_dir=MAFATIH_DIR,
                sahifa_dir=SAHIFA_DIR, all_dir=ALL_DIR):
    """Import all duas into the database.

    Idempotent: clears existing duas before importing.
    Returns total number of duas imported.
    """
    db_path = os.path.abspath(db_path)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Clear existing duas (idempotent)
    c.execute("DELETE FROM duas")
    deleted = c.rowcount
    if deleted > 0:
        print(f"  Cleared {deleted} existing duas")

    total_imported = 0

    # Track imported IDs to avoid duplicates between mafatih/ and all/
    imported_names = set()

    # ── Import from mafatih/ ──
    mafatih_dir = os.path.abspath(mafatih_dir)
    if os.path.isdir(mafatih_dir):
        print(f"\n  === Mafatih al-Jinan ({mafatih_dir}) ===")
        files = sorted([f for f in os.listdir(mafatih_dir) if f.endswith('.json')])
        count = 0
        for filename in files:
            filepath = os.path.join(mafatih_dir, filename)
            result = _import_processed_dua(filepath, conn, 'mafatih')
            if result:
                count += 1
                imported_names.add(os.path.splitext(filename)[0])
        conn.commit()
        total_imported += count
        print(f"  [done] Mafatih: {count}/{len(files)} duas imported")
    else:
        print(f"  [skip] Mafatih directory not found: {mafatih_dir}")

    # ── Import from sahifa/ ──
    sahifa_dir = os.path.abspath(sahifa_dir)
    if os.path.isdir(sahifa_dir):
        print(f"\n  === Sahifa al-Sajjadiya ({sahifa_dir}) ===")
        files = sorted([f for f in os.listdir(sahifa_dir) if f.endswith('.json')])
        count = 0
        for filename in files:
            filepath = os.path.join(sahifa_dir, filename)
            result = _import_processed_dua(filepath, conn, 'sahifa')
            if result:
                count += 1
                imported_names.add(os.path.splitext(filename)[0])
        conn.commit()
        total_imported += count
        print(f"  [done] Sahifa: {count}/{len(files)} duas imported")
    else:
        print(f"  [skip] Sahifa directory not found: {sahifa_dir}")

    # ── Import from all/ (raw API format, skip duplicates) ──
    all_dir = os.path.abspath(all_dir)
    if os.path.isdir(all_dir):
        print(f"\n  === All Available Duas ({all_dir}) ===")
        files = sorted([f for f in os.listdir(all_dir) if f.endswith('.json')])
        count = 0
        skipped_dup = 0
        for filename in files:
            base = os.path.splitext(filename)[0]
            # Skip if already imported from mafatih/ or sahifa/
            # Check for slug overlap (e.g., "dua-kumayl" vs "kumayl")
            if base in imported_names:
                skipped_dup += 1
                continue
            # Also check if the slug minus common prefixes matches
            stripped = base
            for prefix in ['dua-', 'ziyarat-', 'salat-', 'ramadan-']:
                if stripped.startswith(prefix):
                    stripped_check = stripped[len(prefix):]
                    if stripped_check in imported_names:
                        skipped_dup += 1
                        stripped = None
                        break
            if stripped is None:
                continue

            filepath = os.path.join(all_dir, filename)
            result = _import_raw_api_dua(filepath, conn)
            if result:
                count += 1
                imported_names.add(base)
        conn.commit()
        total_imported += count
        print(f"  [done] All: {count}/{len(files)} duas imported ({skipped_dup} duplicates skipped)")
    else:
        print(f"  [skip] All directory not found: {all_dir}")

    conn.close()
    print(f"\n  Total duas imported: {total_imported}")
    return total_imported


if __name__ == '__main__':
    print("=" * 50)
    print("  Importing Duas")
    print("=" * 50)
    total = import_duas()
    print(f"\nDone. {total} duas imported.")
