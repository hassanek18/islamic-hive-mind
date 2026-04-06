"""Verify hadith and dua data integrity in hive-mind.db.

Checks:
  - hadiths table has data
  - Both Shia and Sunni hadiths present
  - All hadiths have grade set (sahih or hasan only)
  - All hadiths have source_book and tradition
  - All hadiths have Arabic or English text
  - duas table has data
  - All duas have name_english, category, attributed_to
  - Breakdown by source_book
  - Breakdown by tradition
"""

import os
import sys
import sqlite3

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'db', 'hive-mind.db')


def verify_hadith_integrity(db_path=DB_PATH):
    """Run all integrity checks on hadiths and duas tables.

    Returns True if all checks pass, False otherwise.
    """
    db_path = os.path.abspath(db_path)

    if not os.path.exists(db_path):
        print(f"  [FAIL] Database not found: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    all_passed = True
    warnings = []

    print("=" * 60)
    print("  Hadith & Dua Integrity Verification")
    print("=" * 60)

    # ── CHECK 1: hadiths table has data ──
    print("\n--- Hadiths Table ---")
    c.execute("SELECT COUNT(*) FROM hadiths")
    total_hadiths = c.fetchone()[0]
    if total_hadiths > 0:
        print(f"  [PASS] Hadiths table has {total_hadiths} records")
    else:
        print(f"  [FAIL] Hadiths table is empty")
        all_passed = False

    # ── CHECK 2: Both traditions present ──
    c.execute("SELECT tradition, COUNT(*) FROM hadiths GROUP BY tradition")
    tradition_counts = dict(c.fetchall())

    sunni_count = tradition_counts.get('sunni', 0)
    shia_count = tradition_counts.get('shia', 0)

    if sunni_count > 0:
        print(f"  [PASS] Sunni hadiths: {sunni_count}")
    else:
        print(f"  [WARN] No Sunni hadiths found")
        warnings.append("No Sunni hadiths")

    if shia_count > 0:
        print(f"  [PASS] Shia hadiths: {shia_count}")
    else:
        print(f"  [WARN] No Shia hadiths found (data may not be downloaded yet)")
        warnings.append("No Shia hadiths")

    # ── CHECK 3: All hadiths have valid grade ──
    c.execute("SELECT COUNT(*) FROM hadiths WHERE grade IS NULL OR grade = ''")
    no_grade = c.fetchone()[0]
    if no_grade == 0:
        print(f"  [PASS] All hadiths have grade set")
    else:
        print(f"  [FAIL] {no_grade} hadiths missing grade")
        all_passed = False

    c.execute("SELECT grade, COUNT(*) FROM hadiths GROUP BY grade")
    grade_counts = dict(c.fetchall())
    valid_grades = {'sahih', 'hasan'}
    invalid_grades = {g: cnt for g, cnt in grade_counts.items() if g not in valid_grades}
    if invalid_grades:
        print(f"  [FAIL] Invalid grades found: {invalid_grades}")
        all_passed = False
    else:
        for grade, cnt in sorted(grade_counts.items()):
            print(f"    Grade '{grade}': {cnt} hadiths")

    # ── CHECK 4: All hadiths have source_book and tradition ──
    c.execute("SELECT COUNT(*) FROM hadiths WHERE source_book IS NULL OR source_book = ''")
    no_book = c.fetchone()[0]
    if no_book == 0:
        print(f"  [PASS] All hadiths have source_book")
    else:
        print(f"  [FAIL] {no_book} hadiths missing source_book")
        all_passed = False

    c.execute("SELECT COUNT(*) FROM hadiths WHERE tradition IS NULL OR tradition = ''")
    no_tradition = c.fetchone()[0]
    if no_tradition == 0:
        print(f"  [PASS] All hadiths have tradition")
    else:
        print(f"  [FAIL] {no_tradition} hadiths missing tradition")
        all_passed = False

    # ── CHECK 5: All hadiths have Arabic or English text ──
    c.execute("""
        SELECT COUNT(*) FROM hadiths
        WHERE (matn_arabic IS NULL OR matn_arabic = '')
          AND (matn_english IS NULL OR matn_english = '')
    """)
    no_text = c.fetchone()[0]
    if no_text == 0:
        print(f"  [PASS] All hadiths have Arabic or English text")
    else:
        print(f"  [FAIL] {no_text} hadiths have neither Arabic nor English text")
        all_passed = False

    # ── CHECK 6: duas table has data ──
    print("\n--- Duas Table ---")
    c.execute("SELECT COUNT(*) FROM duas")
    total_duas = c.fetchone()[0]
    if total_duas > 0:
        print(f"  [PASS] Duas table has {total_duas} records")
    else:
        print(f"  [WARN] Duas table is empty")
        warnings.append("No duas")

    # ── CHECK 7: All duas have required fields ──
    if total_duas > 0:
        c.execute("SELECT COUNT(*) FROM duas WHERE name_english IS NULL OR name_english = ''")
        no_name = c.fetchone()[0]
        if no_name == 0:
            print(f"  [PASS] All duas have name_english")
        else:
            print(f"  [FAIL] {no_name} duas missing name_english")
            all_passed = False

        c.execute("SELECT COUNT(*) FROM duas WHERE category IS NULL OR category = ''")
        no_cat = c.fetchone()[0]
        if no_cat == 0:
            print(f"  [PASS] All duas have category")
        else:
            print(f"  [FAIL] {no_cat} duas missing category")
            all_passed = False

        c.execute("SELECT COUNT(*) FROM duas WHERE attributed_to IS NULL OR attributed_to = ''")
        no_attr = c.fetchone()[0]
        if no_attr == 0:
            print(f"  [PASS] All duas have attributed_to")
        else:
            print(f"  [FAIL] {no_attr} duas missing attributed_to")
            all_passed = False

    # ── BREAKDOWN: by source_book ──
    print("\n--- Breakdown by Source Book ---")
    c.execute("""
        SELECT source_book, tradition, COUNT(*) as cnt
        FROM hadiths
        GROUP BY source_book, tradition
        ORDER BY tradition, cnt DESC
    """)
    for row in c.fetchall():
        print(f"  {row[0]:30s} ({row[1]:5s}): {row[2]:>6d} hadiths")

    # ── BREAKDOWN: by tradition ──
    print("\n--- Breakdown by Tradition ---")
    for tradition, cnt in sorted(tradition_counts.items()):
        pct = (cnt / total_hadiths * 100) if total_hadiths > 0 else 0
        print(f"  {tradition:10s}: {cnt:>6d} ({pct:.1f}%)")
    if total_hadiths > 0:
        print(f"  {'TOTAL':10s}: {total_hadiths:>6d}")

    # ── BREAKDOWN: duas by category ──
    if total_duas > 0:
        print("\n--- Duas by Category ---")
        c.execute("SELECT category, COUNT(*) FROM duas GROUP BY category ORDER BY COUNT(*) DESC")
        for row in c.fetchall():
            print(f"  {row[0]:20s}: {row[1]:>4d}")

        print("\n--- Duas by Source Book ---")
        c.execute("SELECT source_book, COUNT(*) FROM duas GROUP BY source_book ORDER BY COUNT(*) DESC")
        for row in c.fetchall():
            print(f"  {row[0]:25s}: {row[1]:>4d}")

    # ── Summary ──
    print("\n" + "=" * 60)
    if all_passed and not warnings:
        print("  RESULT: ALL CHECKS PASSED")
    elif all_passed and warnings:
        print(f"  RESULT: PASSED WITH {len(warnings)} WARNING(S)")
        for w in warnings:
            print(f"    - {w}")
    else:
        print("  RESULT: SOME CHECKS FAILED")
    print("=" * 60)

    conn.close()
    return all_passed


if __name__ == '__main__':
    passed = verify_hadith_integrity()
    sys.exit(0 if passed else 1)
