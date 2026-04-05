"""Verify Quran database integrity against known statistics."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'hive-mind.db')


def verify(db_path=DB_PATH):
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    results = []

    def check(name, query, expected, tolerance=0):
        c.execute(query)
        actual = c.fetchone()[0]
        if tolerance > 0:
            passed = abs(actual - expected) <= tolerance
        else:
            passed = actual == expected
        status = "PASS" if passed else "FAIL"
        results.append((name, expected, actual, passed))
        print(f"  [{status}] {name}: expected {expected}, got {actual}")
        return passed

    print("\n=== Quran Database Integrity Checks ===\n")

    # Core counts
    check("Total surahs", "SELECT COUNT(*) FROM surahs", 114)
    check("Total ayat", "SELECT COUNT(*) FROM ayat", 6236)

    # Revelation types
    check("Meccan surahs", "SELECT COUNT(*) FROM surahs WHERE revelation_type = 'meccan'", 86)
    check("Medinan surahs", "SELECT COUNT(*) FROM surahs WHERE revelation_type = 'medinan'", 28)

    # Bismillah
    check("Surahs with Bismillah", "SELECT COUNT(*) FROM surahs WHERE bismillah = 1", 113)
    check("Surah 9 no Bismillah", "SELECT bismillah FROM surahs WHERE id = 9", 0)

    # Verse counts for well-known surahs
    check("Al-Fatihah verses", "SELECT verse_count FROM surahs WHERE id = 1", 7)
    check("Al-Baqarah verses", "SELECT verse_count FROM surahs WHERE id = 2", 286)
    check("Al-Ikhlas verses", "SELECT verse_count FROM surahs WHERE id = 112", 4)
    check("An-Nas verses", "SELECT verse_count FROM surahs WHERE id = 114", 6)

    # Arabic text presence
    check("Verses with Arabic text",
          "SELECT COUNT(*) FROM ayat WHERE text_arabic IS NOT NULL AND text_arabic != ''", 6236)

    # English translation
    c.execute("SELECT COUNT(*) FROM ayat WHERE text_english IS NOT NULL AND text_english != ''")
    eng_count = c.fetchone()[0]
    if eng_count > 0:
        check("Verses with English",
              "SELECT COUNT(*) FROM ayat WHERE text_english IS NOT NULL AND text_english != ''",
              6236)
    else:
        print("  [SKIP] English translations not yet imported")

    # Words table
    c.execute("SELECT COUNT(*) FROM words")
    word_count = c.fetchone()[0]
    if word_count > 0:
        check("Total words (approx)", "SELECT COUNT(*) FROM words", 77430, tolerance=2000)
        check("Words have roots",
              "SELECT COUNT(*) FROM words WHERE root IS NOT NULL", 50000, tolerance=10000)
    else:
        print("  [SKIP] Words not yet imported")

    # Letters table
    c.execute("SELECT COUNT(*) FROM letters")
    letter_count = c.fetchone()[0]
    if letter_count > 0:
        check("Total letters (approx)", "SELECT COUNT(*) FROM letters", 323000, tolerance=30000)
    else:
        print("  [SKIP] Letters not yet generated")

    # Abjad values
    check("Abjad reference table", "SELECT COUNT(*) FROM abjad_values", 28)

    # Sajdah verses
    check("Sajdah verses", "SELECT COUNT(*) FROM ayat WHERE sajdah = 1", 15)

    # Juz distribution
    check("Juz range", "SELECT COUNT(DISTINCT juz) FROM ayat WHERE juz IS NOT NULL", 30)

    conn.close()

    # Summary
    passed = sum(1 for _, _, _, p in results if p)
    total = len(results)
    print(f"\n=== Results: {passed}/{total} checks passed ===\n")

    return passed == total


if __name__ == '__main__':
    all_passed = verify()
    exit(0 if all_passed else 1)
