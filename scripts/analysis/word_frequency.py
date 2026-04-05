"""Word and root frequency analysis for the Quran.

Provides both ROOT-BASED counting (all derivatives) and SURFACE-FORM counting
(specific word forms). This distinction is critical for verifying word frequency
claims, which typically count specific forms, not all root derivatives.

Methodology note: Popular claims like "day appears 365 times" count specific
singular noun forms, NOT all words derived from the same root. These claims
are modern (post-1970s) and are not found in classical tafsir literature.
They should be treated as popular claims being tested, not established facts.
"""

import sqlite3
import os
import json
import re

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'hive-mind.db')

# Diacritics regex for stripping tashkeel when comparing surface forms
TASHKEEL = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E8\u06EA-\u06ED\u0640]')


def strip_tashkeel(text):
    """Remove diacritical marks from Arabic text for comparison."""
    return TASHKEEL.sub('', text)


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


def count_surface_forms(db_path, forms, field='text_arabic'):
    """Count occurrences of specific surface forms (with tashkeel stripped).

    This is the correct method for testing claims like "day = 365" which
    count specific word forms, not all root derivatives.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    total = 0
    form_counts = {}
    for form in forms:
        stripped = strip_tashkeel(form)
        # Match against stripped version of the stored text
        c.execute("SELECT text_arabic FROM words")
        # More efficient: compare stripped forms
        c.execute(f"SELECT COUNT(*) FROM words WHERE text_simple LIKE ?", (stripped,))
        count = c.fetchone()[0]
        form_counts[form] = count
        total += count

    conn.close()
    return total, form_counts


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
    """Verify well-known word frequency claims about the Quran.

    Tests both ROOT-BASED and SURFACE-FORM counting to show why results differ.
    Popular claims typically use surface-form counting with contested inclusion criteria.
    """
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Clear old word_frequency patterns
    c.execute("DELETE FROM patterns WHERE category = 'word_frequency'")

    print("\n=== Word Frequency Pattern Verification ===")
    print("  Note: Popular claims (modern, not from classical tafsir)")
    print("  Testing both root-based and surface-form counting\n")

    claims = [
        {
            'name': '"Day" (yawm) appears 365 times',
            'claim': 365,
            'root': 'يوم',
            'surface_forms': ['يوم', 'يوما', 'يومهم', 'يومكم', 'يومئذ'],
            'singular_forms': ['يوم', 'يوما'],
            'notes': 'Popular claim counts singular yawm only. Root count includes all derivatives (ayyam, yawmayn, etc.)',
            'scholarly_consensus': 'popular_claim_unverified',
        },
        {
            'name': '"Month" (shahr) appears 12 times',
            'claim': 12,
            'root': 'شهر',
            'surface_forms': ['شهر', 'شهرا'],
            'singular_forms': ['شهر', 'شهرا'],
            'notes': 'Popular claim counts singular shahr only. Root includes ashur (months), etc.',
            'scholarly_consensus': 'popular_claim_unverified',
        },
        {
            'name': '"Life" (hayat) and "Death" (mawt) appear equally',
            'roots': [('حيي', 'life/hayat'), ('موت', 'death/mawt')],
            'claim': 'equal',
            'scholarly_consensus': 'popular_claim_unverified',
        },
        {
            'name': '"Angels" and "Devils" appear the same count',
            'roots': [('ملك', 'angels/malaika'), ('شطن', 'devils/shayatin')],
            'claim': 'equal',
            'notes': 'Root m-l-k also includes "king/malik" — not just angels. This makes the comparison unreliable at root level.',
            'scholarly_consensus': 'popular_claim_unverified',
        },
        {
            'name': '"World" (dunya) and "Hereafter" (akhira) appear equally',
            'roots': [('دنو', 'world/dunya'), ('أخر', 'hereafter/akhira')],
            'claim': 'equal',
            'notes': 'Root a-kh-r includes "other/another" — not just "hereafter." Root d-n-w includes "near/approach."',
            'scholarly_consensus': 'popular_claim_unverified',
        },
    ]

    results = []

    for claim in claims:
        print(f"  Checking: {claim['name']}")

        if 'root' in claim and 'roots' not in claim:
            root = claim['root']

            # Root-based count (all derivatives)
            c.execute("SELECT COUNT(*) FROM words WHERE root = ?", (root,))
            root_count = c.fetchone()[0]

            # Surface-form count (specific forms matching the claim)
            surface_count = 0
            form_details = {}
            for form in claim.get('singular_forms', []):
                stripped = strip_tashkeel(form)
                c.execute("SELECT COUNT(*) FROM words WHERE text_simple = ?", (stripped,))
                fc = c.fetchone()[0]
                form_details[form] = fc
                surface_count += fc

            # Also try LIKE match for forms that might have attached particles
            c.execute("SELECT COUNT(*) FROM words WHERE text_simple LIKE ?",
                      (strip_tashkeel(claim['singular_forms'][0]) + '%',))
            like_count = c.fetchone()[0]

            expected = claim['claim']
            verified_root = root_count == expected
            verified_surface = surface_count == expected

            result = {
                'name': claim['name'],
                'root': root,
                'expected': expected,
                'root_count': root_count,
                'surface_form_count': surface_count,
                'starts_with_count': like_count,
                'form_details': form_details,
                'verified_root': verified_root,
                'verified_surface': verified_surface,
                'verified': verified_root or verified_surface,
                'significance': 'confirmed' if (verified_root or verified_surface) else 'needs_investigation',
                'scholarly_consensus': claim.get('scholarly_consensus', 'unknown'),
            }

            print(f"    Root '{root}' (all forms): {root_count}")
            print(f"    Singular forms {claim.get('singular_forms', [])}: {surface_count}")
            print(f"    Starts with '{claim['singular_forms'][0]}': {like_count}")
            if form_details:
                for f, fc in form_details.items():
                    print(f"      '{f}': {fc}")
            print(f"    Expected: {expected} -> {'MATCH FOUND' if result['verified'] else 'NO MATCH'}")

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
                    'significance': 'confirmed' if verified else 'needs_investigation',
                    'scholarly_consensus': claim.get('scholarly_consensus', 'unknown'),
                    'notes': claim.get('notes', ''),
                }
                status = "EQUAL" if verified else "NOT EQUAL"
                print(f"    -> {status}")

        results.append(result)

        # Store in patterns table
        c.execute("""
            INSERT INTO patterns (name, category, description, claim, method, result, verified, significance, data)
            VALUES (?, 'word_frequency', ?, ?, 'root_and_surface_form', ?, ?, ?, ?)
        """, (
            claim['name'], claim['name'] + ' | ' + claim.get('notes', ''),
            str(claim.get('claim', '')),
            json.dumps(result, ensure_ascii=False), result['verified'],
            result['significance'], json.dumps(result, ensure_ascii=False)
        ))

    conn.commit()
    conn.close()

    confirmed = sum(1 for r in results if r['verified'])
    print(f"\n  Results: {confirmed}/{len(results)} claims confirmed")
    print("  Note: All claims are modern (post-1970s) and not from classical tafsir.")
    print("  Discrepancies are expected due to contested counting methodology.")
    return results


if __name__ == '__main__':
    verify_known_claims()
