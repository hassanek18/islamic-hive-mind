"""Download Sunni hadith collections from hadith-json GitHub repository.

Downloads the 6 canonical books (Kutub al-Sittah) as JSON files from:
https://github.com/AhmedBaset/hadith-json
"""

import os
import json
import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'hadith', 'sunni')
BASE_URL = "https://raw.githubusercontent.com/AhmedBaset/hadith-json/main/db/by_book/the_9_books"

# The 6 canonical Sunni hadith collections
BOOKS = [
    "bukhari",
    "muslim",
    "abudawud",
    "tirmidhi",
    "nasai",
    "ibnmajah",
]


def download_book(slug, data_dir):
    """Download a single hadith book from GitHub."""
    out_file = os.path.join(data_dir, f"{slug}.json")
    if os.path.exists(out_file):
        print(f"  [skip] {slug} already downloaded")
        return

    url = f"{BASE_URL}/{slug}.json"
    print(f"  Downloading {slug}...")

    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        os.makedirs(data_dir, exist_ok=True)
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        hadith_count = len(data.get('hadiths', []))
        print(f"  [done] {slug}: {hadith_count} hadiths saved")

    except Exception as e:
        print(f"  [error] {slug}: {e}")


def download_sunni_hadith(data_dir=DATA_DIR):
    """Download all 6 Sunni hadith collections."""
    data_dir = os.path.abspath(data_dir)
    os.makedirs(data_dir, exist_ok=True)

    for i, slug in enumerate(BOOKS, 1):
        print(f"\n[{i}/{len(BOOKS)}] {slug}")
        download_book(slug, data_dir)


if __name__ == '__main__':
    print("Downloading Sunni hadith from GitHub (hadith-json)...")
    download_sunni_hadith()
    print("\nDone.")
