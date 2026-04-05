"""Import Quran Arabic text from Tanzil.net data files into the database.

Handles both XML and TXT formats. Populates surahs and ayat tables.
"""

import sqlite3
import os
import re

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'hive-mind.db')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'quran')

# Surah metadata: (name_arabic, name_english, name_transliteration, revelation_type, revelation_order, verse_count, bismillah)
SURAH_META = [
    ("الفاتحة", "The Opening", "Al-Fatihah", "meccan", 5, 7, True),
    ("البقرة", "The Cow", "Al-Baqarah", "medinan", 87, 286, True),
    ("آل عمران", "The Family of Imran", "Ali 'Imran", "medinan", 89, 200, True),
    ("النساء", "The Women", "An-Nisa", "medinan", 92, 176, True),
    ("المائدة", "The Table Spread", "Al-Ma'idah", "medinan", 112, 120, True),
    ("الأنعام", "The Cattle", "Al-An'am", "meccan", 55, 165, True),
    ("الأعراف", "The Heights", "Al-A'raf", "meccan", 39, 206, True),
    ("الأنفال", "The Spoils of War", "Al-Anfal", "medinan", 88, 75, True),
    ("التوبة", "The Repentance", "At-Tawbah", "medinan", 113, 129, False),
    ("يونس", "Jonah", "Yunus", "meccan", 51, 109, True),
    ("هود", "Hud", "Hud", "meccan", 52, 123, True),
    ("يوسف", "Joseph", "Yusuf", "meccan", 53, 111, True),
    ("الرعد", "The Thunder", "Ar-Ra'd", "medinan", 96, 43, True),
    ("إبراهيم", "Abraham", "Ibrahim", "meccan", 72, 52, True),
    ("الحجر", "The Rocky Tract", "Al-Hijr", "meccan", 54, 99, True),
    ("النحل", "The Bee", "An-Nahl", "meccan", 70, 128, True),
    ("الإسراء", "The Night Journey", "Al-Isra", "meccan", 50, 111, True),
    ("الكهف", "The Cave", "Al-Kahf", "meccan", 69, 110, True),
    ("مريم", "Mary", "Maryam", "meccan", 44, 98, True),
    ("طه", "Ta-Ha", "Ta-Ha", "meccan", 45, 135, True),
    ("الأنبياء", "The Prophets", "Al-Anbiya", "meccan", 73, 112, True),
    ("الحج", "The Pilgrimage", "Al-Hajj", "medinan", 103, 78, True),
    ("المؤمنون", "The Believers", "Al-Mu'minun", "meccan", 74, 118, True),
    ("النور", "The Light", "An-Nur", "medinan", 102, 64, True),
    ("الفرقان", "The Criterion", "Al-Furqan", "meccan", 42, 77, True),
    ("الشعراء", "The Poets", "Ash-Shu'ara", "meccan", 47, 227, True),
    ("النمل", "The Ant", "An-Naml", "meccan", 48, 93, True),
    ("القصص", "The Stories", "Al-Qasas", "meccan", 49, 88, True),
    ("العنكبوت", "The Spider", "Al-Ankabut", "meccan", 85, 69, True),
    ("الروم", "The Romans", "Ar-Rum", "meccan", 84, 60, True),
    ("لقمان", "Luqman", "Luqman", "meccan", 57, 34, True),
    ("السجدة", "The Prostration", "As-Sajdah", "meccan", 75, 30, True),
    ("الأحزاب", "The Combined Forces", "Al-Ahzab", "medinan", 90, 73, True),
    ("سبأ", "Sheba", "Saba", "meccan", 58, 54, True),
    ("فاطر", "Originator", "Fatir", "meccan", 43, 45, True),
    ("يس", "Ya-Sin", "Ya-Sin", "meccan", 41, 83, True),
    ("الصافات", "Those Lined Up", "As-Saffat", "meccan", 56, 182, True),
    ("ص", "Sad", "Sad", "meccan", 38, 88, True),
    ("الزمر", "The Troops", "Az-Zumar", "meccan", 59, 75, True),
    ("غافر", "The Forgiver", "Ghafir", "meccan", 60, 85, True),
    ("فصلت", "Explained in Detail", "Fussilat", "meccan", 61, 54, True),
    ("الشورى", "The Consultation", "Ash-Shura", "meccan", 62, 53, True),
    ("الزخرف", "The Ornaments of Gold", "Az-Zukhruf", "meccan", 63, 89, True),
    ("الدخان", "The Smoke", "Ad-Dukhan", "meccan", 64, 59, True),
    ("الجاثية", "The Crouching", "Al-Jathiyah", "meccan", 65, 37, True),
    ("الأحقاف", "The Wind-Curved Sandhills", "Al-Ahqaf", "meccan", 66, 35, True),
    ("محمد", "Muhammad", "Muhammad", "medinan", 95, 38, True),
    ("الفتح", "The Victory", "Al-Fath", "medinan", 111, 29, True),
    ("الحجرات", "The Rooms", "Al-Hujurat", "medinan", 106, 18, True),
    ("ق", "Qaf", "Qaf", "meccan", 34, 45, True),
    ("الذاريات", "The Winnowing Winds", "Adh-Dhariyat", "meccan", 67, 60, True),
    ("الطور", "The Mount", "At-Tur", "meccan", 76, 49, True),
    ("النجم", "The Star", "An-Najm", "meccan", 23, 62, True),
    ("القمر", "The Moon", "Al-Qamar", "meccan", 37, 55, True),
    ("الرحمن", "The Beneficent", "Ar-Rahman", "medinan", 97, 78, True),
    ("الواقعة", "The Inevitable", "Al-Waqi'ah", "meccan", 46, 96, True),
    ("الحديد", "The Iron", "Al-Hadid", "medinan", 94, 29, True),
    ("المجادلة", "The Pleading Woman", "Al-Mujadila", "medinan", 105, 22, True),
    ("الحشر", "The Exile", "Al-Hashr", "medinan", 101, 24, True),
    ("الممتحنة", "She That is to be Examined", "Al-Mumtahanah", "medinan", 91, 13, True),
    ("الصف", "The Ranks", "As-Saff", "medinan", 109, 14, True),
    ("الجمعة", "Friday", "Al-Jumu'ah", "medinan", 110, 11, True),
    ("المنافقون", "The Hypocrites", "Al-Munafiqun", "medinan", 104, 11, True),
    ("التغابن", "The Mutual Disillusion", "At-Taghabun", "medinan", 108, 18, True),
    ("الطلاق", "The Divorce", "At-Talaq", "medinan", 99, 12, True),
    ("التحريم", "The Prohibition", "At-Tahrim", "medinan", 107, 12, True),
    ("الملك", "The Sovereignty", "Al-Mulk", "meccan", 77, 30, True),
    ("القلم", "The Pen", "Al-Qalam", "meccan", 2, 52, True),
    ("الحاقة", "The Reality", "Al-Haqqah", "meccan", 78, 52, True),
    ("المعارج", "The Ascending Stairways", "Al-Ma'arij", "meccan", 79, 44, True),
    ("نوح", "Noah", "Nuh", "meccan", 71, 28, True),
    ("الجن", "The Jinn", "Al-Jinn", "meccan", 40, 28, True),
    ("المزمل", "The Enshrouded One", "Al-Muzzammil", "meccan", 3, 20, True),
    ("المدثر", "The Cloaked One", "Al-Muddathir", "meccan", 4, 56, True),
    ("القيامة", "The Resurrection", "Al-Qiyamah", "meccan", 31, 40, True),
    ("الإنسان", "The Human", "Al-Insan", "medinan", 98, 31, True),
    ("المرسلات", "The Emissaries", "Al-Mursalat", "meccan", 33, 50, True),
    ("النبأ", "The Tidings", "An-Naba", "meccan", 80, 40, True),
    ("النازعات", "Those Who Drag Forth", "An-Nazi'at", "meccan", 81, 46, True),
    ("عبس", "He Frowned", "Abasa", "meccan", 24, 42, True),
    ("التكوير", "The Overthrowing", "At-Takwir", "meccan", 7, 29, True),
    ("الانفطار", "The Cleaving", "Al-Infitar", "meccan", 82, 19, True),
    ("المطففين", "The Defrauding", "Al-Mutaffifin", "meccan", 86, 36, True),
    ("الانشقاق", "The Sundering", "Al-Inshiqaq", "meccan", 83, 25, True),
    ("البروج", "The Mansions of the Stars", "Al-Buruj", "meccan", 27, 22, True),
    ("الطارق", "The Morning Star", "At-Tariq", "meccan", 36, 17, True),
    ("الأعلى", "The Most High", "Al-A'la", "meccan", 8, 19, True),
    ("الغاشية", "The Overwhelming", "Al-Ghashiyah", "meccan", 68, 26, True),
    ("الفجر", "The Dawn", "Al-Fajr", "meccan", 10, 30, True),
    ("البلد", "The City", "Al-Balad", "meccan", 35, 20, True),
    ("الشمس", "The Sun", "Ash-Shams", "meccan", 26, 15, True),
    ("الليل", "The Night", "Al-Layl", "meccan", 9, 21, True),
    ("الضحى", "The Morning Hours", "Ad-Duhaa", "meccan", 11, 11, True),
    ("الشرح", "The Relief", "Ash-Sharh", "meccan", 12, 8, True),
    ("التين", "The Fig", "At-Tin", "meccan", 28, 8, True),
    ("العلق", "The Clot", "Al-Alaq", "meccan", 1, 19, True),
    ("القدر", "The Power", "Al-Qadr", "meccan", 25, 5, True),
    ("البينة", "The Clear Proof", "Al-Bayyinah", "medinan", 100, 8, True),
    ("الزلزلة", "The Earthquake", "Az-Zalzalah", "medinan", 93, 8, True),
    ("العاديات", "The Coursers", "Al-Adiyat", "meccan", 14, 11, True),
    ("القارعة", "The Calamity", "Al-Qari'ah", "meccan", 30, 11, True),
    ("التكاثر", "The Rivalry in World Increase", "At-Takathur", "meccan", 16, 8, True),
    ("العصر", "The Declining Day", "Al-Asr", "meccan", 13, 3, True),
    ("الهمزة", "The Traducer", "Al-Humazah", "meccan", 32, 9, True),
    ("الفيل", "The Elephant", "Al-Fil", "meccan", 19, 5, True),
    ("قريش", "Quraysh", "Quraysh", "meccan", 29, 4, True),
    ("الماعون", "The Small Kindnesses", "Al-Ma'un", "meccan", 17, 7, True),
    ("الكوثر", "The Abundance", "Al-Kawthar", "meccan", 15, 3, True),
    ("الكافرون", "The Disbelievers", "Al-Kafirun", "meccan", 18, 6, True),
    ("النصر", "The Divine Support", "An-Nasr", "medinan", 114, 3, True),
    ("المسد", "The Palm Fiber", "Al-Masad", "meccan", 6, 5, True),
    ("الإخلاص", "The Sincerity", "Al-Ikhlas", "meccan", 22, 4, True),
    ("الفلق", "The Daybreak", "Al-Falaq", "meccan", 20, 5, True),
    ("الناس", "Mankind", "An-Nas", "meccan", 21, 6, True),
]

# Sajdah verses (surah:verse)
SAJDAH_VERSES = [
    (7, 206), (13, 15), (16, 50), (17, 109), (19, 58), (22, 18), (22, 77),
    (25, 60), (27, 26), (32, 15), (38, 24), (41, 38), (53, 62), (84, 21), (96, 19),
]

# Juz boundaries (surah, verse) for start of each juz
JUZ_STARTS = [
    (1, 1), (2, 142), (2, 253), (3, 93), (4, 24), (4, 148), (5, 82),
    (6, 111), (7, 88), (8, 41), (9, 93), (11, 6), (12, 53), (15, 1),
    (17, 1), (18, 75), (21, 1), (23, 1), (25, 21), (27, 56), (29, 46),
    (33, 31), (36, 28), (39, 32), (41, 47), (46, 1), (51, 31), (58, 1),
    (67, 1), (78, 1),
]


def get_juz(surah, verse):
    """Determine which juz a verse belongs to."""
    for i in range(len(JUZ_STARTS) - 1, -1, -1):
        js, jv = JUZ_STARTS[i]
        if surah > js or (surah == js and verse >= jv):
            return i + 1
    return 1


def parse_tanzil_txt(filepath):
    """Parse Tanzil text format: surah|verse|text per line."""
    verses = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('|', 2)
            if len(parts) == 3:
                surah = int(parts[0])
                verse = int(parts[1])
                text = parts[2]
                verses[(surah, verse)] = text
    return verses


def parse_tanzil_xml(filepath):
    """Parse Tanzil XML format."""
    try:
        from lxml import etree
        tree = etree.parse(filepath)
        root = tree.getroot()

        verses = {}
        for sura in root.findall('.//sura'):
            surah_num = int(sura.get('index'))
            for aya in sura.findall('aya'):
                verse_num = int(aya.get('index'))
                text = aya.get('text', '')
                verses[(surah_num, verse_num)] = text
        return verses
    except Exception:
        return {}


def import_quran_arabic(db_path=DB_PATH, data_dir=DATA_DIR):
    db_path = os.path.abspath(db_path)
    data_dir = os.path.abspath(data_dir)

    # Try to load text data - prefer TXT format, fall back to XML
    uthmani_verses = {}
    simple_verses = {}

    for ext in ['txt', 'xml']:
        uthmani_file = os.path.join(data_dir, f'quran-uthmani.{ext}')
        if os.path.exists(uthmani_file) and not uthmani_verses:
            parser = parse_tanzil_txt if ext == 'txt' else parse_tanzil_xml
            uthmani_verses = parser(uthmani_file)
            if uthmani_verses:
                print(f"  Loaded Uthmani text from {ext}: {len(uthmani_verses)} verses")

    for ext in ['txt', 'xml']:
        simple_file = os.path.join(data_dir, f'quran-simple.{ext}')
        if os.path.exists(simple_file) and not simple_verses:
            parser = parse_tanzil_txt if ext == 'txt' else parse_tanzil_xml
            simple_verses = parser(simple_file)
            if simple_verses:
                print(f"  Loaded Simple text from {ext}: {len(simple_verses)} verses")

    if not uthmani_verses:
        print("  [error] No Uthmani Quran text found. Run download_tanzil.py first.")
        return False

    if not simple_verses:
        print("  [warn] No Simple text found; using Uthmani for both columns.")
        simple_verses = uthmani_verses

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Clear existing data
    c.execute("DELETE FROM ayat")
    c.execute("DELETE FROM surahs")

    # Insert surahs
    sajdah_set = set(SAJDAH_VERSES)
    for i, meta in enumerate(SURAH_META):
        surah_id = i + 1
        name_ar, name_en, name_translit, rev_type, rev_order, verse_count, bismillah = meta
        c.execute("""
            INSERT INTO surahs (id, name_arabic, name_english, name_transliteration,
                               revelation_type, revelation_order, verse_count, bismillah)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (surah_id, name_ar, name_en, name_translit, rev_type, rev_order, verse_count, bismillah))

    print(f"  Inserted {len(SURAH_META)} surahs")

    # Insert ayat
    ayat_count = 0
    for surah_id in range(1, 115):
        verse_count = SURAH_META[surah_id - 1][5]
        for verse_num in range(1, verse_count + 1):
            text_uthmani = uthmani_verses.get((surah_id, verse_num), '')
            text_simple = simple_verses.get((surah_id, verse_num), '')
            juz = get_juz(surah_id, verse_num)
            sajdah = (surah_id, verse_num) in sajdah_set

            c.execute("""
                INSERT INTO ayat (surah_id, verse_number, text_arabic, text_arabic_simple,
                                 juz, sajdah)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (surah_id, verse_num, text_uthmani, text_simple, juz, sajdah))
            ayat_count += 1

    conn.commit()

    # Verify
    c.execute("SELECT COUNT(*) FROM surahs")
    surah_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ayat")
    db_ayat_count = c.fetchone()[0]

    conn.close()

    print(f"  Inserted {ayat_count} ayat (db count: {db_ayat_count})")
    print(f"  Surahs: {surah_count}, Ayat: {db_ayat_count}")

    return surah_count == 114 and db_ayat_count == 6236


if __name__ == '__main__':
    print("Importing Quran Arabic text...")
    success = import_quran_arabic()
    if success:
        print("  [OK] Import successful: 114 surahs, 6236 ayat")
    else:
        print("  [WARN] Import completed but counts may not match expected values")
