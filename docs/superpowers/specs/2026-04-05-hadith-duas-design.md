# Islamic Hive Mind — Phase 2: Hadith + Duas Database

## Zero-Guess Principle Applies

All data imported must be traceable to its source. No hadith is fabricated or paraphrased. Every hadith retains its source book, grading, and chain of narration where available. When grading is unavailable from the source, the hadith is marked as `grade_unknown` and excluded from default queries.

## Context

Phase 1 is complete: the Quran corpus (114 surahs, 6,236 ayat, 77,429 words, 325,665 letters) lives in `db/hive-mind.db`. Phase 2 adds hadith collections and dua compilations to the same database.

## Scope

Import **10 hadith collections** (4 Shia + 6 Sunni) and **2 dua compilations** (Mafatih al-Jinan + Sahifa al-Sajjadiya) into the existing SQLite database. Strong hadiths only (sahih + hasan). Shia primary, Sunni cross-reference.

## Data Sources

### Shia Hadith (The Four Books — Al-Kutub al-Arba'a)

| Book | Author | Est. Hadiths | Source | Format |
|------|--------|-------------|--------|--------|
| Al-Kafi | Al-Kulayni (d. 941) | ~16,199 | ThaqalaynAPI | REST JSON |
| Man La Yahduruhu al-Faqih | Sheikh Saduq (d. 991) | ~5,963 | ThaqalaynAPI | REST JSON |
| Tahdhib al-Ahkam | Sheikh Tusi (d. 1067) | ~13,590 | ThaqalaynAPI | REST JSON |
| Al-Istibsar | Sheikh Tusi (d. 1067) | ~5,511 | ThaqalaynAPI | REST JSON |

**API:** https://www.thaqalayn-api.net/api/v2/{book-name}
**GitHub:** https://github.com/MohammedArab1/ThaqalaynAPI

### Sunni Hadith (The Six Books — Al-Kutub al-Sittah)

| Book | Author | Est. Hadiths | Source | Format |
|------|--------|-------------|--------|--------|
| Sahih al-Bukhari | Al-Bukhari (d. 870) | ~7,563 | hadith-json (GitHub) | JSON |
| Sahih Muslim | Muslim (d. 875) | ~7,500 | hadith-json (GitHub) | JSON |
| Sunan Abu Dawud | Abu Dawud (d. 889) | ~5,274 | hadith-json (GitHub) | JSON |
| Jami at-Tirmidhi | At-Tirmidhi (d. 892) | ~3,956 | hadith-json (GitHub) | JSON |
| Sunan an-Nasa'i | An-Nasa'i (d. 915) | ~5,761 | hadith-json (GitHub) | JSON |
| Sunan Ibn Majah | Ibn Majah (d. 887) | ~4,341 | hadith-json (GitHub) | JSON |

**GitHub:** https://github.com/AhmedBaset/hadith-json

### Duas

| Collection | Author | Items | Source | Format |
|-----------|--------|-------|--------|--------|
| Mafatih al-Jinan | Sheikh Abbas Qummi | ~100+ duas | duas.org | HTML scrape |
| Sahifa al-Sajjadiya | Imam Zain al-Abidin (as) | 54 supplications | duas.org | HTML scrape |

**Source:** https://duas.org/

## Database Schema

All new tables are added to the existing `db/hive-mind.db`.

### hadiths table

```sql
CREATE TABLE hadiths (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_book TEXT NOT NULL,       -- 'al_kafi', 'man_la_yahduruhu', 'tahdhib', 'istibsar',
                                     -- 'bukhari', 'muslim', 'abu_dawud', 'tirmidhi', 'nasai', 'ibn_majah'
    tradition TEXT NOT NULL,          -- 'shia' or 'sunni'
    book_volume TEXT,                 -- Volume/book number within the collection
    book_chapter TEXT,                -- Chapter/section name
    hadith_number TEXT,               -- Original numbering from the source
    
    -- Chain of narration
    isnad TEXT,                       -- Full chain of narrators (Arabic if available)
    isnad_english TEXT,               -- English translation of chain
    
    -- Content
    matn_arabic TEXT,                 -- Arabic text of the hadith
    matn_english TEXT,                -- English translation
    
    -- Grading
    grade TEXT NOT NULL,              -- 'sahih' or 'hasan' (only strong hadiths imported)
    grade_source TEXT,                -- Who/what graded it
    
    -- Classification
    topics TEXT,                      -- JSON array of topic tags
    related_quran_verses TEXT,        -- JSON array of surah:verse references
    
    -- Source tracking
    source_url TEXT,                  -- URL where this hadith was sourced from
    source_id TEXT,                   -- ID in the source system (ThaqalaynAPI id, etc.)
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_hadiths_book ON hadiths(source_book);
CREATE INDEX idx_hadiths_tradition ON hadiths(tradition);
CREATE INDEX idx_hadiths_grade ON hadiths(grade);
```

### duas table

```sql
CREATE TABLE duas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Identification
    name_arabic TEXT NOT NULL,
    name_english TEXT NOT NULL,
    name_transliteration TEXT NOT NULL,
    source_book TEXT NOT NULL DEFAULT 'mafatih_al_jinan',
    
    -- Content
    text_arabic TEXT NOT NULL,
    text_english TEXT,
    text_transliteration TEXT,
    
    -- Classification
    category TEXT NOT NULL,            -- 'dua', 'ziyarat', 'munajat', 'amal', 'taqibat', 'sahifa_sajjadiya'
    
    -- Attribution
    attributed_to TEXT NOT NULL,       -- 'prophet', 'imam_ali', 'imam_hussein', 'imam_sajjad', etc.
    
    -- Occasion
    occasion TEXT,                     -- 'daily', 'friday', 'muharram', 'ramadan', 'laylat_al_qadr', etc.
    day_specific TEXT,                 -- 'every_thursday_night', '15_shaban', 'night_of_ashura'
    prescribed_for TEXT,               -- 'forgiveness', 'protection', 'sustenance', 'healing'
    
    -- Quran connections
    quran_verses_referenced TEXT,      -- JSON array of surah:verse refs found in the dua text
    
    -- Source tracking
    source_url TEXT,
    hadith_grade TEXT,                 -- Grade of the hadith chain for this dua
    
    -- Metadata
    section_in_source TEXT,            -- Section/chapter in Mafatih or Sahifa
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_duas_category ON duas(category);
CREATE INDEX idx_duas_attributed ON duas(attributed_to);
CREATE INDEX idx_duas_occasion ON duas(occasion);
```

### narrators table

```sql
CREATE TABLE narrators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_arabic TEXT NOT NULL,
    name_english TEXT,
    birth_year_hijri INTEGER,
    death_year_hijri INTEGER,
    reliability TEXT,                  -- 'thiqah' (trustworthy), 'hasan' (good)
    tradition TEXT,                    -- 'shia', 'sunni', 'both'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_narrators_reliability ON narrators(reliability);
```

## Pipeline Architecture

### Directory Structure (new files)

```
scripts/
├── download/
│   ├── download_shia_hadith.py       ← Fetch from ThaqalaynAPI (all 4 books)
│   ├── download_sunni_hadith.py      ← Download hadith-json repo from GitHub
│   └── download_duas.py             ← Scrape duas.org for Mafatih + Sahifa
├── import/
│   ├── create_hadith_schema.py       ← Add hadiths, duas, narrators tables to hive-mind.db
│   ├── import_shia_hadith.py         ← Parse ThaqalaynAPI JSON → hadiths table (strong only)
│   ├── import_sunni_hadith.py        ← Parse hadith-json → hadiths table (strong only)
│   ├── import_mafatih_duas.py        ← Parse scraped Mafatih → duas table
│   ├── import_sahifa_sajjadiya.py    ← Parse scraped Sahifa → duas table
│   └── cross_reference_quran.py      ← Scan hadith/dua text for Quran verse references
├── verify/
│   └── verify_hadith_integrity.py    ← Per-collection count checks, grade distribution
└── pipeline_phase2.py                ← Orchestrate all Phase 2 steps
```

### Download Scripts

**download_shia_hadith.py:**
- Fetch all hadiths from ThaqalaynAPI for each of the 4 books
- API endpoint pattern: `https://www.thaqalayn-api.net/api/v2/{book-slug}`
- Save raw JSON per book in `data/hadith/shia/`
- Rate-limit requests (0.5s between pages)
- Resume capability (skip books already downloaded)

**download_sunni_hadith.py:**
- Clone/download the hadith-json GitHub repo
- Extract the 6 Sunni books from the JSON files
- Save to `data/hadith/sunni/`

**download_duas.py:**
- Scrape duas.org for:
  - Mafatih al-Jinan: key duas (Kumayl, Tawassul, Nudba, Arafah, etc.)
  - Ziyarat: Ashura, Arba'een, Aminullah
  - Sahifa al-Sajjadiya: all 54 supplications
- Extract Arabic text + English translation
- Save structured JSON to `data/duas/`

### Import Scripts

**import_shia_hadith.py:**
- Read downloaded JSON from `data/hadith/shia/`
- Filter: import ONLY hadiths graded sahih or hasan
- Map ThaqalaynAPI fields to hadiths table columns
- Set `tradition = 'shia'`
- Store source_url and source_id for traceability

**import_sunni_hadith.py:**
- Read downloaded JSON from `data/hadith/sunni/`
- Filter: import ONLY hadiths graded sahih or hasan
- Map hadith-json fields to hadiths table columns
- Set `tradition = 'sunni'`

**import_mafatih_duas.py / import_sahifa_sajjadiya.py:**
- Read scraped JSON from `data/duas/`
- Map to duas table columns
- Set `attributed_to` based on known attributions
- Set `category` (dua, ziyarat, munajat, etc.)

**cross_reference_quran.py:**
- Scan all hadith matn_english for Quran verse references (patterns like "Quran X:Y" or known verse text)
- Scan dua text_arabic for known Quran verse fragments
- Update `related_quran_verses` JSON field

### Data Directory Structure

```
data/
├── quran/            ← Existing (unchanged)
├── hadith/
│   ├── shia/
│   │   ├── al_kafi.json
│   │   ├── man_la_yahduruhu.json
│   │   ├── tahdhib.json
│   │   └── istibsar.json
│   └── sunni/
│       ├── bukhari.json
│       ├── muslim.json
│       ├── abu_dawud.json
│       ├── tirmidhi.json
│       ├── nasai.json
│       └── ibn_majah.json
└── duas/
    ├── mafatih_al_jinan/
    │   ├── dua_kumayl.json
    │   ├── dua_tawassul.json
    │   ├── ziyarat_ashura.json
    │   └── ...
    └── sahifa_sajjadiya/
        ├── supplication_01.json
        ├── supplication_02.json
        └── ...
```

## Filtering Rules

- **Import only:** sahih (authentic) and hasan (good) graded hadiths
- **Exclude entirely:** daif (weak) and mawdu (fabricated)
- **When grade is unknown:** Mark as `grade = 'grade_unknown'` and exclude from default queries. Log a warning during import.
- **Shia sources are PRIMARY.** Sunni sources are cross-reference only.
- **When Shia and Sunni agree** on a hadith: note the agreement
- **When they disagree:** present Shia perspective first

## Chatbot Integration

After Phase 2 import is complete:
- Update `web/lib/chat-context.ts` to remove the `hadith_request` direct response (which currently says "hadith database not built yet")
- Add hadith search to the RAG pipeline:
  - `hadith_request` intent → query hadiths table by topic or English text search
  - Include source book, grade, and chain in context
- Add dua search:
  - New intent pattern for dua requests → query duas table by occasion or name
  - Include Arabic text + English + attribution

## Verification Plan

1. Per-collection counts match expected ranges
2. All hadiths have non-null `matn_arabic` or `matn_english`
3. All hadiths have `grade` set (sahih or hasan only)
4. All hadiths have `source_book` and `tradition` set
5. All duas have `name_english`, `text_arabic`, `category`, `attributed_to`
6. Sahifa al-Sajjadiya has exactly 54 entries
7. Key duas present: Kumayl, Tawassul, Nudba, Arafah, Ziyarat Ashura
8. No duplicate hadiths within the same source book
9. `related_quran_verses` populated for hadiths that reference Quran
10. Pipeline is idempotent (running twice produces same results)

## Implementation Order

1. Schema creation (create_hadith_schema.py)
2. Download Shia hadiths (ThaqalaynAPI)
3. Download Sunni hadiths (hadith-json GitHub)
4. Download duas (duas.org scrape)
5. Import Shia hadiths (strong only)
6. Import Sunni hadiths (strong only)
7. Import Mafatih al-Jinan duas
8. Import Sahifa al-Sajjadiya
9. Cross-reference Quran verses
10. Run verification
11. Update chatbot RAG pipeline to use new data
