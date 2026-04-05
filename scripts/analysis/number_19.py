"""Verify Number 19 patterns in the Quran.

Tests various claims about the significance of the number 19.
"""

import sqlite3
import os
import json
import re

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'hive-mind.db')

TASHKEEL = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E8\u06EA-\u06ED\u0640]')


def count_arabic_letters(text):
    """Count Arabic letters, stripping diacritics."""
    stripped = TASHKEEL.sub('', text)
    count = 0
    for ch in stripped:
        if '\u0600' <= ch <= '\u06FF' and ch not in (' ', '\u0640'):
            count += 1
    return count


def verify_number_19(db_path=DB_PATH):
    """Verify claims related to the number 19 in the Quran."""
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print("\n=== Number 19 Pattern Verification ===\n")

    results = []

    # 1. Bismillah has 19 letters
    bismillah = "بسم الله الرحمن الرحيم"
    letter_count = count_arabic_letters(bismillah)
    check = letter_count == 19
    print(f"  Bismillah letter count: {letter_count} (expected 19) -> {'CONFIRMED' if check else 'NOT CONFIRMED'}")
    results.append({
        'name': 'Bismillah has 19 letters',
        'expected': 19, 'actual': letter_count, 'verified': check,
        'method': 'Letter count of بسم الله الرحمن الرحيم'
    })

    # 2. Total surahs = 114 = 19 × 6
    c.execute("SELECT COUNT(*) FROM surahs")
    surah_count = c.fetchone()[0]
    check = surah_count == 114 and 114 % 19 == 0
    print(f"  Total surahs: {surah_count} = 19 × {surah_count // 19} -> {'CONFIRMED' if check else 'NOT CONFIRMED'}")
    results.append({
        'name': 'Total surahs = 114 = 19 × 6',
        'expected': 114, 'actual': surah_count, 'verified': check,
        'method': 'Count surahs, check divisibility by 19'
    })

    # 3. First revelation (96:1-5) has 19 words
    c.execute("""
        SELECT COUNT(*) FROM words
        WHERE surah_id = 96 AND verse_number BETWEEN 1 AND 5
    """)
    word_count = c.fetchone()[0]
    check = word_count == 19
    print(f"  First revelation (96:1-5) word count: {word_count} (expected 19) -> {'CONFIRMED' if check else f'FOUND {word_count}'}")
    results.append({
        'name': 'First revelation (96:1-5) has 19 words',
        'expected': 19, 'actual': word_count, 'verified': check,
        'method': 'Count words in Surah 96, verses 1-5'
    })

    # 4. Surah 96 (Al-Alaq) has 19 verses
    c.execute("SELECT verse_count FROM surahs WHERE id = 96")
    verse_count = c.fetchone()[0]
    check = verse_count == 19
    print(f"  Surah 96 verse count: {verse_count} (expected 19) -> {'CONFIRMED' if check else 'NOT CONFIRMED'}")
    results.append({
        'name': 'Surah 96 has 19 verses',
        'expected': 19, 'actual': verse_count, 'verified': check,
        'method': 'Count verses in Surah 96'
    })

    # 5. Surah 96 is the 19th from the end (114 - 96 + 1 = 19)
    position_from_end = 114 - 96 + 1
    check = position_from_end == 19
    print(f"  Surah 96 position from end: {position_from_end} (expected 19) -> {'CONFIRMED' if check else 'NOT CONFIRMED'}")
    results.append({
        'name': 'Surah 96 is 19th from end',
        'expected': 19, 'actual': position_from_end, 'verified': check,
        'method': '114 - 96 + 1'
    })

    # 6. Number of surahs from Surah 96 to end = 19
    # Same as above, just stated differently

    # 7. Total verses in Quran: check divisibility by 19
    c.execute("SELECT COUNT(*) FROM ayat")
    total_ayat = c.fetchone()[0]
    divisible = total_ayat % 19 == 0
    print(f"  Total ayat: {total_ayat}, divisible by 19: {divisible} ({total_ayat}/19 = {total_ayat/19:.2f})")
    results.append({
        'name': 'Total ayat divisible by 19',
        'expected': 'divisible', 'actual': total_ayat,
        'verified': divisible,
        'method': f'{total_ayat} % 19 = {total_ayat % 19}'
    })

    # Store all results
    for r in results:
        c.execute("""
            INSERT INTO patterns (name, category, description, claim, method, result,
                                 verified, significance, data)
            VALUES (?, 'number_19', ?, ?, ?, ?, ?, ?, ?)
        """, (
            r['name'], r['name'], str(r['expected']),
            r['method'], json.dumps(r), r['verified'],
            'confirmed' if r['verified'] else 'debunked',
            json.dumps(r)
        ))

    conn.commit()
    conn.close()

    confirmed = sum(1 for r in results if r['verified'])
    print(f"\n  Results: {confirmed}/{len(results)} claims confirmed")
    return results


if __name__ == '__main__':
    verify_number_19()
