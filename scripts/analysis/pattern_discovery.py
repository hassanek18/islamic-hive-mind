"""Pattern discovery engine — search for new numerical patterns in the Quran.

Includes: divisibility scanner, symmetry detector, and sequence finder.
"""

import sqlite3
import os
import json
import math

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'hive-mind.db')

SIGNIFICANT_NUMBERS = [7, 19, 29, 114]


def divisibility_scan(db_path=DB_PATH):
    """Check various Quran counts for divisibility by significant numbers."""
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print("\n=== Divisibility Scanner ===\n")

    findings = []

    # Check surah-level counts
    c.execute("SELECT id, name_english, verse_count, word_count, letter_count FROM surahs")
    surahs = c.fetchall()

    for surah_id, name, verses, words, letters in surahs:
        for n in SIGNIFICANT_NUMBERS:
            if verses and verses % n == 0:
                findings.append({
                    'type': 'surah_verses_divisible',
                    'surah': surah_id, 'name': name,
                    'count': verses, 'divisor': n,
                    'desc': f"Surah {surah_id} ({name}): {verses} verses divisible by {n}"
                })
            if words and words % n == 0:
                findings.append({
                    'type': 'surah_words_divisible',
                    'surah': surah_id, 'name': name,
                    'count': words, 'divisor': n,
                    'desc': f"Surah {surah_id} ({name}): {words} words divisible by {n}"
                })

    # Check totals
    c.execute("SELECT SUM(verse_count), SUM(word_count), SUM(letter_count) FROM surahs")
    total_v, total_w, total_l = c.fetchone()

    for label, total in [('total_verses', total_v), ('total_words', total_w), ('total_letters', total_l)]:
        if total:
            for n in SIGNIFICANT_NUMBERS:
                if total % n == 0:
                    findings.append({
                        'type': f'{label}_divisible',
                        'count': total, 'divisor': n,
                        'desc': f"Quran {label}: {total} divisible by {n} = {total // n}"
                    })

    # Print top findings
    for f in findings[:20]:
        print(f"  {f['desc']}")

    if len(findings) > 20:
        print(f"  ... and {len(findings) - 20} more findings")

    # Store analysis run
    c.execute("""
        INSERT INTO analysis_runs (analysis_type, parameters, results, interesting_findings)
        VALUES ('divisibility_scan', ?, ?, ?)
    """, (
        json.dumps({'numbers': SIGNIFICANT_NUMBERS}),
        json.dumps(findings),
        f"{len(findings)} divisibility patterns found"
    ))
    conn.commit()
    conn.close()

    print(f"\n  Total findings: {len(findings)}")
    return findings


def symmetry_analysis(db_path=DB_PATH):
    """Analyze symmetry between first and second halves of the Quran."""
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print("\n=== Symmetry Analysis ===\n")

    findings = []

    # First half (surahs 1-57) vs second half (58-114)
    for half_label, start, end in [('first_half', 1, 57), ('second_half', 58, 114)]:
        c.execute("SELECT SUM(verse_count), SUM(word_count), SUM(letter_count) FROM surahs WHERE id BETWEEN ? AND ?",
                  (start, end))
        row = c.fetchone()
        findings.append({
            'half': half_label, 'surahs': f'{start}-{end}',
            'verses': row[0], 'words': row[1], 'letters': row[2]
        })

    if len(findings) == 2:
        f1, f2 = findings
        print(f"  First half  (1-57):  {f1['verses']} verses, {f1['words']} words, {f1['letters']} letters")
        print(f"  Second half (58-114): {f2['verses']} verses, {f2['words']} words, {f2['letters']} letters")

        if f1['verses'] and f2['verses']:
            ratio_v = f1['verses'] / f2['verses']
            ratio_w = f1['words'] / f2['words'] if f2['words'] else 0
            print(f"  Verse ratio: {ratio_v:.4f}")
            print(f"  Word ratio: {ratio_w:.4f}")
            print(f"  Golden ratio (phi): {(1 + math.sqrt(5)) / 2:.4f}")

    # Midpoint analysis (surah 57 is Al-Hadid = The Iron, atomic number 26)
    c.execute("SELECT name_english, verse_count FROM surahs WHERE id = 57")
    mid = c.fetchone()
    print(f"\n  Middle surah (57): {mid[0]} ({mid[1]} verses)")
    print(f"  Note: 57 = 19 × 3, and Iron's atomic number is 26")

    # Surah number + verse count sums
    c.execute("SELECT id, verse_count FROM surahs")
    surahs = c.fetchall()
    total_sum = sum(s_id + vc for s_id, vc in surahs)
    print(f"\n  Sum of (surah_number + verse_count) for all surahs: {total_sum}")
    for n in SIGNIFICANT_NUMBERS:
        if total_sum % n == 0:
            print(f"    Divisible by {n}: {total_sum // n}")

    c.execute("""
        INSERT INTO analysis_runs (analysis_type, parameters, results, interesting_findings)
        VALUES ('symmetry_analysis', '{}', ?, ?)
    """, (json.dumps(findings), f"Symmetry analysis of first/second half"))
    conn.commit()
    conn.close()

    return findings


def prime_analysis(db_path=DB_PATH):
    """Analyze prime number patterns in surah verse counts."""
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print("\n=== Prime Number Analysis ===\n")

    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

    c.execute("SELECT id, name_english, verse_count FROM surahs")
    surahs = c.fetchall()

    prime_surahs = [(s_id, name, vc) for s_id, name, vc in surahs if is_prime(vc)]
    prime_numbered = [(s_id, name, vc) for s_id, name, vc in surahs if is_prime(s_id)]

    print(f"  Surahs with prime verse counts: {len(prime_surahs)}")
    for s_id, name, vc in prime_surahs[:10]:
        print(f"    Surah {s_id} ({name}): {vc} verses")
    if len(prime_surahs) > 10:
        print(f"    ... and {len(prime_surahs) - 10} more")

    print(f"\n  Prime-numbered surahs: {len(prime_numbered)}")

    c.execute("""
        INSERT INTO analysis_runs (analysis_type, parameters, results, interesting_findings)
        VALUES ('prime_analysis', '{}', ?, ?)
    """, (
        json.dumps({
            'prime_verse_count_surahs': [(s, n, v) for s, n, v in prime_surahs],
            'prime_numbered_surahs': len(prime_numbered)
        }),
        f"{len(prime_surahs)} surahs with prime verse counts"
    ))
    conn.commit()
    conn.close()

    return prime_surahs


def run_all_discovery(db_path=DB_PATH):
    """Run all pattern discovery tools."""
    print("=" * 60)
    print("  Pattern Discovery Engine")
    print("=" * 60)

    divisibility_scan(db_path)
    symmetry_analysis(db_path)
    prime_analysis(db_path)

    print("\n" + "=" * 60)
    print("  Discovery complete")
    print("=" * 60)


if __name__ == '__main__':
    run_all_discovery()
