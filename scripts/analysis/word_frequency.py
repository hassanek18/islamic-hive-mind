"""Word and root frequency analysis for the Quran.

Verifies known word frequency claims and provides general frequency tools.
"""

import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'hive-mind.db')


def count_word(db_path, word, field='text_simple'):
    """Count occurrences of an exact word match."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f"SELECT COUNT(*) FROM words WHERE {field} = ?", (word,))
    count = c.fetchone()[0]
    conn.close()
    return count


def count_word_contains(db_path, substring, field='text_simple'):
    """Count words containing a substring."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f"SELECT COUNT(*) FROM words WHERE {field} LIKE ?", (f'%{substring}%',))
    count = c.fetchone()[0]
    conn.close()
    return count


def count_root(db_path, root):
    """Count all words derived from a specific root."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM words WHERE root = ?", (root,))
    count = c.fetchone()[0]
    conn.close()
    return count


def get_root_occurrences(db_path, root):
    """Get all occurrences of a root with verse locations."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        SELECT w.surah_id, w.verse_number, w.text_arabic, w.text_simple, w.part_of_speech
        FROM words w WHERE w.root = ?
        ORDER BY w.surah_id, w.verse_number, w.word_position
    """, (root,))
    results = c.fetchall()
    conn.close()
    return results


def top_roots(db_path, limit=50):
    """Get the most frequent roots in the Quran."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        SELECT root, COUNT(*) as cnt
        FROM words WHERE root IS NOT NULL AND root != ''
        GROUP BY root ORDER BY cnt DESC LIMIT ?
    """, (limit,))
    results = c.fetchall()
    conn.close()
    return results


def top_words(db_path, limit=50):
    """Get the most frequent words in the Quran."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        SELECT text_simple, COUNT(*) as cnt
        FROM words WHERE text_simple IS NOT NULL AND text_simple != ''
        GROUP BY text_simple ORDER BY cnt DESC LIMIT ?
    """, (limit,))
    results = c.fetchall()
    conn.close()
    return results


def verify_known_claims(db_path=DB_PATH):
    """Verify well-known word frequency claims about the Quran."""
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print("\n=== Word Frequency Pattern Verification ===\n")

    claims = [
        {
            'name': '"Day" (yawm) appears 365 times',
            'claim': 365,
            'root': 'يوم',
            'notes': 'Counting all forms from root y-w-m',
        },
        {
            'name': '"Month" (shahr) appears 12 times',
            'claim': 12,
            'root': 'شهر',
            'notes': 'Counting all forms from root sh-h-r',
        },
        {
            'name': '"Angels" and "Devils" appear the same count',
            'roots': [('ملك', 'angels'), ('شطن', 'devils')],
            'claim': 'equal',
        },
        {
            'name': '"World" (dunya) and "Hereafter" (akhira) appear equally',
            'roots': [('دنو', 'world/dunya'), ('أخر', 'hereafter/akhira')],
            'claim': 'equal',
        },
    ]

    results = []

    for claim in claims:
        print(f"  Checking: {claim['name']}")

        if 'root' in claim:
            root = claim['root']
            c.execute("SELECT COUNT(*) FROM words WHERE root = ?", (root,))
            count = c.fetchone()[0]
            expected = claim['claim']

            verified = count == expected
            result = {
                'name': claim['name'],
                'root': root,
                'expected': expected,
                'actual': count,
                'verified': verified,
                'significance': 'confirmed' if verified else 'partial',
            }
            status = "CONFIRMED" if verified else f"FOUND {count}"
            print(f"    Root '{root}': {count} occurrences -> {status}")

        elif 'roots' in claim:
            counts = []
            for root, label in claim['roots']:
                c.execute("SELECT COUNT(*) FROM words WHERE root = ?", (root,))
                count = c.fetchone()[0]
                counts.append((root, label, count))
                print(f"    Root '{root}' ({label}): {count}")

            if claim['claim'] == 'equal':
                verified = counts[0][2] == counts[1][2]
                result = {
                    'name': claim['name'],
                    'counts': {label: count for _, label, count in counts},
                    'verified': verified,
                    'significance': 'confirmed' if verified else 'partial',
                }
                status = "EQUAL" if verified else "NOT EQUAL"
                print(f"    -> {status}")

        results.append(result)

        # Store in patterns table
        c.execute("""
            INSERT INTO patterns (name, category, description, claim, method, result, verified, significance, data)
            VALUES (?, 'word_frequency', ?, ?, 'root_count', ?, ?, ?, ?)
        """, (
            claim['name'], claim['name'], str(claim.get('claim', '')),
            json.dumps(result), result['verified'],
            result['significance'], json.dumps(result)
        ))

    conn.commit()
    conn.close()

    confirmed = sum(1 for r in results if r['verified'])
    print(f"\n  Results: {confirmed}/{len(results)} claims confirmed")
    return results


if __name__ == '__main__':
    verify_known_claims()
