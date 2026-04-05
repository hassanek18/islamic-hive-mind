# Phase 2: Hadith + Duas Database — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Import 8 hadith collections (4 Shia + 4 Sunni) and 2 dua compilations into the existing SQLite database, with grading, Quran cross-references, and chatbot integration.

**Architecture:** Python import scripts following the Phase 1 pattern. Download raw data → parse → filter (strong only) → import to SQLite → cross-reference with Quran → update chatbot RAG pipeline. All scripts in `scripts/` directory, data in `data/`.

**Tech Stack:** Python 3.12, requests, sqlite3, BeautifulSoup4 (for duas.org scraping)

**Spec:** `docs/superpowers/specs/2026-04-05-hadith-duas-design.md`

**Data availability (verified 2026-04-05):**
- ThaqalaynAPI: Al-Kafi (8 volumes), Man La Yahduruhu (5 volumes) — REST JSON. Tahdhib and Istibsar are NOT on this API.
- hadith-json GitHub: Bukhari, Muslim, Abu Dawud, Tirmidhi, Nasa'i, Ibn Majah — JSON by chapter
- duas.org: Mafatih al-Jinan, Sahifa al-Sajjadiya — HTML pages

**Note:** Tahdhib al-Ahkam and Al-Istibsar are not available on ThaqalaynAPI. This plan imports what's available now (Al-Kafi + Man La Yahduruhu for Shia, all 6 Sunni books). Tahdhib and Istibsar will be added when a digital source is found.

---

## File Map

```
scripts/
├── download/
│   ├── download_shia_hadith.py       ← Fetch Al-Kafi + Man La Yahduruhu from ThaqalaynAPI
│   ├── download_sunni_hadith.py      ← Download hadith-json from GitHub
│   └── download_duas.py             ← Scrape duas.org (Mafatih + Sahifa)
├── import/
│   ├── create_hadith_schema.py       ← Add 3 new tables to hive-mind.db
│   ├── import_shia_hadith.py         ← Parse + import Shia hadiths
│   ├── import_sunni_hadith.py        ← Parse + import Sunni hadiths
│   ├── import_duas.py                ← Import Mafatih + Sahifa duas
│   └── cross_reference_quran.py      ← Link hadiths/duas to Quran verses
├── verify/
│   └── verify_hadith_integrity.py    ← Count checks, grade checks
└── pipeline_phase2.py                ← Orchestrate all Phase 2 steps

data/
├── hadith/
│   ├── shia/                         ← Downloaded Shia hadith JSON
│   └── sunni/                        ← Downloaded Sunni hadith JSON
└── duas/
    ├── mafatih/                      ← Scraped Mafatih duas
    └── sahifa/                       ← Scraped Sahifa supplications

web/lib/
├── hadith.ts                         ← New: Hadith query functions
└── chat-context.ts                   ← Modified: Remove "not built yet" block, add hadith/dua RAG
```

---

### Task 1: Install BeautifulSoup4 + Create Data Directories

**Files:**
- Modify: `requirements.txt`
- Create: `data/hadith/shia/`, `data/hadith/sunni/`, `data/duas/mafatih/`, `data/duas/sahifa/`

- [ ] **Step 1: Add beautifulsoup4 to requirements.txt**

```bash
cd /c/Users/hassa/islamic-hive-mind
echo "beautifulsoup4>=4.12.0" >> requirements.txt
pip install beautifulsoup4
```

- [ ] **Step 2: Create data directories**

```bash
mkdir -p data/hadith/shia data/hadith/sunni data/duas/mafatih data/duas/sahifa
```

- [ ] **Step 3: Commit**

```bash
git add requirements.txt
git commit -m "feat: add beautifulsoup4 dependency for Phase 2 scraping

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Create Hadith/Duas Database Schema

**Files:**
- Create: `scripts/import/create_hadith_schema.py`

- [ ] **Step 1: Write schema creation script**

Create `scripts/import/create_hadith_schema.py`:
```python
"""Add hadith, duas, and narrators tables to hive-mind.db."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'hive-mind.db')


def create_hadith_schema(db_path=DB_PATH):
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS hadiths (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_book TEXT NOT NULL,
        tradition TEXT NOT NULL,
        book_volume TEXT,
        book_chapter TEXT,
        hadith_number TEXT,
        isnad TEXT,
        isnad_english TEXT,
        matn_arabic TEXT,
        matn_english TEXT,
        grade TEXT NOT NULL,
        grade_source TEXT,
        topics TEXT,
        related_quran_verses TEXT,
        source_url TEXT,
        source_id TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS duas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name_arabic TEXT NOT NULL,
        name_english TEXT NOT NULL,
        name_transliteration TEXT NOT NULL,
        source_book TEXT NOT NULL DEFAULT 'mafatih_al_jinan',
        text_arabic TEXT NOT NULL,
        text_english TEXT,
        text_transliteration TEXT,
        category TEXT NOT NULL,
        attributed_to TEXT NOT NULL,
        occasion TEXT,
        day_specific TEXT,
        prescribed_for TEXT,
        quran_verses_referenced TEXT,
        source_url TEXT,
        hadith_grade TEXT,
        section_in_source TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS narrators (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name_arabic TEXT NOT NULL,
        name_english TEXT,
        birth_year_hijri INTEGER,
        death_year_hijri INTEGER,
        reliability TEXT,
        tradition TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Indexes
    c.execute("CREATE INDEX IF NOT EXISTS idx_hadiths_book ON hadiths(source_book)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_hadiths_tradition ON hadiths(tradition)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_hadiths_grade ON hadiths(grade)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_duas_category ON duas(category)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_duas_attributed ON duas(attributed_to)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_duas_occasion ON duas(occasion)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_narrators_reliability ON narrators(reliability)")

    conn.commit()
    conn.close()
    print(f"Hadith schema created at {db_path}")
    print(f"  Tables: hadiths, duas, narrators")


if __name__ == '__main__':
    create_hadith_schema()
```

- [ ] **Step 2: Run the schema script**

```bash
python scripts/import/create_hadith_schema.py
```

Expected: "Hadith schema created" + "Tables: hadiths, duas, narrators"

- [ ] **Step 3: Verify tables exist**

```bash
python -c "
import sqlite3
conn = sqlite3.connect('db/hive-mind.db')
c = conn.cursor()
for t in ['hadiths', 'duas', 'narrators']:
    c.execute(f'SELECT COUNT(*) FROM {t}')
    print(f'{t}: {c.fetchone()[0]} rows')
conn.close()
"
```

Expected: 0 rows in each table.

- [ ] **Step 4: Commit**

```bash
git add scripts/import/create_hadith_schema.py
git commit -m "feat: add hadith, duas, narrators tables to database schema

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Download Shia Hadiths from ThaqalaynAPI

**Files:**
- Create: `scripts/download/download_shia_hadith.py`

- [ ] **Step 1: Write the download script**

Create `scripts/download/download_shia_hadith.py`:
```python
"""Download Shia hadith collections from ThaqalaynAPI.

Available books:
- Al-Kafi (8 volumes): Al-Kafi-Volume-{1-8}-Kulayni
- Man La Yahduruhu al-Faqih (5 volumes): Man-La-Yahduruh-al-Faqih-Volume-{1-5}-Saduq

Note: Tahdhib al-Ahkam and Al-Istibsar are NOT available on ThaqalaynAPI.
"""

import os
import json
import time
import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'hadith', 'shia')
API_BASE = "https://www.thaqalayn-api.net/api/v2"

SHIA_BOOKS = [
    # (slug, display_name, volumes)
    ("Al-Kafi-Volume-{vol}-Kulayni", "Al-Kafi", list(range(1, 9))),
    ("Man-La-Yahduruh-al-Faqih-Volume-{vol}-Saduq", "Man La Yahduruhu al-Faqih", list(range(1, 6))),
]

# Max hadith IDs per volume (from API /allbooks response)
VOLUME_MAX_IDS = {
    "Al-Kafi-Volume-1-Kulayni": 1449,
    "Al-Kafi-Volume-2-Kulayni": 2343,
    "Al-Kafi-Volume-3-Kulayni": 2178,
    "Al-Kafi-Volume-4-Kulayni": 2190,
    "Al-Kafi-Volume-5-Kulayni": 2088,
    "Al-Kafi-Volume-6-Kulayni": 2509,
    "Al-Kafi-Volume-7-Kulayni": 891,
    "Al-Kafi-Volume-8-Kulayni": 597,
    "Man-La-Yahduruh-al-Faqih-Volume-1-Saduq": 1569,
    "Man-La-Yahduruh-al-Faqih-Volume-2-Saduq": 1696,
    "Man-La-Yahduruh-al-Faqih-Volume-3-Saduq": 1758,
    "Man-La-Yahduruh-al-Faqih-Volume-4-Saduq": 964,
    "Man-La-Yahduruh-al-Faqih-Volume-5-Saduq": 395,
}


def download_shia_hadiths(data_dir=DATA_DIR):
    data_dir = os.path.abspath(data_dir)
    os.makedirs(data_dir, exist_ok=True)

    for slug_template, book_name, volumes in SHIA_BOOKS:
        for vol in volumes:
            slug = slug_template.format(vol=vol)
            out_file = os.path.join(data_dir, f"{slug}.json")

            if os.path.exists(out_file):
                print(f"  [skip] {slug} already downloaded")
                continue

            max_id = VOLUME_MAX_IDS.get(slug, 2000)
            print(f"  Downloading {book_name} Volume {vol} ({slug}, up to {max_id} hadiths)...")

            hadiths = []
            batch_size = 50
            for start in range(1, max_id + 1, batch_size):
                end = min(start + batch_size - 1, max_id)
                url = f"{API_BASE}/{slug}/{start}"

                try:
                    resp = requests.get(url, timeout=30)
                    if resp.status_code == 200:
                        data = resp.json()
                        if isinstance(data, dict) and 'id' in data:
                            hadiths.append(data)
                        elif isinstance(data, list):
                            hadiths.extend(data)
                    elif resp.status_code == 404:
                        pass  # Hadith ID doesn't exist, skip
                except Exception as e:
                    print(f"    [error] ID {start}: {e}")

                time.sleep(0.3)  # Rate limit

                if start % 200 == 0:
                    print(f"    Progress: {start}/{max_id} ({len(hadiths)} hadiths)")

            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(hadiths, f, ensure_ascii=False, indent=2)

            print(f"  [done] {slug}: {len(hadiths)} hadiths saved")

    print(f"\nShia hadith data directory: {data_dir}")


if __name__ == '__main__':
    print("Downloading Shia hadiths from ThaqalaynAPI...")
    download_shia_hadiths()
```

- [ ] **Step 2: Run the download (this takes a while — ~13 volumes, thousands of API calls)**

```bash
PYTHONIOENCODING=utf-8 python scripts/download/download_shia_hadith.py
```

This will take 30-60 minutes due to rate limiting. Run in background if needed.

- [ ] **Step 3: Commit**

```bash
git add scripts/download/download_shia_hadith.py
git commit -m "feat: add Shia hadith download script (ThaqalaynAPI)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Download Sunni Hadiths from GitHub

**Files:**
- Create: `scripts/download/download_sunni_hadith.py`

- [ ] **Step 1: Write the download script**

Create `scripts/download/download_sunni_hadith.py`:
```python
"""Download Sunni hadith collections from hadith-json GitHub repository.

Source: https://github.com/AhmedBaset/hadith-json
Format: JSON by chapter, containing {metadata, hadiths[]}
Books: bukhari, muslim, abudawud, tirmidhi, nasai, ibnmajah
"""

import os
import json
import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'hadith', 'sunni')
GITHUB_RAW = "https://raw.githubusercontent.com/AhmedBaset/hadith-json/main/db/by_book/the_9_books"

SUNNI_BOOKS = {
    'bukhari': 'Sahih al-Bukhari',
    'muslim': 'Sahih Muslim',
    'abudawud': 'Sunan Abu Dawud',
    'tirmidhi': "Jami' at-Tirmidhi",
    'nasai': "Sunan an-Nasa'i",
    'ibnmajah': 'Sunan Ibn Majah',
}


def download_sunni_hadiths(data_dir=DATA_DIR):
    data_dir = os.path.abspath(data_dir)
    os.makedirs(data_dir, exist_ok=True)

    for slug, name in SUNNI_BOOKS.items():
        out_file = os.path.join(data_dir, f"{slug}.json")

        if os.path.exists(out_file):
            print(f"  [skip] {slug} already downloaded")
            continue

        url = f"{GITHUB_RAW}/{slug}.json"
        print(f"  Downloading {name} from GitHub...")

        try:
            resp = requests.get(url, timeout=120)
            resp.raise_for_status()
            data = resp.json()

            # The by_book format is a single JSON with all hadiths
            if isinstance(data, dict) and 'hadiths' in data:
                count = len(data['hadiths'])
            elif isinstance(data, list):
                count = len(data)
            else:
                count = 0

            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"  [done] {slug}: {count} hadiths saved")

        except Exception as e:
            print(f"  [error] {slug}: {e}")

    print(f"\nSunni hadith data directory: {data_dir}")


if __name__ == '__main__':
    print("Downloading Sunni hadiths from GitHub...")
    download_sunni_hadiths()
```

- [ ] **Step 2: Run the download**

```bash
PYTHONIOENCODING=utf-8 python scripts/download/download_sunni_hadith.py
```

Expected: 6 JSON files downloaded in ~1-2 minutes (single file per book from GitHub).

- [ ] **Step 3: Commit**

```bash
git add scripts/download/download_sunni_hadith.py
git commit -m "feat: add Sunni hadith download script (hadith-json GitHub)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Download Duas from Duas.org

**Files:**
- Create: `scripts/download/download_duas.py`

- [ ] **Step 1: Write the duas scraper**

Create `scripts/download/download_duas.py`:
```python
"""Download duas from duas.org for Mafatih al-Jinan and Sahifa al-Sajjadiya.

Scrapes individual dua pages for Arabic text + English translation.
"""

import os
import json
import time
import requests
from bs4 import BeautifulSoup

MAFATIH_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'duas', 'mafatih')
SAHIFA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'duas', 'sahifa')

# Key duas from Mafatih al-Jinan with their duas.org URLs
MAFATIH_DUAS = [
    {"name_en": "Dua Kumayl", "name_ar": "دعاء كميل", "name_translit": "Du'a Kumayl",
     "url": "https://www.duas.org/kumayl.htm", "category": "dua",
     "attributed_to": "imam_ali", "occasion": "thursday_night"},
    {"name_en": "Dua Tawassul", "name_ar": "دعاء التوسل", "name_translit": "Du'a Tawassul",
     "url": "https://www.duas.org/tawassul.htm", "category": "dua",
     "attributed_to": "multiple_imams", "occasion": "tuesday_night"},
    {"name_en": "Dua Nudba", "name_ar": "دعاء الندبة", "name_translit": "Du'a Nudba",
     "url": "https://www.duas.org/nudba.htm", "category": "dua",
     "attributed_to": "imam_mahdi", "occasion": "friday_morning"},
    {"name_en": "Dua Arafah of Imam Hussain", "name_ar": "دعاء عرفة", "name_translit": "Du'a 'Arafah",
     "url": "https://www.duas.org/arafathusain.htm", "category": "dua",
     "attributed_to": "imam_hussein", "occasion": "day_of_arafah"},
    {"name_en": "Dua Abu Hamza al-Thumali", "name_ar": "دعاء أبي حمزة الثمالي", "name_translit": "Du'a Abi Hamza al-Thumali",
     "url": "https://www.duas.org/abuhamza.htm", "category": "dua",
     "attributed_to": "imam_sajjad", "occasion": "ramadan_predawn"},
    {"name_en": "Dua Jawshan al-Kabir", "name_ar": "دعاء الجوشن الكبير", "name_translit": "Du'a al-Jawshan al-Kabir",
     "url": "https://www.duas.org/jkabir.htm", "category": "dua",
     "attributed_to": "prophet", "occasion": "nights_of_qadr"},
    {"name_en": "Ziyarat Ashura", "name_ar": "زيارة عاشوراء", "name_translit": "Ziyarat 'Ashura",
     "url": "https://www.duas.org/ashura.htm", "category": "ziyarat",
     "attributed_to": "imam_baqir", "occasion": "muharram"},
    {"name_en": "Ziyarat Arba'een", "name_ar": "زيارة الأربعين", "name_translit": "Ziyarat al-Arba'in",
     "url": "https://www.duas.org/ziaraat/Arbain.htm", "category": "ziyarat",
     "attributed_to": "imam_askari", "occasion": "20_safar"},
    {"name_en": "Ziyarat Aminullah", "name_ar": "زيارة أمين الله", "name_translit": "Ziyarat Aminullah",
     "url": "https://www.duas.org/ziaraat/aminallah.htm", "category": "ziyarat",
     "attributed_to": "imam_sajjad", "occasion": "visiting_imam_ali_shrine"},
    {"name_en": "Dua Makarim al-Akhlaq", "name_ar": "دعاء مكارم الأخلاق", "name_translit": "Du'a Makarim al-Akhlaq",
     "url": "https://www.duas.org/sahifasajjadia/dua20.htm", "category": "dua",
     "attributed_to": "imam_sajjad", "occasion": "anytime"},
]

# Sahifa al-Sajjadiya — 54 supplications
SAHIFA_BASE_URL = "https://www.duas.org/sahifasajjadia/dua{num}.htm"


def scrape_dua_page(url):
    """Scrape a dua page from duas.org. Extract Arabic and English text."""
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'html.parser')

        # Extract text content — duas.org uses various formats
        # Try to find Arabic and English blocks
        text = soup.get_text(separator='\n', strip=True)

        # Split into lines, try to identify Arabic vs English
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        arabic_lines = []
        english_lines = []

        for line in lines:
            # Heuristic: lines with Arabic characters are Arabic
            has_arabic = any('\u0600' <= c <= '\u06FF' for c in line)
            if has_arabic and len(line) > 10:
                arabic_lines.append(line)
            elif len(line) > 10 and not line.startswith(('Home', 'Duas', 'Copyright', 'www.')):
                english_lines.append(line)

        arabic_text = '\n'.join(arabic_lines)
        english_text = '\n'.join(english_lines)

        return arabic_text, english_text

    except Exception as e:
        print(f"    [error] {url}: {e}")
        return '', ''


def download_mafatih(data_dir=MAFATIH_DIR):
    """Download key duas from Mafatih al-Jinan."""
    os.makedirs(data_dir, exist_ok=True)

    for dua in MAFATIH_DUAS:
        slug = dua['name_en'].lower().replace(' ', '_').replace("'", '')
        out_file = os.path.join(data_dir, f"{slug}.json")

        if os.path.exists(out_file):
            print(f"  [skip] {dua['name_en']} already downloaded")
            continue

        print(f"  Downloading {dua['name_en']}...")
        arabic, english = scrape_dua_page(dua['url'])

        result = {
            'name_arabic': dua['name_ar'],
            'name_english': dua['name_en'],
            'name_transliteration': dua['name_translit'],
            'text_arabic': arabic,
            'text_english': english,
            'category': dua['category'],
            'attributed_to': dua['attributed_to'],
            'occasion': dua['occasion'],
            'source_url': dua['url'],
            'source_book': 'mafatih_al_jinan',
        }

        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        has_ar = 'yes' if arabic else 'no'
        has_en = 'yes' if english else 'no'
        print(f"  [done] {dua['name_en']} (Arabic: {has_ar}, English: {has_en})")
        time.sleep(1)  # Be respectful to the server


def download_sahifa(data_dir=SAHIFA_DIR):
    """Download all 54 supplications of Sahifa al-Sajjadiya."""
    os.makedirs(data_dir, exist_ok=True)

    for num in range(1, 55):
        out_file = os.path.join(data_dir, f"supplication_{num:02d}.json")

        if os.path.exists(out_file):
            print(f"  [skip] Sahifa supplication {num} already downloaded")
            continue

        url = SAHIFA_BASE_URL.format(num=num)
        print(f"  Downloading Sahifa al-Sajjadiya #{num}...")
        arabic, english = scrape_dua_page(url)

        result = {
            'name_arabic': f'الدعاء {num}',
            'name_english': f'Supplication {num}',
            'name_transliteration': f"Du'a {num}",
            'number': num,
            'text_arabic': arabic,
            'text_english': english,
            'category': 'sahifa_sajjadiya',
            'attributed_to': 'imam_sajjad',
            'source_url': url,
            'source_book': 'sahifa_sajjadiya',
        }

        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        has_ar = 'yes' if arabic else 'no'
        has_en = 'yes' if english else 'no'
        print(f"  [done] Supplication {num} (Arabic: {has_ar}, English: {has_en})")
        time.sleep(1)


if __name__ == '__main__':
    print("Downloading Mafatih al-Jinan duas...")
    download_mafatih()
    print("\nDownloading Sahifa al-Sajjadiya...")
    download_sahifa()
```

- [ ] **Step 2: Run the download**

```bash
PYTHONIOENCODING=utf-8 python scripts/download/download_duas.py
```

Expected: ~10 Mafatih duas + 54 Sahifa supplications downloaded.

- [ ] **Step 3: Commit**

```bash
git add scripts/download/download_duas.py
git commit -m "feat: add duas download script (duas.org scraping)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: Import Shia Hadiths

**Files:**
- Create: `scripts/import/import_shia_hadith.py`

- [ ] **Step 1: Write the import script**

Create `scripts/import/import_shia_hadith.py`:
```python
"""Import Shia hadiths from downloaded ThaqalaynAPI JSON into the database.

Imports only hadiths that have grading information indicating sahih or hasan.
ThaqalaynAPI grading is in the 'majlisiGrading' or 'gradingsFull' fields.
"""

import sqlite3
import os
import json
import re

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'hive-mind.db')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'hadith', 'shia')

BOOK_SLUG_MAP = {
    'Al-Kafi': 'al_kafi',
    'Man La Yahduruhu al-Faqih': 'man_la_yahduruhu',
}

# Arabic grading keywords for sahih/hasan
STRONG_GRADES_AR = ['صحيح', 'حسن', 'موثق', 'قوي']
# Some gradings contain negations — these should be excluded
WEAK_INDICATORS_AR = ['ضعيف', 'مرسل', 'مجهول', 'مرفوع']


def is_strong_hadith(hadith_data):
    """Determine if a hadith is graded sahih or hasan based on available grading."""
    # Check majlisiGrading field
    majlisi = hadith_data.get('majlisiGrading', '')
    if majlisi:
        majlisi_lower = majlisi.strip()
        # Check for weak indicators first
        for weak in WEAK_INDICATORS_AR:
            if weak in majlisi_lower:
                return False, 'daif'
        # Check for strong indicators
        for strong in STRONG_GRADES_AR:
            if strong in majlisi_lower:
                if 'صحيح' in majlisi_lower:
                    return True, 'sahih'
                return True, 'hasan'

    # Check gradingsFull array
    gradings = hadith_data.get('gradingsFull', [])
    for g in gradings:
        grade_ar = g.get('grade_ar', '')
        if grade_ar:
            for weak in WEAK_INDICATORS_AR:
                if weak in grade_ar:
                    return False, 'daif'
            for strong in STRONG_GRADES_AR:
                if strong in grade_ar:
                    if 'صحيح' in grade_ar:
                        return True, 'sahih'
                    return True, 'hasan'

    # No grading available
    return False, 'grade_unknown'


def import_shia_hadiths(db_path=DB_PATH, data_dir=DATA_DIR):
    db_path = os.path.abspath(db_path)
    data_dir = os.path.abspath(data_dir)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Clear existing Shia hadiths
    c.execute("DELETE FROM hadiths WHERE tradition = 'shia'")

    total_imported = 0
    total_skipped = 0

    for filename in sorted(os.listdir(data_dir)):
        if not filename.endswith('.json'):
            continue

        filepath = os.path.join(data_dir, filename)
        print(f"  Processing {filename}...")

        with open(filepath, 'r', encoding='utf-8') as f:
            hadiths = json.load(f)

        if not isinstance(hadiths, list):
            hadiths = [hadiths]

        imported = 0
        skipped = 0

        for h in hadiths:
            is_strong, grade = is_strong_hadith(h)

            if not is_strong:
                skipped += 1
                continue

            book_name = h.get('book', '')
            source_book = BOOK_SLUG_MAP.get(book_name, book_name.lower().replace(' ', '_'))

            # Extract sanad (chain) and matn (text) from thaqalayn fields
            sanad = h.get('thaqalaynSanad', '') or ''
            matn_en = h.get('thaqalaynMatn', '') or h.get('englishText', '')
            matn_ar = h.get('arabicText', '')

            grade_source = 'Majlisi (Mir\'at al-\'Uqul)' if h.get('majlisiGrading') else 'ThaqalaynAPI grading'

            c.execute("""
                INSERT INTO hadiths (source_book, tradition, book_volume, book_chapter,
                    hadith_number, isnad_english, matn_arabic, matn_english,
                    grade, grade_source, source_url, source_id)
                VALUES (?, 'shia', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source_book,
                str(h.get('volume', '')),
                h.get('chapter', '') or h.get('category', ''),
                str(h.get('id', '')),
                sanad,
                matn_ar,
                matn_en,
                grade,
                grade_source,
                h.get('URL', ''),
                f"{h.get('bookId', '')}:{h.get('id', '')}",
            ))
            imported += 1

        total_imported += imported
        total_skipped += skipped
        print(f"    Imported: {imported}, Skipped (weak/unknown): {skipped}")

    conn.commit()

    c.execute("SELECT COUNT(*) FROM hadiths WHERE tradition = 'shia'")
    db_count = c.fetchone()[0]
    conn.close()

    print(f"\n  Total imported: {total_imported}")
    print(f"  Total skipped: {total_skipped}")
    print(f"  Database count (Shia): {db_count}")
    return db_count > 0


if __name__ == '__main__':
    print("Importing Shia hadiths (strong only)...")
    import_shia_hadiths()
```

- [ ] **Step 2: Run the import**

```bash
PYTHONIOENCODING=utf-8 python scripts/import/import_shia_hadith.py
```

- [ ] **Step 3: Commit**

```bash
git add scripts/import/import_shia_hadith.py
git commit -m "feat: add Shia hadith import (strong grades only, from ThaqalaynAPI)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 7: Import Sunni Hadiths

**Files:**
- Create: `scripts/import/import_sunni_hadith.py`

- [ ] **Step 1: Write the import script**

Create `scripts/import/import_sunni_hadith.py`:
```python
"""Import Sunni hadiths from downloaded hadith-json GitHub data.

Bukhari and Muslim are considered entirely sahih by Sunni scholars.
Other books (Abu Dawud, Tirmidhi, Nasa'i, Ibn Majah) have mixed grades
but the hadith-json dataset doesn't include per-hadith grading.
We import Bukhari and Muslim as sahih. The other 4 as hasan (conservative).
"""

import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'hive-mind.db')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'hadith', 'sunni')

SUNNI_BOOKS = {
    'bukhari': ('sahih_bukhari', 'sahih'),
    'muslim': ('sahih_muslim', 'sahih'),
    'abudawud': ('sunan_abu_dawud', 'hasan'),
    'tirmidhi': ('jami_tirmidhi', 'hasan'),
    'nasai': ('sunan_nasai', 'hasan'),
    'ibnmajah': ('sunan_ibn_majah', 'hasan'),
}


def import_sunni_hadiths(db_path=DB_PATH, data_dir=DATA_DIR):
    db_path = os.path.abspath(db_path)
    data_dir = os.path.abspath(data_dir)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Clear existing Sunni hadiths
    c.execute("DELETE FROM hadiths WHERE tradition = 'sunni'")

    total_imported = 0

    for filename, (source_book, default_grade) in SUNNI_BOOKS.items():
        filepath = os.path.join(data_dir, f"{filename}.json")
        if not os.path.exists(filepath):
            print(f"  [skip] {filename}.json not found")
            continue

        print(f"  Processing {filename}...")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle both formats: {hadiths: [...]} or [...]
        if isinstance(data, dict) and 'hadiths' in data:
            hadiths = data['hadiths']
        elif isinstance(data, list):
            hadiths = data
        else:
            print(f"  [warn] Unexpected format in {filename}")
            continue

        imported = 0
        for h in hadiths:
            matn_ar = h.get('arabic', '')
            eng = h.get('english', {})
            narrator = eng.get('narrator', '') if isinstance(eng, dict) else ''
            matn_en = eng.get('text', '') if isinstance(eng, dict) else str(eng)

            if narrator:
                matn_en = f"{narrator} {matn_en}"

            c.execute("""
                INSERT INTO hadiths (source_book, tradition, book_volume, book_chapter,
                    hadith_number, matn_arabic, matn_english, grade, grade_source,
                    source_id)
                VALUES (?, 'sunni', ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source_book,
                str(h.get('bookId', '')),
                str(h.get('chapterId', '')),
                str(h.get('idInBook', h.get('id', ''))),
                matn_ar,
                matn_en,
                default_grade,
                f"{'Entire collection sahih' if default_grade == 'sahih' else 'Default hasan (per-hadith grading not available)'}",
                str(h.get('id', '')),
            ))
            imported += 1

        total_imported += imported
        print(f"    Imported: {imported}")

    conn.commit()

    c.execute("SELECT COUNT(*) FROM hadiths WHERE tradition = 'sunni'")
    db_count = c.fetchone()[0]
    c.execute("SELECT source_book, COUNT(*) FROM hadiths WHERE tradition = 'sunni' GROUP BY source_book")
    for book, count in c.fetchall():
        print(f"    {book}: {count}")
    conn.close()

    print(f"\n  Total Sunni hadiths imported: {db_count}")
    return db_count > 0


if __name__ == '__main__':
    print("Importing Sunni hadiths...")
    import_sunni_hadiths()
```

- [ ] **Step 2: Run the import**

```bash
PYTHONIOENCODING=utf-8 python scripts/import/import_sunni_hadith.py
```

- [ ] **Step 3: Commit**

```bash
git add scripts/import/import_sunni_hadith.py
git commit -m "feat: add Sunni hadith import (Bukhari/Muslim sahih, others hasan)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 8: Import Duas

**Files:**
- Create: `scripts/import/import_duas.py`

- [ ] **Step 1: Write the duas import script**

Create `scripts/import/import_duas.py`:
```python
"""Import duas from scraped JSON files (Mafatih al-Jinan + Sahifa al-Sajjadiya)."""

import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'hive-mind.db')
MAFATIH_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'duas', 'mafatih')
SAHIFA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'duas', 'sahifa')


def import_duas(db_path=DB_PATH):
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Clear existing duas
    c.execute("DELETE FROM duas")

    total = 0

    # Import Mafatih al-Jinan
    mafatih_dir = os.path.abspath(MAFATIH_DIR)
    if os.path.exists(mafatih_dir):
        for filename in sorted(os.listdir(mafatih_dir)):
            if not filename.endswith('.json'):
                continue

            filepath = os.path.join(mafatih_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                dua = json.load(f)

            if not dua.get('text_arabic') and not dua.get('text_english'):
                print(f"  [skip] {filename}: no text content")
                continue

            c.execute("""
                INSERT INTO duas (name_arabic, name_english, name_transliteration,
                    source_book, text_arabic, text_english, category,
                    attributed_to, occasion, source_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dua.get('name_arabic', ''),
                dua.get('name_english', ''),
                dua.get('name_transliteration', ''),
                dua.get('source_book', 'mafatih_al_jinan'),
                dua.get('text_arabic', ''),
                dua.get('text_english', ''),
                dua.get('category', 'dua'),
                dua.get('attributed_to', ''),
                dua.get('occasion', ''),
                dua.get('source_url', ''),
            ))
            total += 1
            print(f"  [ok] {dua.get('name_english', filename)}")

    # Import Sahifa al-Sajjadiya
    sahifa_dir = os.path.abspath(SAHIFA_DIR)
    if os.path.exists(sahifa_dir):
        for filename in sorted(os.listdir(sahifa_dir)):
            if not filename.endswith('.json'):
                continue

            filepath = os.path.join(sahifa_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                dua = json.load(f)

            if not dua.get('text_arabic') and not dua.get('text_english'):
                print(f"  [skip] {filename}: no text content")
                continue

            c.execute("""
                INSERT INTO duas (name_arabic, name_english, name_transliteration,
                    source_book, text_arabic, text_english, category,
                    attributed_to, source_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dua.get('name_arabic', ''),
                dua.get('name_english', ''),
                dua.get('name_transliteration', ''),
                'sahifa_sajjadiya',
                dua.get('text_arabic', ''),
                dua.get('text_english', ''),
                'sahifa_sajjadiya',
                'imam_sajjad',
                dua.get('source_url', ''),
            ))
            total += 1
            print(f"  [ok] Sahifa #{dua.get('number', '?')}")

    conn.commit()

    c.execute("SELECT COUNT(*) FROM duas")
    db_count = c.fetchone()[0]
    c.execute("SELECT source_book, COUNT(*) FROM duas GROUP BY source_book")
    for book, count in c.fetchall():
        print(f"    {book}: {count}")
    conn.close()

    print(f"\n  Total duas imported: {db_count}")
    return db_count > 0


if __name__ == '__main__':
    print("Importing duas...")
    import_duas()
```

- [ ] **Step 2: Run**

```bash
PYTHONIOENCODING=utf-8 python scripts/import/import_duas.py
```

- [ ] **Step 3: Commit**

```bash
git add scripts/import/import_duas.py
git commit -m "feat: add duas import (Mafatih al-Jinan + Sahifa al-Sajjadiya)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 9: Verification Script

**Files:**
- Create: `scripts/verify/verify_hadith_integrity.py`

- [ ] **Step 1: Write verification script**

Create `scripts/verify/verify_hadith_integrity.py`:
```python
"""Verify Phase 2 data integrity: hadiths and duas."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'hive-mind.db')


def verify(db_path=DB_PATH):
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    results = []

    def check(name, query, expected_min=None, expected_exact=None):
        c.execute(query)
        actual = c.fetchone()[0]
        if expected_exact is not None:
            passed = actual == expected_exact
            exp_str = str(expected_exact)
        elif expected_min is not None:
            passed = actual >= expected_min
            exp_str = f">={expected_min}"
        else:
            passed = actual > 0
            exp_str = ">0"
        status = "PASS" if passed else "FAIL"
        results.append((name, passed))
        print(f"  [{status}] {name}: expected {exp_str}, got {actual}")

    print("\n=== Phase 2: Hadith & Duas Integrity ===\n")

    # Hadith checks
    check("Hadiths table exists and has data",
          "SELECT COUNT(*) FROM hadiths", expected_min=1)
    check("Shia hadiths present",
          "SELECT COUNT(*) FROM hadiths WHERE tradition = 'shia'", expected_min=1)
    check("Sunni hadiths present",
          "SELECT COUNT(*) FROM hadiths WHERE tradition = 'sunni'", expected_min=1)
    check("All hadiths have grade",
          "SELECT COUNT(*) FROM hadiths WHERE grade IS NULL OR grade = ''", expected_exact=0)
    check("All hadiths have source_book",
          "SELECT COUNT(*) FROM hadiths WHERE source_book IS NULL OR source_book = ''", expected_exact=0)
    check("All hadiths have tradition",
          "SELECT COUNT(*) FROM hadiths WHERE tradition IS NULL OR tradition = ''", expected_exact=0)
    check("All hadiths have Arabic or English text",
          "SELECT COUNT(*) FROM hadiths WHERE (matn_arabic IS NULL OR matn_arabic = '') AND (matn_english IS NULL OR matn_english = '')",
          expected_exact=0)
    check("Only strong grades (sahih/hasan)",
          "SELECT COUNT(*) FROM hadiths WHERE grade NOT IN ('sahih', 'hasan')", expected_exact=0)

    # Duas checks
    check("Duas table has data",
          "SELECT COUNT(*) FROM duas", expected_min=1)
    check("All duas have name_english",
          "SELECT COUNT(*) FROM duas WHERE name_english IS NULL OR name_english = ''", expected_exact=0)
    check("All duas have text_arabic or text_english",
          "SELECT COUNT(*) FROM duas WHERE (text_arabic IS NULL OR text_arabic = '') AND (text_english IS NULL OR text_english = '')",
          expected_exact=0)
    check("All duas have category",
          "SELECT COUNT(*) FROM duas WHERE category IS NULL OR category = ''", expected_exact=0)
    check("All duas have attributed_to",
          "SELECT COUNT(*) FROM duas WHERE attributed_to IS NULL OR attributed_to = ''", expected_exact=0)

    # Summary
    c.execute("SELECT source_book, COUNT(*) FROM hadiths GROUP BY source_book ORDER BY COUNT(*) DESC")
    print("\n  Hadith counts by source:")
    for book, count in c.fetchall():
        print(f"    {book}: {count}")

    c.execute("SELECT source_book, COUNT(*) FROM duas GROUP BY source_book")
    print("\n  Dua counts by source:")
    for book, count in c.fetchall():
        print(f"    {book}: {count}")

    conn.close()

    passed = sum(1 for _, p in results if p)
    total = len(results)
    print(f"\n=== Results: {passed}/{total} checks passed ===\n")
    return passed == total


if __name__ == '__main__':
    verify()
```

- [ ] **Step 2: Run verification**

```bash
PYTHONIOENCODING=utf-8 python scripts/verify/verify_hadith_integrity.py
```

- [ ] **Step 3: Commit**

```bash
git add scripts/verify/verify_hadith_integrity.py
git commit -m "feat: add Phase 2 integrity verification script

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 10: Phase 2 Pipeline Orchestrator

**Files:**
- Create: `scripts/pipeline_phase2.py`

- [ ] **Step 1: Write pipeline script**

Create `scripts/pipeline_phase2.py`:
```python
"""Run the Phase 2 (Hadith + Duas) import pipeline."""

import sys
import os
import time
import importlib

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

STEPS = [
    ('schema', 'Create hadith/duas schema',
     'scripts.import.create_hadith_schema', 'create_hadith_schema'),
    ('download_shia', 'Download Shia hadiths (ThaqalaynAPI)',
     'scripts.download.download_shia_hadith', 'download_shia_hadiths'),
    ('download_sunni', 'Download Sunni hadiths (GitHub)',
     'scripts.download.download_sunni_hadith', 'download_sunni_hadiths'),
    ('download_duas', 'Download duas (duas.org)',
     'scripts.download.download_duas', 'download_mafatih'),
    ('download_sahifa', 'Download Sahifa al-Sajjadiya',
     'scripts.download.download_duas', 'download_sahifa'),
    ('import_shia', 'Import Shia hadiths (strong only)',
     'scripts.import.import_shia_hadith', 'import_shia_hadiths'),
    ('import_sunni', 'Import Sunni hadiths',
     'scripts.import.import_sunni_hadith', 'import_sunni_hadiths'),
    ('import_duas', 'Import duas',
     'scripts.import.import_duas', 'import_duas'),
    ('verify', 'Verify integrity',
     'scripts.verify.verify_hadith_integrity', 'verify'),
]


def run_pipeline(step_name=None):
    print("=" * 60)
    print("  Islamic Hive Mind - Phase 2: Hadith + Duas Pipeline")
    print("=" * 60)

    steps = STEPS
    if step_name:
        steps = [s for s in STEPS if s[0] == step_name]
        if not steps:
            print(f"Unknown step: {step_name}")
            print(f"Available: {', '.join(s[0] for s in STEPS)}")
            return False

    total = len(steps)
    passed = 0

    for i, (name, desc, mod_path, func_name) in enumerate(steps, 1):
        print(f"\n[{i}/{total}] {desc} ({name})")
        print("-" * 40)

        start = time.time()
        try:
            mod = importlib.import_module(mod_path)
            func = getattr(mod, func_name)
            result = func()
            elapsed = time.time() - start
            if result is False:
                print(f"  [warn] ({elapsed:.1f}s)")
            else:
                print(f"  [ok] ({elapsed:.1f}s)")
                passed += 1
        except Exception as e:
            elapsed = time.time() - start
            print(f"  [error] ({elapsed:.1f}s): {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'=' * 60}")
    print(f"  Pipeline complete: {passed}/{total} steps successful")
    print(f"{'=' * 60}")
    return passed == total


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--step', help='Run only this step')
    args = parser.parse_args()
    success = run_pipeline(step_name=args.step)
    sys.exit(0 if success else 1)
```

- [ ] **Step 2: Commit**

```bash
git add scripts/pipeline_phase2.py
git commit -m "feat: add Phase 2 pipeline orchestrator

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 11: Update Chatbot to Use Hadith Data

**Files:**
- Create: `web/lib/hadith.ts`
- Modify: `web/lib/chat-context.ts`

- [ ] **Step 1: Create hadith query functions**

Create `web/lib/hadith.ts`:
```typescript
import { getDb } from './db';

export interface Hadith {
  id: number;
  source_book: string;
  tradition: string;
  book_chapter: string | null;
  hadith_number: string | null;
  matn_arabic: string | null;
  matn_english: string | null;
  grade: string;
  grade_source: string | null;
}

export interface Dua {
  id: number;
  name_arabic: string;
  name_english: string;
  name_transliteration: string;
  source_book: string;
  text_arabic: string;
  text_english: string | null;
  category: string;
  attributed_to: string;
  occasion: string | null;
}

export async function searchHadithByTopic(topic: string): Promise<Hadith[]> {
  const db = getDb();
  const result = await db.query<Hadith>(
    `SELECT * FROM hadiths WHERE matn_english LIKE ? ORDER BY tradition, source_book LIMIT 10`,
    [`%${topic}%`]
  );
  return result.rows;
}

export async function getDuaByName(name: string): Promise<Dua | null> {
  const db = getDb();
  return db.queryOne<Dua>(
    `SELECT * FROM duas WHERE name_english LIKE ? OR name_transliteration LIKE ?`,
    [`%${name}%`, `%${name}%`]
  );
}

export async function getDuasByOccasion(occasion: string): Promise<Dua[]> {
  const db = getDb();
  const result = await db.query<Dua>(
    `SELECT * FROM duas WHERE occasion LIKE ? ORDER BY name_english`,
    [`%${occasion}%`]
  );
  return result.rows;
}

export async function getHadithStats(): Promise<{ tradition: string; source_book: string; count: number }[]> {
  const db = getDb();
  const result = await db.query<{ tradition: string; source_book: string; count: number }>(
    `SELECT tradition, source_book, COUNT(*) as count FROM hadiths GROUP BY tradition, source_book ORDER BY tradition, count DESC`
  );
  return result.rows;
}
```

- [ ] **Step 2: Update chat-context.ts to use hadith data**

In `web/lib/chat-context.ts`, make these changes:

1. Add import at the top:
```typescript
import { searchHadithByTopic, getDuaByName, getDuasByOccasion } from './hadith';
```

2. Remove the `hadith_request` entry from `DIRECT_RESPONSES` (delete the line that says "The hadith database has not been built yet...")

3. Add `hadith_request` and a new `dua_request` to the `buildContext` switch statement:
```typescript
      case 'hadith_request': {
        const term = extractSearchTerm(message);
        const hadiths = await searchHadithByTopic(term);
        context = `[Database Query: hadiths table, search for "${term}"]\n`;
        context += `Found ${hadiths.length} hadiths:\n\n`;
        for (const h of hadiths.slice(0, 5)) {
          context += `Source: ${h.source_book} (${h.tradition}, grade: ${h.grade})\n`;
          if (h.matn_arabic) context += `Arabic: ${h.matn_arabic.slice(0, 200)}\n`;
          if (h.matn_english) context += `English: ${h.matn_english.slice(0, 300)}\n`;
          context += '\n';
        }
        if (hadiths.length === 0) {
          context += 'No hadiths found matching this topic in the database.\n';
        }
        context += '\nIMPORTANT: Only cite hadiths shown above. Do not fabricate any hadith.\n';
        break;
      }
```

4. Add dua intent patterns to `INTENT_PATTERNS`:
```typescript
  dua_request: [
    /dua\s+/i,
    /supplication/i,
    /ziyarat/i,
    /sahifa/i,
    /mafatih/i,
    /what (?:dua|prayer|supplication).*(?:read|recite)/i,
  ],
```

5. Add dua_request to the switch in buildContext:
```typescript
      case 'dua_request': {
        const term = extractSearchTerm(message);
        const dua = await getDuaByName(term);
        if (dua) {
          context = `[Database Query: duas table, found "${dua.name_english}"]\n\n`;
          context += `Name: ${dua.name_english} (${dua.name_transliteration})\n`;
          context += `Arabic name: ${dua.name_arabic}\n`;
          context += `Category: ${dua.category}\n`;
          context += `Attributed to: ${dua.attributed_to}\n`;
          if (dua.occasion) context += `Occasion: ${dua.occasion}\n`;
          if (dua.text_arabic) context += `\nArabic text (first 500 chars): ${dua.text_arabic.slice(0, 500)}\n`;
          if (dua.text_english) context += `\nEnglish text (first 500 chars): ${dua.text_english.slice(0, 500)}\n`;
        } else {
          context = `[Database Query: no dua found matching "${term}"]\n`;
        }
        break;
      }
```

6. Update the IntentType in `web/types/index.ts` to add `'dua_request'`:
```typescript
export type IntentType =
  | 'verse_lookup'
  | 'word_query'
  | 'pattern_query'
  | 'surah_info'
  | 'story_request'
  | 'fiqh_ruling'
  | 'hadith_request'
  | 'dua_request'
  | 'general_islamic';
```

- [ ] **Step 3: Commit**

```bash
git add web/lib/hadith.ts web/lib/chat-context.ts web/types/index.ts
git commit -m "feat: integrate hadith + dua data into chatbot RAG pipeline

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 12: Run Full Pipeline and Verify

- [ ] **Step 1: Run the full Phase 2 pipeline**

```bash
cd /c/Users/hassa/islamic-hive-mind
PYTHONIOENCODING=utf-8 python scripts/pipeline_phase2.py
```

This runs all steps: schema → download → import → verify.

Note: The Shia hadith download is the slowest step (~30-60 min). You can run individual steps:
```bash
python scripts/pipeline_phase2.py --step download_shia   # Just Shia download
python scripts/pipeline_phase2.py --step import_shia     # Just Shia import
```

- [ ] **Step 2: Verify final database state**

```bash
PYTHONIOENCODING=utf-8 python -c "
import sqlite3
conn = sqlite3.connect('db/hive-mind.db')
c = conn.cursor()
print('=== Full Database Summary ===')
for table in ['surahs','ayat','words','letters','hadiths','duas','narrators','patterns']:
    c.execute(f'SELECT COUNT(*) FROM {table}')
    print(f'  {table}: {c.fetchone()[0]}')
print()
c.execute('SELECT tradition, source_book, COUNT(*) FROM hadiths GROUP BY tradition, source_book ORDER BY tradition, COUNT(*) DESC')
print('Hadith breakdown:')
for row in c.fetchall():
    print(f'  {row[0]} / {row[1]}: {row[2]}')
print()
c.execute('SELECT source_book, COUNT(*) FROM duas GROUP BY source_book')
print('Dua breakdown:')
for row in c.fetchall():
    print(f'  {row[0]}: {row[1]}')
conn.close()
"
```

- [ ] **Step 3: Commit everything and push**

```bash
git add -A
git commit -m "feat: complete Phase 2 — hadith + duas database fully imported

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
git push origin master
```
