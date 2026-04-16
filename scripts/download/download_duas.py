"""Download duas from duas.org.

Uses the duas.org JSON API (data_v2/*.json) as primary source.
Falls back to static HTML scraping for pages that still serve old-format content.

Downloads:
  - Mafatih al-Jinan key duas (mapped to new API IDs where available)
  - Sahifa al-Sajjadiya supplications (where available)
  - All other available duas from the duas.org search index
"""

import os
import re
import json
import time
import unicodedata

import requests
from bs4 import BeautifulSoup

MAFATIH_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'duas', 'mafatih')
SAHIFA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'duas', 'sahifa')

DELAY = 1.0  # seconds between requests (be respectful)

HEADERS = {
    'User-Agent': 'IslamicHiveMind/1.0 (academic research project)'
}

API_BASE = "https://www.duas.org/data_v2"

# ── Mafatih duas: mapped to new API IDs where available ──────────────────────
# Some duas have moved to new IDs on the restructured site.
# Where the API has them, we use the API; otherwise we try static HTML or
# mark as unavailable.
MAFATIH_DUAS = [
    {
        "slug": "kumayl",
        "api_id": "dua-kumayl",
        "name_english": "Dua Kumayl",
        "name_arabic": "\u062f\u0639\u0627\u0621 \u0643\u0645\u064a\u0644",
        "attributed_to": "imam_ali",
        "occasion": "thursday_night",
        "source_book": "Mafatih al-Jinan",
    },
    {
        "slug": "tawassul",
        "api_id": None,  # Not in new API; static HTML still works
        "static_url": "https://www.duas.org/tawassul.htm",
        "name_english": "Dua Tawassul",
        "name_arabic": "\u062f\u0639\u0627\u0621 \u0627\u0644\u062a\u0648\u0633\u0644",
        "attributed_to": "multiple_imams",
        "occasion": "tuesday_night",
        "source_book": "Mafatih al-Jinan",
    },
    {
        "slug": "nudba",
        "api_id": "dua-nudbah",
        "name_english": "Dua Nudba",
        "name_arabic": "\u062f\u0639\u0627\u0621 \u0627\u0644\u0646\u062f\u0628\u0629",
        "attributed_to": "imam_mahdi",
        "occasion": "friday_morning",
        "source_book": "Mafatih al-Jinan",
    },
    {
        "slug": "arafah-hussain",
        "api_id": None,  # Not available on current site
        "static_url": None,
        "name_english": "Dua Arafah of Imam Hussain",
        "name_arabic": "\u062f\u0639\u0627\u0621 \u0639\u0631\u0641\u0629 \u0644\u0644\u0625\u0645\u0627\u0645 \u0627\u0644\u062d\u0633\u064a\u0646",
        "attributed_to": "imam_hussein",
        "occasion": "day_of_arafah",
        "source_book": "Mafatih al-Jinan",
    },
    {
        "slug": "abu-hamza-thumali",
        "api_id": "ramadan-dua-abu-hamza-thumali",
        "name_english": "Dua Abu Hamza al-Thumali",
        "name_arabic": "\u062f\u0639\u0627\u0621 \u0623\u0628\u064a \u062d\u0645\u0632\u0629 \u0627\u0644\u062b\u0645\u0627\u0644\u064a",
        "attributed_to": "imam_sajjad",
        "occasion": "ramadan_predawn",
        "source_book": "Mafatih al-Jinan",
    },
    {
        "slug": "jawshan-kabir",
        "api_id": None,  # Not available on current site
        "static_url": None,
        "name_english": "Jawshan al-Kabir",
        "name_arabic": "\u062f\u0639\u0627\u0621 \u0627\u0644\u062c\u0648\u0634\u0646 \u0627\u0644\u0643\u0628\u064a\u0631",
        "attributed_to": "prophet",
        "occasion": "nights_of_qadr",
        "source_book": "Mafatih al-Jinan",
    },
    {
        "slug": "ziyarat-ashura",
        "api_id": "ziyarat-imam-hussain-ashura",
        "name_english": "Ziyarat Ashura",
        "name_arabic": "\u0632\u064a\u0627\u0631\u0629 \u0639\u0627\u0634\u0648\u0631\u0627\u0621",
        "attributed_to": "imam_baqir",
        "occasion": "muharram",
        "source_book": "Mafatih al-Jinan",
    },
    {
        "slug": "ziyarat-arbaeen",
        "api_id": None,  # Not available on current site
        "static_url": None,
        "name_english": "Ziyarat Arba'een",
        "name_arabic": "\u0632\u064a\u0627\u0631\u0629 \u0627\u0644\u0623\u0631\u0628\u0639\u064a\u0646",
        "attributed_to": "imam_askari",
        "occasion": "20_safar",
        "source_book": "Mafatih al-Jinan",
    },
    {
        "slug": "ziyarat-aminullah",
        "api_id": None,  # Not available on current site
        "static_url": None,
        "name_english": "Ziyarat Aminullah",
        "name_arabic": "\u0632\u064a\u0627\u0631\u0629 \u0623\u0645\u064a\u0646 \u0627\u0644\u0644\u0647",
        "attributed_to": "imam_sajjad",
        "occasion": "visiting_imam_ali_shrine",
        "source_book": "Mafatih al-Jinan",
    },
    {
        "slug": "makarim-al-akhlaq",
        "api_id": None,  # Not available on current site
        "static_url": None,
        "name_english": "Dua Makarim al-Akhlaq",
        "name_arabic": "\u062f\u0639\u0627\u0621 \u0645\u0643\u0627\u0631\u0645 \u0627\u0644\u0623\u062e\u0644\u0627\u0642",
        "attributed_to": "imam_sajjad",
        "occasion": "anytime",
        "source_book": "Sahifa al-Sajjadiya",
    },
]

# ── Sahifa al-Sajjadiya: only dua 44 is available via the new API ────────────
# The old URLs (sahifasajjadia/dua{1-54}.htm) are all 404.
# We download what's available.
SAHIFA_API_IDS = [
    "sahifa-sajjadiya-dua-44-welcoming-the-month-of-ramadan",
]


# ──────────────────────────────────────────────────────────────────────────────
# JSON API download (primary)
# ──────────────────────────────────────────────────────────────────────────────

def _download_api_json(api_id):
    """Fetch a dua from the duas.org JSON API."""
    url = f"{API_BASE}/{api_id}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _api_json_to_our_format(api_data, dua_info):
    """Convert duas.org API JSON to our storage format.

    Concatenates all segment arabic/translation text and preserves
    the full structured data for later processing.
    """
    all_arabic = []
    all_english = []
    all_transliteration = []
    segments_structured = []

    for dua_block in api_data.get("duas", []):
        # Skip non-dua blocks (like 'text' type explanations)
        if dua_block.get("type") == "text":
            continue

        for seg in dua_block.get("segments", []):
            ar = seg.get("arabic", "").strip()
            en = seg.get("translation", "").strip()
            tr = seg.get("transliteration", "").strip()

            if ar:
                all_arabic.append(ar)
            if en:
                all_english.append(en)
            if tr:
                all_transliteration.append(tr)

            segments_structured.append({
                "arabic": ar,
                "translation": en,
                "transliteration": tr,
            })

    # Build metadata from dua_info + API data
    meta_from_api = {}
    for dua_block in api_data.get("duas", []):
        if dua_block.get("type") == "dua":
            meta_from_api = dua_block.get("meta", {})
            break

    result = {
        "api_id": api_data.get("id", ""),
        "name_arabic": dua_info.get("name_arabic", ""),
        "name_english": dua_info.get("name_english", api_data.get("title", "")),
        "text_arabic": "\n".join(all_arabic),
        "text_english": "\n".join(all_english),
        "text_transliteration": "\n".join(all_transliteration),
        "segments": segments_structured,
        "category": dua_info.get("category", "mafatih"),
        "attributed_to": dua_info.get("attributed_to", ""),
        "occasion": dua_info.get("occasion", ""),
        "source_url": f"https://www.duas.org/{api_data.get('id', '')}.html",
        "source_book": dua_info.get("source_book", ""),
        "tags": meta_from_api.get("purpose", []),
        "api_meta": meta_from_api,
    }
    return result


# ──────────────────────────────────────────────────────────────────────────────
# HTML scraping (fallback for old static pages)
# ──────────────────────────────────────────────────────────────────────────────

def _is_arabic(text):
    """Check if a string contains predominantly Arabic characters."""
    if not text or not text.strip():
        return False
    arabic_count = 0
    total_count = 0
    for char in text:
        if unicodedata.category(char).startswith('L'):
            total_count += 1
            cp = ord(char)
            if (0x0600 <= cp <= 0x06FF or   # Arabic
                0x0750 <= cp <= 0x077F or   # Arabic Supplement
                0x08A0 <= cp <= 0x08FF or   # Arabic Extended-A
                0xFB50 <= cp <= 0xFDFF or   # Arabic Presentation Forms-A
                0xFE70 <= cp <= 0xFEFF):    # Arabic Presentation Forms-B
                arabic_count += 1
    if total_count == 0:
        return False
    return arabic_count / total_count > 0.5


def _extract_text_from_page(url):
    """Scrape a duas.org static HTML page and extract Arabic and English text."""
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    resp.encoding = resp.apparent_encoding or 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Remove script and style elements
    for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
        tag.decompose()

    arabic_lines = []
    english_lines = []

    for element in soup.find_all(['p', 'td', 'div', 'span', 'font', 'b', 'i']):
        text = element.get_text(separator=' ', strip=True)
        if not text or len(text) < 3:
            continue

        if any(skip in text.lower() for skip in [
            'copyright', 'duas.org', 'click here', 'back to',
            'home page', 'email', 'www.', 'http', 'bookmark',
            'javascript', 'mp3', 'download', '.wav', '.rm',
        ]):
            continue

        if _is_arabic(text):
            if text not in arabic_lines:
                arabic_lines.append(text)
        else:
            cleaned = text.strip()
            if cleaned and cleaned not in english_lines:
                english_lines.append(cleaned)

    return {
        "text_arabic": "\n".join(arabic_lines),
        "text_english": "\n".join(english_lines),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Download logic
# ──────────────────────────────────────────────────────────────────────────────

def download_mafatih_dua(dua_info, data_dir):
    """Download a single Mafatih dua (API first, then HTML fallback)."""
    slug = dua_info["slug"]
    out_file = os.path.join(data_dir, f"{slug}.json")

    if os.path.exists(out_file):
        # Check if existing file has actual content
        try:
            with open(out_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
            ar_len = len(existing.get("text_arabic", ""))
            en_len = len(existing.get("text_english", ""))
            if ar_len > 0 or en_len > 0:
                print(f"  [skip] {slug} already downloaded ({ar_len} ar, {en_len} en chars)")
                return
            else:
                print(f"  [re-download] {slug} exists but has no content, retrying...")
        except Exception:
            pass  # File is corrupt, re-download

    api_id = dua_info.get("api_id")
    static_url = dua_info.get("static_url")

    # Strategy 1: JSON API
    if api_id:
        print(f"  Downloading {slug} via API (id={api_id})...")
        try:
            api_data = _download_api_json(api_id)
            result = _api_json_to_our_format(api_data, {
                "name_arabic": dua_info["name_arabic"],
                "name_english": dua_info["name_english"],
                "category": "mafatih",
                "attributed_to": dua_info["attributed_to"],
                "occasion": dua_info["occasion"],
                "source_book": dua_info["source_book"],
            })

            os.makedirs(data_dir, exist_ok=True)
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            ar_len = len(result["text_arabic"])
            en_len = len(result["text_english"])
            n_segs = len(result.get("segments", []))
            print(f"  [done] {slug}: {ar_len} chars Arabic, {en_len} chars English, {n_segs} segments")
            return

        except Exception as e:
            print(f"  [api-error] {slug}: {e}")

    # Strategy 2: Static HTML scraping
    if static_url:
        print(f"  Downloading {slug} via HTML scraping ({static_url})...")
        try:
            extracted = _extract_text_from_page(static_url)
            result = {
                "name_arabic": dua_info["name_arabic"],
                "name_english": dua_info["name_english"],
                "text_arabic": extracted["text_arabic"],
                "text_english": extracted["text_english"],
                "category": "mafatih",
                "attributed_to": dua_info["attributed_to"],
                "occasion": dua_info["occasion"],
                "source_url": static_url,
                "source_book": dua_info["source_book"],
            }

            os.makedirs(data_dir, exist_ok=True)
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            ar_len = len(extracted["text_arabic"])
            en_len = len(extracted["text_english"])
            print(f"  [done] {slug}: {ar_len} chars Arabic, {en_len} chars English (HTML scrape)")
            return

        except Exception as e:
            print(f"  [html-error] {slug}: {e}")

    # Strategy 3: Not available
    print(f"  [unavailable] {slug}: not found in API or static HTML (site restructured)")


def download_sahifa_supplication(api_id, number, data_dir):
    """Download a Sahifa al-Sajjadiya supplication from the API."""
    out_file = os.path.join(data_dir, f"supplication_{number:02d}.json")

    if os.path.exists(out_file):
        try:
            with open(out_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
            ar_len = len(existing.get("text_arabic", ""))
            if ar_len > 0:
                print(f"  [skip] supplication_{number:02d} already downloaded")
                return
        except Exception:
            pass

    print(f"  Downloading supplication {number} (id={api_id})...")

    try:
        api_data = _download_api_json(api_id)
        result = _api_json_to_our_format(api_data, {
            "name_arabic": "",
            "name_english": api_data.get("title", f"Sahifa al-Sajjadiya - Supplication {number}"),
            "category": "sahifa",
            "attributed_to": "imam_sajjad",
            "occasion": "",
            "source_book": "Sahifa al-Sajjadiya",
        })

        os.makedirs(data_dir, exist_ok=True)
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        ar_len = len(result["text_arabic"])
        en_len = len(result["text_english"])
        n_segs = len(result.get("segments", []))
        print(f"  [done] supplication_{number:02d}: {ar_len} chars Arabic, {en_len} chars English, {n_segs} segments")

    except Exception as e:
        print(f"  [error] supplication {number}: {e}")


def download_all_available_duas(data_dir):
    """Download ALL available duas from the duas.org search index.

    This fetches every dua that has a JSON data file, beyond just the
    specific mafatih/sahifa ones. Saves to data_dir/all/.
    """
    all_dir = os.path.join(data_dir, '..', 'all')
    all_dir = os.path.abspath(all_dir)
    os.makedirs(all_dir, exist_ok=True)

    print("  Fetching search index...")
    try:
        resp = requests.get(f"{API_BASE}/search_index.json", headers=HEADERS, timeout=30)
        resp.raise_for_status()
        index = resp.json()
    except Exception as e:
        print(f"  [error] Could not fetch search index: {e}")
        return

    total = len(index)
    downloaded = 0
    skipped = 0
    errors = 0

    for i, item in enumerate(index, 1):
        dua_id = item.get("id", "")
        title = item.get("title", "unknown")
        out_file = os.path.join(all_dir, f"{dua_id}.json")

        if os.path.exists(out_file):
            skipped += 1
            continue

        print(f"  [{i}/{total}] {dua_id}...")
        try:
            api_data = _download_api_json(dua_id)

            # Save the raw API data plus index metadata
            api_data["_index_meta"] = item
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(api_data, f, ensure_ascii=False, indent=2)

            downloaded += 1
        except Exception as e:
            print(f"    [error] {dua_id}: {e}")
            errors += 1

        time.sleep(DELAY)

    print(f"\n  All duas: {downloaded} downloaded, {skipped} skipped, {errors} errors (of {total} total)")


def download_duas(mafatih_dir=MAFATIH_DIR, sahifa_dir=SAHIFA_DIR):
    """Download all duas (Mafatih + Sahifa + all available)."""
    mafatih_dir = os.path.abspath(mafatih_dir)
    sahifa_dir = os.path.abspath(sahifa_dir)
    os.makedirs(mafatih_dir, exist_ok=True)
    os.makedirs(sahifa_dir, exist_ok=True)

    # ── Mafatih al-Jinan ──
    print("=== Mafatih al-Jinan ===")
    available_count = 0
    unavailable = []
    for i, dua in enumerate(MAFATIH_DUAS, 1):
        print(f"\n[{i}/{len(MAFATIH_DUAS)}] {dua['name_english']}")
        download_mafatih_dua(dua, mafatih_dir)

        if not dua.get("api_id") and not dua.get("static_url"):
            unavailable.append(dua["name_english"])
        else:
            available_count += 1

        time.sleep(DELAY)

    if unavailable:
        print(f"\n  NOTE: {len(unavailable)} duas unavailable due to site restructuring:")
        for name in unavailable:
            print(f"    - {name}")

    # ── Sahifa al-Sajjadiya ──
    print("\n\n=== Sahifa al-Sajjadiya ===")
    print("  NOTE: The original 54 supplications at sahifasajjadia/dua{1-54}.htm")
    print("        are no longer available (duas.org site restructured).")
    print(f"        {len(SAHIFA_API_IDS)} supplication(s) available via the new API.")

    for i, api_id in enumerate(SAHIFA_API_IDS, 1):
        # Extract dua number from ID if possible
        num = 44  # Default for the known one
        print(f"\n[{i}/{len(SAHIFA_API_IDS)}]")
        download_sahifa_supplication(api_id, num, sahifa_dir)
        time.sleep(DELAY)

    # ── All available duas ──
    print("\n\n=== All Available Duas (full index) ===")
    download_all_available_duas(mafatih_dir)


if __name__ == '__main__':
    print("Downloading duas from duas.org...")
    print(f"  {len(MAFATIH_DUAS)} Mafatih duas (some may be unavailable)")
    print(f"  {len(SAHIFA_API_IDS)} Sahifa supplication(s)")
    print(f"  Plus all available duas from search index\n")
    download_duas()
    print("\nDone.")
