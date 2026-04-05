"""Download duas from duas.org.

Scrapes key Mafatih al-Jinan duas and the complete Sahifa al-Sajjadiya
(54 supplications). Extracts Arabic and English text from HTML pages.
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

# Key Mafatih duas with metadata
MAFATIH_DUAS = [
    {
        "slug": "kumayl",
        "url": "https://www.duas.org/kumayl.htm",
        "name_english": "Dua Kumayl",
        "name_arabic": "دعاء كميل",
        "name_transliteration": "Du'a Kumayl",
        "attributed_to": "Imam Ali (a.s.)",
        "occasion": "Thursday nights",
        "source_book": "Mafatih al-Jinan",
    },
    {
        "slug": "tawassul",
        "url": "https://www.duas.org/tawassul.htm",
        "name_english": "Dua Tawassul",
        "name_arabic": "دعاء التوسل",
        "name_transliteration": "Du'a al-Tawassul",
        "attributed_to": "Imam al-Mahdi (a.s.)",
        "occasion": "Seeking intercession",
        "source_book": "Mafatih al-Jinan",
    },
    {
        "slug": "nudba",
        "url": "https://www.duas.org/nudba.htm",
        "name_english": "Dua Nudba",
        "name_arabic": "دعاء الندبة",
        "name_transliteration": "Du'a al-Nudba",
        "attributed_to": "Imam al-Sadiq (a.s.)",
        "occasion": "Fridays, Eids",
        "source_book": "Mafatih al-Jinan",
    },
    {
        "slug": "arafah-hussain",
        "url": "https://www.duas.org/arafathusain.htm",
        "name_english": "Dua Arafah of Imam Hussain",
        "name_arabic": "دعاء عرفة للإمام الحسين",
        "name_transliteration": "Du'a 'Arafah",
        "attributed_to": "Imam Hussain (a.s.)",
        "occasion": "Day of Arafah",
        "source_book": "Mafatih al-Jinan",
    },
    {
        "slug": "abu-hamza-thumali",
        "url": "https://www.duas.org/abuhamza.htm",
        "name_english": "Dua Abu Hamza al-Thumali",
        "name_arabic": "دعاء أبي حمزة الثمالي",
        "name_transliteration": "Du'a Abi Hamza al-Thumali",
        "attributed_to": "Imam Zayn al-Abidin (a.s.)",
        "occasion": "Pre-dawn (sahar) of Ramadan",
        "source_book": "Mafatih al-Jinan",
    },
    {
        "slug": "jawshan-kabir",
        "url": "https://www.duas.org/jkabir.htm",
        "name_english": "Dua Jawshan al-Kabir",
        "name_arabic": "دعاء الجوشن الكبير",
        "name_transliteration": "Du'a al-Jawshan al-Kabir",
        "attributed_to": "Prophet Muhammad (s.a.w.)",
        "occasion": "Nights of Ramadan, Qadr nights",
        "source_book": "Mafatih al-Jinan",
    },
    {
        "slug": "ziyarat-ashura",
        "url": "https://www.duas.org/ashura.htm",
        "name_english": "Ziyarat Ashura",
        "name_arabic": "زيارة عاشوراء",
        "name_transliteration": "Ziyarat 'Ashura",
        "attributed_to": "Imam al-Baqir (a.s.)",
        "occasion": "Day of Ashura, any time",
        "source_book": "Mafatih al-Jinan",
    },
    {
        "slug": "ziyarat-arbaeen",
        "url": "https://www.duas.org/ziaraat/Arbain.htm",
        "name_english": "Ziyarat Arba'een",
        "name_arabic": "زيارة الأربعين",
        "name_transliteration": "Ziyarat al-Arba'in",
        "attributed_to": "Imam al-Hadi (a.s.)",
        "occasion": "20th Safar (Arba'een)",
        "source_book": "Mafatih al-Jinan",
    },
    {
        "slug": "ziyarat-aminullah",
        "url": "https://www.duas.org/ziaraat/aminallah.htm",
        "name_english": "Ziyarat Aminullah",
        "name_arabic": "زيارة أمين الله",
        "name_transliteration": "Ziyarat Amin Allah",
        "attributed_to": "Imam Zayn al-Abidin (a.s.)",
        "occasion": "Visiting shrines of Imams",
        "source_book": "Mafatih al-Jinan",
    },
    {
        "slug": "makarim-al-akhlaq",
        "url": "https://www.duas.org/sahifasajjadia/dua20.htm",
        "name_english": "Dua Makarim al-Akhlaq",
        "name_arabic": "دعاء مكارم الأخلاق",
        "name_transliteration": "Du'a Makarim al-Akhlaq",
        "attributed_to": "Imam Zayn al-Abidin (a.s.)",
        "occasion": "Noble character traits",
        "source_book": "Sahifa al-Sajjadiya",
    },
]


def _is_arabic(text):
    """Check if a string contains predominantly Arabic characters."""
    if not text or not text.strip():
        return False
    arabic_count = 0
    total_count = 0
    for char in text:
        if unicodedata.category(char).startswith('L'):
            total_count += 1
            # Arabic Unicode blocks
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
    """Scrape a duas.org page and extract Arabic and English text."""
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    # Try different encodings
    resp.encoding = resp.apparent_encoding or 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Remove script and style elements
    for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
        tag.decompose()

    arabic_lines = []
    english_lines = []

    # Strategy: walk through all text-bearing elements and classify
    # duas.org typically uses <p>, <td>, <div>, <span> for content
    for element in soup.find_all(['p', 'td', 'div', 'span', 'font', 'b', 'i']):
        text = element.get_text(separator=' ', strip=True)
        if not text or len(text) < 3:
            continue

        # Skip navigation/boilerplate
        if any(skip in text.lower() for skip in [
            'copyright', 'duas.org', 'click here', 'back to',
            'home page', 'email', 'www.', 'http', 'bookmark',
            'javascript', 'mp3', 'download', '.wav', '.rm',
        ]):
            continue

        if _is_arabic(text):
            # Avoid duplicate lines from nested elements
            if text not in arabic_lines:
                arabic_lines.append(text)
        else:
            # English or transliteration
            cleaned = text.strip()
            if cleaned and cleaned not in english_lines:
                english_lines.append(cleaned)

    return {
        "text_arabic": "\n".join(arabic_lines),
        "text_english": "\n".join(english_lines),
    }


def download_mafatih_dua(dua_info, data_dir):
    """Download a single Mafatih dua."""
    slug = dua_info["slug"]
    out_file = os.path.join(data_dir, f"{slug}.json")

    if os.path.exists(out_file):
        print(f"  [skip] {slug} already downloaded")
        return

    url = dua_info["url"]
    print(f"  Downloading {slug} from {url}...")

    try:
        extracted = _extract_text_from_page(url)

        result = {
            "name_arabic": dua_info["name_arabic"],
            "name_english": dua_info["name_english"],
            "name_transliteration": dua_info["name_transliteration"],
            "text_arabic": extracted["text_arabic"],
            "text_english": extracted["text_english"],
            "category": "mafatih",
            "attributed_to": dua_info["attributed_to"],
            "occasion": dua_info["occasion"],
            "source_url": url,
            "source_book": dua_info["source_book"],
        }

        os.makedirs(data_dir, exist_ok=True)
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        ar_len = len(extracted["text_arabic"])
        en_len = len(extracted["text_english"])
        print(f"  [done] {slug}: {ar_len} chars Arabic, {en_len} chars English")

    except Exception as e:
        print(f"  [error] {slug}: {e}")


def download_sahifa_supplication(number, data_dir):
    """Download a single Sahifa al-Sajjadiya supplication."""
    out_file = os.path.join(data_dir, f"supplication_{number:02d}.json")

    if os.path.exists(out_file):
        print(f"  [skip] supplication_{number:02d} already downloaded")
        return

    url = f"https://www.duas.org/sahifasajjadia/dua{number}.htm"
    print(f"  Downloading supplication {number}/54...")

    try:
        extracted = _extract_text_from_page(url)

        result = {
            "name_arabic": "",
            "name_english": f"Sahifa al-Sajjadiya - Supplication {number}",
            "name_transliteration": "",
            "text_arabic": extracted["text_arabic"],
            "text_english": extracted["text_english"],
            "category": "sahifa",
            "attributed_to": "Imam Zayn al-Abidin (a.s.)",
            "occasion": "",
            "source_url": url,
            "source_book": "Sahifa al-Sajjadiya",
        }

        os.makedirs(data_dir, exist_ok=True)
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        ar_len = len(extracted["text_arabic"])
        en_len = len(extracted["text_english"])
        print(f"  [done] supplication_{number:02d}: {ar_len} chars Arabic, {en_len} chars English")

    except Exception as e:
        print(f"  [error] supplication {number}: {e}")


def download_duas(mafatih_dir=MAFATIH_DIR, sahifa_dir=SAHIFA_DIR):
    """Download all duas (Mafatih + Sahifa)."""
    mafatih_dir = os.path.abspath(mafatih_dir)
    sahifa_dir = os.path.abspath(sahifa_dir)
    os.makedirs(mafatih_dir, exist_ok=True)
    os.makedirs(sahifa_dir, exist_ok=True)

    # Download Mafatih duas
    print("=== Mafatih al-Jinan ===")
    for i, dua in enumerate(MAFATIH_DUAS, 1):
        print(f"\n[{i}/{len(MAFATIH_DUAS)}] {dua['name_english']}")
        download_mafatih_dua(dua, mafatih_dir)
        time.sleep(DELAY)

    # Download Sahifa al-Sajjadiya (54 supplications)
    # Note: supplication 20 (Makarim al-Akhlaq) is also in Mafatih above,
    # but we download it separately here as part of the complete Sahifa
    print("\n\n=== Sahifa al-Sajjadiya ===")
    for num in range(1, 55):
        print(f"\n[{num}/54]")
        download_sahifa_supplication(num, sahifa_dir)
        time.sleep(DELAY)


if __name__ == '__main__':
    print("Downloading duas from duas.org...")
    print(f"  {len(MAFATIH_DUAS)} Mafatih duas + 54 Sahifa supplications\n")
    download_duas()
    print("\nDone.")
