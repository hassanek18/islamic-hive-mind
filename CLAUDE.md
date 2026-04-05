# Islamic Hive Mind — Claude Code Instructions

## Project Context
Islamic knowledge base combining Quran text analysis (Arabic + English + transliteration)
with numerical pattern discovery. Phase 1: Quran corpus.

## Tech Stack
- Python 3.12 — import scripts, analysis, visualizations
- Node.js — query layer (future)
- SQLite — database at db/hive-mind.db

## Project Structure
- `scripts/download/` — Data acquisition (Python)
- `scripts/import/` — DB import pipeline (Python)
- `scripts/analysis/` — Pattern analysis tools (Python)
- `scripts/verify/` — Integrity verification (Python)
- `visualizations/` — Generated HTML with D3.js/Chart.js
- `data/quran/` — Downloaded source files (XML, JSON)
- `db/` — SQLite database

## Commands
- `pip install -r requirements.txt` — Install Python deps
- `python scripts/pipeline.py` — Run full import pipeline
- `python scripts/pipeline.py --step <name>` — Run single step
- `python scripts/verify/verify_integrity.py` — Run integrity checks

## Key Rules
- All Quran text verified against known statistics after import
- Arabic text: preserve full Unicode, never strip diacritics from Uthmani (keep simple copy separately)
- Abjad values use standard Eastern Arabic (Mashriqi) system
- Every pattern claim must show methodology and raw data
- Mark patterns as: confirmed, partial, debunked, or new_discovery
- Never overstate findings — if approximate, say so
