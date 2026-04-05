# Islamic Hive Mind — Project Plan

## Vision

A growing Islamic knowledge base that combines AI with deep Quranic scholarship. Three core capabilities:

1. **Quran Analysis Engine** — Full text corpus (Arabic + English + transliteration) with numerical pattern discovery and verification tools, visualized through interactive charts, grids, and heatmaps.

2. **Islamic Knowledge Base** — Shia-primary hadith scholarship with strong hadiths only, cross-referenced against Sunni sources, queryable conversationally.

3. **Faith, Emotion & Devotion Engine** �� The human heart of the project. Comprehensive Shia historical narrative from the Prophet through the 12 Imams, with Karbala as the spiritual center. Full catalog of latmiyat and nasheeds (Arabic + Farsi) with lyrics, reciters, historical context, emotional/sentiment analysis, and cross-references back to Quran verses and hadiths.

**Start:** Quran first. Hadith second. Grow from there.

---

## Technical Architecture

### Stack

| Layer | Technology |
|---|---|
| Runtime | Node.js (Claude Code project) |
| Database | SQLite (local, portable, no server needed) via better-sqlite3 |
| Analysis scripts | Python (for heavy numerical computation, Arabic text processing) |
| Visualization | HTML artifacts with D3.js / Chart.js (generated on demand) |
| Conversational | Query the database through Claude, ask questions naturally |
| Arabic text | Full Unicode Arabic support, Abjad/gematria value tables |

### Why SQLite
- Local to the project (no Supabase setup needed)
- Portable — the entire knowledge base is a single file you can copy/backup
- Fast for the data volumes involved (Quran is ~78,000 words — tiny for a database)
- Perfect for a personal research tool that grows over time

---

## PHASE 1 — Quran Text Corpus (COMPLETE)

### Step 1.1: Acquire the Quran Text

**Sources (all free, open, and respected):**

| Source | What it provides | Format |
|---|---|---|
| **Tanzil.net** | Gold-standard Arabic text (Uthmani + Simple scripts), verified by multiple Islamic organizations | XML, UTF-8 text |
| **Quran.com API** | English translations (Sahih International, Pickthall, Yusuf Ali, etc.) + transliteration | JSON API |
| **Leeds Quranic Arabic Corpus** | Word-by-word morphological analysis (root, lemma, part of speech, grammar) | XML |

### Step 1.2: Database Schema — Quran Text

```sql
-- Surahs (chapters)
CREATE TABLE surahs (
  id INTEGER PRIMARY KEY, -- 1-114
  name_arabic TEXT NOT NULL, -- Arabic name
  name_english TEXT NOT NULL, -- English name
  name_transliteration TEXT NOT NULL, -- Transliterated name
  revelation_type TEXT NOT NULL, -- 'meccan' or 'medinan'
  revelation_order INTEGER, -- chronological order of revelation
  verse_count INTEGER NOT NULL,
  word_count INTEGER, -- total words in surah
  letter_count INTEGER, -- total letters in surah
  bismillah BOOLEAN DEFAULT true -- all except surah 9 (At-Tawbah)
);

-- Ayat (verses)
CREATE TABLE ayat (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  surah_id INTEGER REFERENCES surahs(id),
  verse_number INTEGER NOT NULL,
  text_arabic TEXT NOT NULL, -- Arabic (Uthmani script)
  text_arabic_simple TEXT NOT NULL, -- Arabic (simplified, no diacritics)
  text_english TEXT NOT NULL, -- English translation
  text_transliteration TEXT NOT NULL, -- Transliteration
  word_count INTEGER,
  letter_count INTEGER,
  letter_count_no_spaces INTEGER, -- letters excluding spaces
  abjad_value INTEGER, -- total Abjad/gematria value of the verse
  juz INTEGER, -- which juz (1-30)
  hizb INTEGER, -- which hizb
  page INTEGER, -- Madani mushaf page number
  sajdah BOOLEAN DEFAULT false, -- verse of prostration
  UNIQUE(surah_id, verse_number)
);

-- Words (word-by-word breakdown)
CREATE TABLE words (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ayah_id INTEGER REFERENCES ayat(id),
  surah_id INTEGER,
  verse_number INTEGER,
  word_position INTEGER, -- position within the verse (1-based)
  text_arabic TEXT NOT NULL,
  text_simple TEXT NOT NULL, -- without diacritics
  text_english TEXT, -- word translation
  text_transliteration TEXT,
  root TEXT, -- Arabic root (3-letter or 4-letter)
  lemma TEXT, -- dictionary form
  part_of_speech TEXT, -- noun, verb, particle, etc.
  morphology TEXT, -- detailed morphological tags
  abjad_value INTEGER,
  letter_count INTEGER
);

-- Letters (individual letter breakdown for deep analysis)
CREATE TABLE letters (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ayah_id INTEGER REFERENCES ayat(id),
  word_id INTEGER REFERENCES words(id),
  surah_id INTEGER,
  verse_number INTEGER,
  word_position INTEGER,
  letter_position INTEGER, -- position within word
  letter_arabic TEXT NOT NULL, -- the letter
  letter_name TEXT, -- name of the letter (Alif, Ba, Ta, etc.)
  abjad_value INTEGER, -- Abjad numerical value
  is_sun_letter BOOLEAN,
  is_moon_letter BOOLEAN
);

-- Abjad value reference table
CREATE TABLE abjad_values (
  letter TEXT PRIMARY KEY,
  letter_name TEXT NOT NULL,
  value INTEGER NOT NULL,
  order_position INTEGER NOT NULL -- position in Arabic alphabet
);
```

### Step 1.3: Data Import Scripts

```
scripts/
├── import_quran_arabic.py      — Parse Tanzil.net XML, populate surahs + ayat (Arabic)
├── import_quran_english.py     — Fetch translations from Quran.com API, add to ayat
├── import_transliteration.py   — Fetch transliteration, add to ayat
├── import_morphology.py        — Parse Leeds corpus XML, populate words table
├── generate_letters.py         — Break every word into individual letters, populate letters table
├── calculate_abjad.py          — Calculate Abjad values for every letter, word, verse, surah
├── calculate_statistics.py     — Count words, letters per verse/surah, update aggregate fields
└── verify_integrity.py         — Verify: 114 surahs, 6,236 verses, totals match known counts
```

### Step 1.4: Verification Checksums

After import, verify against known Quran statistics:

| Metric | Expected Value | Verification |
|---|---|---|
| Total surahs | 114 | Count surahs |
| Total ayat | 6,236 | Count ayat |
| Total words | 77,429 (Leeds Corpus segmentation, Hafs reading) | Count words |
| Total letters | 325,665 (includes ta marbuta, alif maqsura, alif wasla) | Count letters |
| Meccan surahs | 86 | Count where revelation_type = 'meccan' |
| Medinan surahs | 28 | Count where revelation_type = 'medinan' |
| Surahs with Bismillah | 113 (all except At-Tawbah) | Count where bismillah = true |
| Bismillah in An-Naml (27:30) | 1 (inside a verse) | Verify ayah content |

---

## PHASE 2 — Numerical Pattern Analysis

### Step 2.1: Known Pattern Verification

Build analysis tools to verify well-documented numerical claims about the Quran:

**Category A: Word Frequency Patterns**

| Claim | What to verify | Method |
|---|---|---|
| "Day" (يوم) appears 365 times | Count all forms of يوم in singular form | Word root search |
| "Month" (شهر) appears 12 times | Count all forms of شهر | Word root search |
| "Life" (حياة) and "Death" (موت) appear the same number of times | Count both roots and compare | Root frequency |
| "Angels" (ملائكة) and "Devils" (شياطين) appear the same count | Count both | Word search |
| "World" (دنيا) and "Hereafter" (آخرة) appear equally | Count both | Word search |
| "Man" and "Woman" appear equally | Count both terms | Word search |

**Category B: Number 19 Patterns**

| Claim | What to verify | Method |
|---|---|---|
| Bismillah has 19 letters | Count letters in بسم الله الرحمن الرحيم | Letter count |
| Total surahs = 114 = 19 × 6 | 114 / 19 | Division check |
| First revelation (96:1-5) has 19 words | Count words in Surah 96, verses 1-5 | Word count |
| Surah 96 has 19 verses | Count verses | Verse count |
| The "mysterious letters" (Muqatta'at) and their frequencies | Count occurrences of each letter in its surah | Letter frequency |

**Category C: Structural Patterns**

| Pattern | What to look for | Method |
|---|---|---|
| Surah/verse number sums | Do surah numbers + verse counts produce meaningful numbers? | Arithmetic |
| Center point symmetry | Is there symmetry around the midpoint of the Quran? | Positional analysis |
| Ring composition | Do surahs/passages form chiastic (A-B-C-B'-A') structures? | Text pattern matching |
| Golden ratio in text distribution | Does the golden ratio appear in text/chapter divisions? | Mathematical analysis |
| Odd/even patterns | Patterns in odd/even surah numbers, verse counts | Statistical analysis |

### Step 2.2: Pattern Discovery Engine

Build tools to search for NEW patterns that haven't been documented:

**Discovery tools:**

```sql
-- Tool 1: Frequency analysis
-- Tool 2: Divisibility scanner
-- Tool 3: Sum scanner
-- Tool 4: Symmetry detector
-- Tool 5: Cross-reference finder
-- Tool 6: Prime number analyzer
-- Tool 7: Sequence detector
-- Tool 8: Abjad deep analysis
```

### Step 2.3: Database — Pattern Storage

```sql
CREATE TABLE patterns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  description TEXT NOT NULL,
  claim TEXT,
  method TEXT,
  result TEXT,
  verified BOOLEAN,
  significance TEXT,
  data JSONB,
  notes TEXT,
  source TEXT,
  discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE analysis_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  analysis_type TEXT NOT NULL,
  parameters JSONB,
  results JSONB,
  interesting_findings TEXT,
  run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## PHASE 3 — Visualization Tools

### Interactive visualizations (built as HTML artifacts on demand)

| Visualization | What it shows | Technology |
|---|---|---|
| **Letter frequency heatmap** | Frequency of each Arabic letter across all 114 surahs as a heatmap grid | D3.js |
| **Surah statistics dashboard** | Bar charts of verse count, word count, letter count per surah | Chart.js |
| **Abjad value map** | Color-coded grid of Abjad values per verse | D3.js |
| **Word frequency chart** | Top N most frequent words/roots with their counts | Bar chart |
| **Pattern verification results** | Dashboard showing all tested claims with pass/fail | Table + indicators |
| **Symmetry visualizer** | Side-by-side comparison of first/second half | Split view |
| **Number distribution** | Where specific numbers appear in verse/surah/word counts | Scatter plot |
| **Muqatta'at letter analysis** | The mysterious letters and their frequency | Specialized grid |
| **Ring composition viewer** | Visual display of chiastic structures | Arc diagram |
| **Cross-reference network** | How word locations relate numerically | Network graph |

---

## PHASE 4 — Islamic Knowledge Base (Hadith)

### Shia Primary Sources (Al-Kutub al-Arba'a — The Four Books)

| # | Book | Author | Hadiths | Focus |
|---|---|---|---|---|
| 1 | **Al-Kafi** | Al-Kulayni (d. 941 CE) | ~16,199 | Most comprehensive — theology, jurisprudence, ethics, history |
| 2 | **Man La Yahduruhu al-Faqih** | Sheikh Saduq (d. 991 CE) | ~5,963 | Jurisprudence focused |
| 3 | **Tahdhib al-Ahkam** | Sheikh Tusi (d. 1067 CE) | ~13,590 | Jurisprudence, reconciles contradictions |
| 4 | **Al-Istibsar** | Sheikh Tusi (d. 1067 CE) | ~5,511 | Resolves conflicting hadiths |

### Sunni Cross-Reference Sources (Al-Kutub al-Sittah — The Six Books)

| # | Book | Author | Focus |
|---|---|---|---|
| 1 | **Sahih al-Bukhari** | Al-Bukhari (d. 870 CE) | Most authenticated Sunni collection |
| 2 | **Sahih Muslim** | Muslim ibn al-Hajjaj (d. 875 CE) | Second most authenticated |
| 3 | **Sunan Abu Dawud** | Abu Dawud (d. 889 CE) | Legal hadiths |
| 4 | **Jami at-Tirmidhi** | Al-Tirmidhi (d. 892 CE) | Includes grading |
| 5 | **Sunan an-Nasa'i** | Al-Nasa'i (d. 915 CE) | Strictest criteria |
| 6 | **Sunan Ibn Majah** | Ibn Majah (d. 887 CE) | Broadest collection |

### Hadith Database Schema

```sql
CREATE TABLE hadiths (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_book TEXT NOT NULL,
  tradition TEXT NOT NULL, -- 'shia' or 'sunni'
  book_section TEXT,
  hadith_number TEXT,
  isnad TEXT,
  narrators JSONB,
  matn_arabic TEXT,
  matn_english TEXT,
  grade TEXT, -- 'sahih', 'hasan', 'daif', 'mawdu'
  grade_source TEXT,
  is_strong BOOLEAN,
  topics JSONB,
  related_quran_verses JSONB,
  cross_references JSONB,
  shia_sunni_agreement BOOLEAN,
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hadith_topics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  parent_id INTEGER REFERENCES hadith_topics(id),
  description TEXT
);

CREATE TABLE narrators (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name_arabic TEXT NOT NULL,
  name_english TEXT,
  birth_year INTEGER,
  death_year INTEGER,
  reliability TEXT,
  tradition TEXT,
  notes TEXT
);
```

### Filtering Rules
- **Primary view:** Shia hadiths graded sahih or hasan ONLY
- **Weak hadiths (daif):** stored but flagged and excluded from default queries
- **Fabricated hadiths (mawdu):** excluded entirely
- **Cross-reference:** when a Shia hadith has a matching Sunni hadith, show both
- **Conflicts:** always present the Shia perspective as primary

### Mafatih al-Jinan Integration

```sql
CREATE TABLE duas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name_arabic TEXT NOT NULL,
  name_english TEXT NOT NULL,
  name_transliteration TEXT NOT NULL,
  source_book TEXT DEFAULT 'mafatih_al_jinan',
  original_source TEXT,
  text_arabic TEXT NOT NULL,
  text_english TEXT,
  text_transliteration TEXT,
  category TEXT NOT NULL, -- 'dua', 'ziyarat', 'munajat', 'amal', 'taqibat', 'sahifa_sajjadiya'
  attributed_to TEXT NOT NULL,
  attributed_to_id INTEGER REFERENCES historical_figures(id),
  isnad TEXT,
  hadith_source TEXT,
  hadith_grade TEXT,
  is_strong BOOLEAN DEFAULT true,
  occasion TEXT,
  day_specific TEXT,
  time_specific TEXT,
  prescribed_for TEXT,
  quran_verses_referenced JSONB,
  quran_verses_related JSONB,
  section_in_mafatih TEXT,
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key duas to prioritize:**

| Dua | Attributed to | Occasion | Significance |
|---|---|---|---|
| Dua Kumayl | Imam Ali (as) | Thursday nights | Among the most beloved supplications |
| Dua Tawassul | Multiple Imams | Anytime, especially difficulties | Intercession through Ahlul Bayt |
| Dua Nudba | Imam Mahdi tradition | Friday mornings, Eids | Longing for the 12th Imam |
| Dua Arafah | Imam Hussein (as) | Day of Arafah | Recited by Hussein before Karbala |
| Ziyarat Ashura | Imam Baqir (as) | Daily, especially Muharram | Central to Karbala mourning |
| Ziyarat Arba'een | Imam Hassan al-Askari (as) | 20th Safar | 40 days after Ashura |
| Dua Abu Hamza al-Thumali | Imam Zain al-Abidin (as) | Ramadan, pre-dawn | One of the most emotional prayers |
| Sahifa al-Sajjadiya (all 54) | Imam Zain al-Abidin (as) | Various | "The Psalms of Islam" |

---

## PHASE 5 — Conversational Interface

### Example queries

| User asks | Claude does |
|---|---|
| "How many times does 'mercy' appear?" | Queries words table for root r-h-m |
| "Show me the letter frequency heatmap" | Generates D3.js visualization |
| "Is it true that 'day' appears 365 times?" | Runs verification query |
| "Find strong hadiths about patience from Al-Kafi" | Queries hadiths with filters |
| "What do Shia and Sunni sources say about Ghadir?" | Cross-reference query |
| "I'm feeling lost, what dua should I read?" | Recommends based on emotional state |

---

## PHASE 6 — Faith, Emotion & Devotion Engine

### Historical Narrative Scope

| Era | Key Events |
|---|---|
| Pre-Islam | Context: Arabia before the Prophet |
| Prophetic era | Revelation, early Islam, key battles |
| Key theological events | Ghadir Khumm, Mubahala, Event of the Cloak |
| Post-Prophet | Saqifa, Fadak (Shia perspective) |
| Imam Ali's era | Caliphate, Jamal, Siffin, martyrdom |
| **Karbala** | **The central event — full detailed narrative** |
| Post-Karbala | Captivity, journey to Damascus |
| Remaining Imams | Each Imam through the 12th |
| The Occultation | Minor and Major occultation |

### Karbala Timeline Database

```sql
CREATE TABLE karbala_timeline (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date_hijri TEXT,
  date_gregorian TEXT,
  day_of_muharram INTEGER,
  event_title TEXT NOT NULL,
  event_description TEXT NOT NULL,
  location TEXT,
  figures_involved JSONB,
  quran_references JSONB,
  hadith_references JSONB,
  emotional_significance TEXT,
  sources JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Historical Figures Database

```sql
CREATE TABLE historical_figures (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name_arabic TEXT NOT NULL,
  name_english TEXT NOT NULL,
  name_farsi TEXT,
  title TEXT,
  kunya TEXT,
  category TEXT NOT NULL,
  birth_date TEXT,
  birth_place TEXT,
  death_date TEXT,
  death_place TEXT,
  cause_of_death TEXT,
  age_at_death INTEGER,
  father_id INTEGER REFERENCES historical_figures(id),
  mother_id INTEGER REFERENCES historical_figures(id),
  imam_number INTEGER,
  role_in_karbala TEXT,
  biography TEXT,
  key_quotes JSONB,
  related_quran_verses JSONB,
  related_hadiths JSONB,
  is_opponent BOOLEAN DEFAULT false,
  opposition_role TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Latmiyat & Nasheeds Catalog

```sql
CREATE TABLE reciters (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name_arabic TEXT,
  name_english TEXT NOT NULL,
  name_farsi TEXT,
  country TEXT,
  language TEXT,
  active BOOLEAN DEFAULT true,
  biography TEXT,
  popularity_tier TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE devotional_poetry (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title_original TEXT NOT NULL,
  title_english TEXT,
  lyrics_original TEXT NOT NULL,
  lyrics_transliteration TEXT,
  lyrics_english_translation TEXT,
  language TEXT NOT NULL,
  type TEXT NOT NULL, -- 'latmiya', 'nasheed', 'qasida', 'noha', 'marsiya', 'radood'
  reciter_id INTEGER REFERENCES reciters(id),
  poet TEXT,
  composer TEXT,
  occasion TEXT,
  day_specific TEXT,
  dedicated_to JSONB,
  historical_event TEXT,
  themes JSONB,
  emotional_tone TEXT,
  audio_url TEXT,
  video_url TEXT,
  quran_references JSONB,
  hadith_references JSONB,
  historical_context TEXT,
  sentiment_analysis JSONB,
  year_published INTEGER,
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Emotional Analysis for Duas

```sql
CREATE TABLE dua_emotional_analysis (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  dua_id INTEGER REFERENCES duas(id),
  emotional_tone TEXT,
  emotional_arc JSONB,
  relationship_with_god TEXT,
  core_theology JSONB,
  human_condition TEXT,
  key_imagery JSONB,
  metaphors JSONB,
  when_people_turn_to_this TEXT,
  related_latmiyat JSONB,
  related_historical_moments JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Build Order

### Phase 1A: Quran Text Import ✅ COMPLETE
### Phase 1B: Pattern Verification ✅ COMPLETE
### Phase 1C: Pattern Discovery ✅ COMPLETE
### Phase 1D: Visualizations ✅ COMPLETE

### Phase 2: Hadith + Duas (NEXT)
26. Source and import Shia Four Books
27. Source and import Sunni Six Books
28. Grade filtering (strong only)
29. Cross-reference matching
30. Topic tagging
31. Import Mafatih al-Jinan
32. Import Sahifa al-Sajjadiya
33. Map hadith chains
34. Cross-reference duas with Quran
35. Build conversational query layer

### Phase 3A: Historical Narrative
### Phase 3B: Devotional Poetry Catalog
### Phase 3C: Emotional/Sentiment Analysis

---

## Project Structure

```
islamic-hive-mind/
├── data/
│   └── quran/                          ← Downloaded source files
├── db/
│   └── hive-mind.db                    ← SQLite database
├── scripts/
│   ���── download/                       ← Data acquisition
│   ├── import/                         ← DB import pipeline
│   ├── analysis/                       ← Pattern analysis
│   ├── verify/                         ← Integrity verification
│   └── pipeline.py                     ← Pipeline orchestrator
├── visualizations/                     ← HTML visualization generators
├── requirements.txt
├── package.json
├── CLAUDE.md
└── islamic-hive-mind-plan.md           ← This file
```
