"""Generate letter-by-letter breakdown from words table.

Breaks every word into individual Arabic letters and populates the letters table.
"""

import sqlite3
import os
import re
import unicodedata

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'hive-mind.db')

# Arabic letters (28 standard + hamza variants + ta marbuta + alif maqsura + alif wasla)
ARABIC_LETTERS = set('ابتثجحخدذرزسشصضطظعغفقكلمنهويءآأؤإئةىٱ')

# Diacritical marks to strip when isolating letters
TASHKEEL = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E8\u06EA-\u06ED]')

# Sun letters (assimilate with definite article ال)
SUN_LETTERS = set('تثدذرزسشصضطظلن')
# Moon letters (don't assimilate)
MOON_LETTERS = set('ابجحخعغفقكمهوي')

# Letter names
LETTER_NAMES = {
    'ا': 'Alif', 'ب': 'Ba', 'ت': 'Ta', 'ث': 'Tha', 'ج': 'Jeem', 'ح': 'Hha',
    'خ': 'Kha', 'د': 'Dal', 'ذ': 'Dhal', 'ر': 'Ra', 'ز': 'Zayn', 'س': 'Sin',
    'ش': 'Shin', 'ص': 'Sad', 'ض': 'Dad', 'ط': 'Tta', 'ظ': 'Dha', 'ع': 'Ayn',
    'غ': 'Ghayn', 'ف': 'Fa', 'ق': 'Qaf', 'ك': 'Kaf', 'ل': 'Lam', 'م': 'Mim',
    'ن': 'Nun', 'ه': 'Ha', 'و': 'Waw', 'ي': 'Ya',
    'ء': 'Hamza', 'آ': 'Alif Madda', 'أ': 'Alif Hamza Above',
    'ؤ': 'Waw Hamza', 'إ': 'Alif Hamza Below', 'ئ': 'Ya Hamza',
    'ة': 'Ta Marbuta', 'ى': 'Alif Maqsura', 'ٱ': 'Alif Wasla',
}


def extract_letters(text):
    """Extract Arabic letters from text, stripping diacritics.

    Includes all 28 standard letters plus: hamza variants, ta marbuta,
    alif maqsura, and alif wasla. Excludes diacritics, spaces, and tatweel.
    """
    stripped = TASHKEEL.sub('', text)
    letters = []
    for ch in stripped:
        if ch in ARABIC_LETTERS:
            letters.append(ch)
    return letters


def generate_letters(db_path=DB_PATH):
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Load Abjad values
    c.execute("SELECT letter, value FROM abjad_values")
    abjad_map = dict(c.fetchall())

    # Map hamza variants to base letter Abjad values
    abjad_map['ء'] = 1   # Hamza → Alif value
    abjad_map['آ'] = 1   # Alif Madda → Alif
    abjad_map['أ'] = 1   # Alif Hamza Above → Alif
    abjad_map['إ'] = 1   # Alif Hamza Below → Alif
    abjad_map['ؤ'] = 6   # Waw Hamza → Waw
    abjad_map['ئ'] = 10  # Ya Hamza → Ya
    abjad_map['ة'] = 5   # Ta Marbuta → Ha value (common convention; some use 400 for Ta)
    abjad_map['ى'] = 10  # Alif Maqsura → Ya value
    abjad_map['ٱ'] = 1   # Alif Wasla → Alif value

    # Clear existing letters
    c.execute("DELETE FROM letters")

    # Process all words
    c.execute("SELECT id, ayah_id, surah_id, verse_number, word_position, text_arabic FROM words")
    words = c.fetchall()

    batch = []
    total = 0

    for word_id, ayah_id, surah_id, verse_number, word_position, text_arabic in words:
        letters = extract_letters(text_arabic)

        for pos, letter in enumerate(letters, 1):
            letter_name = LETTER_NAMES.get(letter, '')
            abjad_val = abjad_map.get(letter)
            is_sun = letter in SUN_LETTERS
            is_moon = letter in MOON_LETTERS

            batch.append((
                ayah_id, word_id, surah_id, verse_number, word_position,
                pos, letter, letter_name, abjad_val, is_sun, is_moon
            ))
            total += 1

        if len(batch) >= 10000:
            c.executemany("""
                INSERT INTO letters (ayah_id, word_id, surah_id, verse_number, word_position,
                                    letter_position, letter_arabic, letter_name, abjad_value,
                                    is_sun_letter, is_moon_letter)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch)
            batch = []

    # Insert remaining
    if batch:
        c.executemany("""
            INSERT INTO letters (ayah_id, word_id, surah_id, verse_number, word_position,
                                letter_position, letter_arabic, letter_name, abjad_value,
                                is_sun_letter, is_moon_letter)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, batch)

    conn.commit()

    c.execute("SELECT COUNT(*) FROM letters")
    db_total = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT letter_arabic) FROM letters")
    unique = c.fetchone()[0]
    conn.close()

    print(f"  Generated {total} letters (db total: {db_total})")
    print(f"  Unique letter forms: {unique}")
    return db_total > 100000


if __name__ == '__main__':
    print("Generating letter-by-letter breakdown...")
    generate_letters()
