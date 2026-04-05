"""Download Shia hadith collections from ThaqalaynAPI.

Fetches hadiths one-by-one from https://www.thaqalayn-api.net/api/v2/{bookId}/{id}
for Al-Kafi (8 volumes) and Man La Yahduruh al-Faqih (5 volumes).
"""

import os
import json
import time
import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'hadith', 'shia')
API_BASE = "https://www.thaqalayn-api.net/api/v2"

# Book ID -> max hadith ID (inclusive)
BOOKS = {
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

DELAY = 0.2  # seconds between requests


def download_book(book_id, max_id, data_dir):
    """Download all hadiths for a single book/volume."""
    out_file = os.path.join(data_dir, f"{book_id}.json")
    if os.path.exists(out_file):
        print(f"  [skip] {book_id} already downloaded")
        return

    print(f"  Downloading {book_id} (IDs 1-{max_id})...")
    hadiths = []
    errors = 0
    not_found = 0

    for hadith_id in range(1, max_id + 1):
        url = f"{API_BASE}/{book_id}/{hadith_id}"
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 404:
                not_found += 1
                time.sleep(DELAY)
                continue
            resp.raise_for_status()
            data = resp.json()
            hadiths.append(data)
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                not_found += 1
            else:
                errors += 1
                if errors <= 5:
                    print(f"    [error] {book_id}/{hadith_id}: {e}")
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"    [error] {book_id}/{hadith_id}: {e}")

        if hadith_id % 100 == 0:
            print(f"    {book_id}: {hadith_id}/{max_id} fetched ({len(hadiths)} collected, {not_found} not found)")

        time.sleep(DELAY)

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(hadiths, f, ensure_ascii=False, indent=2)

    print(f"  [done] {book_id}: {len(hadiths)} hadiths saved ({not_found} IDs not found, {errors} errors)")


def download_shia_hadith(data_dir=DATA_DIR):
    """Download all Shia hadith collections."""
    data_dir = os.path.abspath(data_dir)
    os.makedirs(data_dir, exist_ok=True)

    total_books = len(BOOKS)
    for i, (book_id, max_id) in enumerate(BOOKS.items(), 1):
        print(f"\n[{i}/{total_books}] {book_id}")
        download_book(book_id, max_id, data_dir)


if __name__ == '__main__':
    print("Downloading Shia hadith from ThaqalaynAPI...")
    print(f"  {len(BOOKS)} books, {sum(BOOKS.values())} total IDs to check")
    print(f"  Estimated time: ~{sum(BOOKS.values()) * DELAY / 60:.0f} minutes\n")
    download_shia_hadith()
    print("\nDone.")
