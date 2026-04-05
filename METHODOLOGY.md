# Islamic Hive Mind — Methodology & Counting Conventions

This document records every methodological decision that affects numerical
analysis. All counts in this database are convention-dependent — changing
any convention changes the results.

## Qira'ah (Recitation)

**Reading used: Hafs 'an 'Asim** (the most widely used reading globally
and the standard in Shia practice).

All letter counts, word counts, and Abjad values are specific to this
reading. Other qira'at (Warsh, Qalun, etc.) differ in approximately
40-50 words, which would affect letter counts and Abjad totals.

## Verse Numbering System

**System used: Kufan (al-'add al-Kufi)** — 6,236 verses total.

This is the system used in the standard Hafs Mushaf and is the accepted
standard in Shia scholarship. Other systems: Basran (6,204), Damascene
(6,227), Meccan (6,210).

### Bismillah Status

**Current implementation:** Bismillah is counted as verse 1 of Al-Fatihah
only. For surahs 2-114, the Bismillah is stored as a boolean flag on the
surahs table but is NOT included in the verse/word/letter counts.

**Shia scholarly position:** The majority Shia position (per Sayyid al-Khoei,
Sayyid al-Sistani, and virtually all Shia maraji') is that Bismillah IS
a verse of every surah except At-Tawbah (Surah 9). This means the true
Shia verse count would be 6,348 (6,236 + 112 Bismillahs).

**Impact:** All numerical patterns in this database are calculated WITHOUT
Bismillah as verse 1 for surahs 2-114. This follows the standard Mushaf
numbering convention but differs from the Shia theological position.

## Revelation Order

**Source: Egyptian standard chronological order** (1924 Cairo Royal Edition).

This is the most widely used ordering. The Shia tradition has its own
chronological traditions transmitted through the Imams, which differ in
several places. Notable: Surah 96 (Al-Alaq) as first revelation is
agreed upon across traditions.

## Meccan/Medinan Classification

**Current: Binary classification per surah.** 86 Meccan, 28 Medinan.

This is a simplification — approximately 20 surahs contain verses from
both periods. The database does not currently track verse-level revelation
type for mixed surahs.

## Word Boundary Definition

**Words are defined by the Leeds Quranic Arabic Corpus segmentation.**
Each space-delimited token in the Hafs Mushaf is one "word." Prefixed
particles (bi-, wa-, fa-, li-, al-) are morphological segments WITHIN
the word, not separate words.

Example: بِسْمِ (bismi) = 1 word containing prefix بِ + stem اسْمِ

**Total word count: 77,429** — this means 77,429 space-delimited tokens
per the Leeds Corpus segmentation.

**Total letter count: 325,665** — includes all 28 standard Arabic letters
plus hamza variants, ta marbuta (ة), alif maqsura (ى), and alif wasla (ٱ).
Diacritics excluded. Shadda counted as single letter.

**Total Abjad value: 23,381,357** — sum of all verse Abjad values using
the Eastern Arabic (Mashriqi) system with ة→5 and ى→10.

## Letter Counting

### Characters Counted as Letters
- 28 standard Arabic letters (alif through ya)
- Hamza variants: ء (standalone), آ (alif madda), أ (alif hamza above),
  إ (alif hamza below), ؤ (waw hamza), ئ (ya hamza)
- Ta Marbuta (ة) — counted as a letter
- Alif Maqsura (ى) — counted as a letter
- Alif Wasla (ٱ) — counted as a letter (13,483 occurrences)

### Characters NOT Counted
- Diacritical marks (tashkeel): fatha, kasra, damma, sukun, shadda, tanwin
- Spaces
- Tatweel/kashida (ـ)

### Shadda Convention
A letter with shadda (ّ) represents a doubled consonant. This project
counts it as **ONE letter** (the visual letter only). Some counting
traditions count it as TWO (since it represents two phonemes). This
choice affects total letter count significantly.

### Alif Wasla Convention
Alif Wasla (ٱ) is counted as a **separate letter form** from regular
Alif (ا). Both have Abjad value 1. In the letters table, they appear
as distinct entries. For aggregate letter frequency analysis, they may
be combined under "Alif family."

## Abjad (Gematria) Values

**System: Eastern Arabic (Mashriqi)** — the standard system used in the
Islamic East (Iraq, Iran, Indian subcontinent).

### Standard 28 Letters
Alif=1, Ba=2, Jeem=3, Dal=4, Ha=5, Waw=6, Zayn=7, Hha=8, Tta=9,
Ya=10, Kaf=20, Lam=30, Mim=40, Nun=50, Sin=60, Ayn=70, Fa=80, Sad=90,
Qaf=100, Ra=200, Shin=300, Ta=400, Tha=500, Kha=600, Dhal=700,
Dad=800, Dha=900, Ghayn=1000.

### Variant Character Mapping
| Character | Mapped To | Abjad Value | Rationale |
|-----------|-----------|-------------|-----------|
| ء Hamza | Alif | 1 | Hamza carried on alif base |
| آ Alif Madda | Alif | 1 | Variant of alif |
| أ Alif Hamza Above | Alif | 1 | Variant of alif |
| إ Alif Hamza Below | Alif | 1 | Variant of alif |
| ؤ Waw Hamza | Waw | 6 | Hamza carried on waw |
| ئ Ya Hamza | Ya | 10 | Hamza carried on ya |
| ة Ta Marbuta | Ha | 5 | Common convention; some scholars use 400 (Ta) |
| ى Alif Maqsura | Ya | 10 | Form of ya; some scholars use 1 (Alif) |
| ٱ Alif Wasla | Alif | 1 | Connecting alif |

**Note on Ta Marbuta:** The choice of 5 (Ha) vs. 400 (Ta) is debated.
This project uses 5 (Ha convention). If 400 (Ta) were used, the total
Quran Abjad value would be significantly higher.

## Word Frequency Claims

### Methodology
This project provides BOTH counting methods:
1. **Root-based counting:** Counts all words derived from a triliteral root.
   Includes all morphological forms (singular, plural, dual, verb conjugations).
2. **Surface-form counting:** Counts specific word forms by exact text match
   (with diacritics stripped for comparison).

### Scholarly Context
Popular word frequency claims (e.g., "day appears 365 times") are:
- **Modern origin:** Post-1970s, not found in any classical tafsir
- **Methodology-dependent:** Different proponents use different inclusion/exclusion
  criteria to reach their claimed numbers
- **Not endorsed by the hawzah:** Shia seminary scholarship treats these claims
  with caution to skepticism

### Number 19 Claims
The "Code 19" theory was primarily popularized by Rashad Khalifa (1974).
Khalifa was later rejected by mainstream Muslim scholarship. Individual
observations (like Bismillah having 19 letters) may be acknowledged as
interesting, but the broader "Code 19" framework is not accepted.

## English Translation

**Primary: Sahih International** — a clear, modern English translation.

**Limitation:** Sahih International follows a Sunni interpretive tradition.
Key verses with Shia-Sunni interpretive differences (e.g., 5:55 on wilayah,
33:33 on purification) reflect the Sunni reading. A Shia-oriented translation
(Ali Quli Qarai) should be added in a future iteration.

## Data Sources

| Source | Used For | Notes |
|--------|----------|-------|
| Tanzil.net | Arabic text (Uthmani + simplified) | Verified by multiple Islamic organizations |
| Quran.com API v4 | English translation, transliteration | Sahih International (resource_id 20) |
| Leeds Quranic Arabic Corpus | Word morphology (root, lemma, POS) | Academic, peer-reviewed, ~95% accuracy |
