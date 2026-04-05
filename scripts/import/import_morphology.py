"""Import word-by-word morphological data from the Quranic Arabic Corpus (Leeds).

The corpus file format (tab-separated):
LOCATION\tFORM\tTAG\tFEATURES
(1:1:1:1)\tبِسْمِ\tP\tPREFIX|bi+\nSTEM|POS:P
...

Location format: (chapter:verse:word:segment)
"""

import sqlite3
import os
import re

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'hive-mind.db')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'quran', 'morphology')


# POS tag mapping from corpus tags to readable names
POS_MAP = {
    'N': 'noun', 'PN': 'proper noun', 'ADJ': 'adjective',
    'V': 'verb', 'IMPV': 'imperative verb', 'PV': 'perfect verb', 'IV': 'imperfect verb',
    'P': 'preposition', 'CONJ': 'conjunction', 'DET': 'determiner',
    'REL': 'relative pronoun', 'DEM': 'demonstrative', 'PRON': 'pronoun',
    'NEG': 'negative particle', 'INTG': 'interrogative', 'VOC': 'vocative',
    'INL': 'initials', 'COND': 'conditional', 'SUP': 'supplementary',
    'REM': 'resumption', 'CIRC': 'circumstantial', 'COM': 'comitative',
    'ANS': 'answer', 'AVR': 'aversion', 'CERT': 'certainty',
    'RES': 'restriction', 'INC': 'inceptive', 'SUR': 'surprise',
    'EXP': 'explanation', 'AMD': 'amendment', 'EXH': 'exhortation',
    'EXL': 'exclamation', 'FUT': 'future', 'PREV': 'preventive',
    'ACC': 'accusative', 'T': 'time adverb', 'LOC': 'location adverb',
}


def parse_morphology_file(filepath):
    """Parse the Quranic Arabic Corpus morphology file.

    Returns list of dicts: {surah, verse, word_pos, segment, form, tag, features}
    """
    words = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split('\t')
            if len(parts) < 4:
                continue

            location = parts[0]
            form = parts[1]
            tag = parts[2]
            features = parts[3] if len(parts) > 3 else ''

            # Parse location (chapter:verse:word:segment) — with or without parens
            match = re.match(r'\(?(\d+):(\d+):(\d+):(\d+)\)?', location)
            if not match:
                continue

            surah = int(match.group(1))
            verse = int(match.group(2))
            word_pos = int(match.group(3))
            segment = int(match.group(4))

            # Extract root and lemma from features
            root = ''
            lemma = ''
            for feat in features.split('|'):
                if feat.startswith('ROOT:'):
                    root = feat[5:]
                elif feat.startswith('LEM:'):
                    lemma = feat[4:]

            words.append({
                'surah': surah,
                'verse': verse,
                'word_pos': word_pos,
                'segment': segment,
                'form': form,
                'tag': tag,
                'features': features,
                'root': root,
                'lemma': lemma,
            })

    return words


def import_morphology(db_path=DB_PATH, data_dir=DATA_DIR):
    db_path = os.path.abspath(db_path)
    data_dir = os.path.abspath(data_dir)

    morph_file = os.path.join(data_dir, 'quranic-corpus-morphology.txt')
    if not os.path.exists(morph_file):
        print("  [skip] No morphology file found. Run download_morphology.py first.")
        print("         Or download from https://corpus.quran.com/download/")
        return False

    print("  Parsing morphology file...")
    raw_words = parse_morphology_file(morph_file)
    print(f"  Parsed {len(raw_words)} word segments")

    # Group segments into words (combine segments of the same word)
    word_groups = {}
    for w in raw_words:
        key = (w['surah'], w['verse'], w['word_pos'])
        if key not in word_groups:
            word_groups[key] = {
                'surah': w['surah'],
                'verse': w['verse'],
                'word_pos': w['word_pos'],
                'forms': [],
                'tags': [],
                'roots': [],
                'lemmas': [],
                'features': [],
            }
        word_groups[key]['forms'].append(w['form'])
        word_groups[key]['tags'].append(w['tag'])
        if w['root']:
            word_groups[key]['roots'].append(w['root'])
        if w['lemma']:
            word_groups[key]['lemmas'].append(w['lemma'])
        word_groups[key]['features'].append(w['features'])

    print(f"  Grouped into {len(word_groups)} words")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Clear existing word data
    c.execute("DELETE FROM words")

    inserted = 0
    for key, wg in sorted(word_groups.items()):
        surah, verse, word_pos = key

        # Get ayah_id
        c.execute("SELECT id FROM ayat WHERE surah_id = ? AND verse_number = ?", (surah, verse))
        row = c.fetchone()
        if not row:
            continue
        ayah_id = row[0]

        # Combine word form from segments
        text_arabic = ''.join(wg['forms'])
        # Simple version: strip diacritics (tashkeel)
        text_simple = re.sub(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E8\u06EA-\u06ED]', '', text_arabic)

        # Use the primary (stem) tag and root
        pos = POS_MAP.get(wg['tags'][-1], wg['tags'][-1]) if wg['tags'] else ''
        root = wg['roots'][0] if wg['roots'] else None
        lemma = wg['lemmas'][0] if wg['lemmas'] else None
        morphology = '|'.join(wg['features'])

        c.execute("""
            INSERT INTO words (ayah_id, surah_id, verse_number, word_position,
                              text_arabic, text_simple, root, lemma, part_of_speech, morphology)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ayah_id, surah, verse, word_pos, text_arabic, text_simple,
              root, lemma, pos, morphology))
        inserted += 1

    conn.commit()

    c.execute("SELECT COUNT(*) FROM words")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT root) FROM words WHERE root IS NOT NULL")
    root_count = c.fetchone()[0]
    conn.close()

    print(f"  Inserted {inserted} words (db total: {total})")
    print(f"  Unique roots: {root_count}")
    return total > 50000


if __name__ == '__main__':
    print("Importing morphology data...")
    import_morphology()
