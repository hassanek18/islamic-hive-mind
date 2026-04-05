"""Download English translation and transliteration from Quran.com API v4.

Uses the /verses/by_chapter endpoint which returns translations inline.
Sahih International = resource_id 20
Transliteration = resource_id 57
"""

import os
import json
import time
import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'quran')
API_BASE = "https://api.quran.com/api/v4"

# Verse counts per surah (to set per_page correctly)
VERSE_COUNTS = [
    7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,110,98,135,
    112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,182,88,75,85,54,53,89,
    59,37,35,38,29,18,45,60,49,62,55,78,96,29,22,24,13,14,11,11,18,12,12,30,
    52,52,44,28,28,20,56,40,31,50,40,46,42,29,19,36,25,22,17,19,26,30,20,15,
    21,11,8,8,19,5,8,8,11,11,8,3,9,5,4,7,3,6,3,5,4,5,6
]


def _download_resource(resource_id, resource_type, out_file, label):
    """Download a translation/transliteration resource for all 114 surahs."""
    if os.path.exists(out_file):
        print(f"  [skip] {label} already downloaded")
        return

    print(f"  Downloading {label}...")
    all_verses = []

    for surah in range(1, 115):
        per_page = VERSE_COUNTS[surah - 1]
        url = f"{API_BASE}/verses/by_chapter/{surah}"
        params = {
            'translations': str(resource_id),
            'per_page': per_page,
            'page': 1,
        }

        try:
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            for v in data.get('verses', []):
                verse_key = v.get('verse_key', f'{surah}:?')
                translations = v.get('translations', [])
                text = ''
                if translations:
                    text = translations[0].get('text', '')
                all_verses.append({
                    'verse_key': verse_key,
                    'text': text,
                })

            if surah % 10 == 0:
                print(f"    Surah {surah}/114 done ({len(all_verses)} verses so far)")

        except Exception as e:
            print(f"    [error] Surah {surah}: {e}")

        time.sleep(0.2)  # Rate limiting

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(all_verses, f, ensure_ascii=False, indent=2)

    print(f"  [done] {len(all_verses)} verses saved")


def download_translation(data_dir=DATA_DIR):
    """Download Sahih International English translation."""
    data_dir = os.path.abspath(data_dir)
    out_file = os.path.join(data_dir, 'translations', 'en-sahih-international.json')
    _download_resource(20, 'translation', out_file, 'Sahih International translation')


def download_transliteration(data_dir=DATA_DIR):
    """Download transliteration."""
    data_dir = os.path.abspath(data_dir)
    out_file = os.path.join(data_dir, 'transliteration', 'transliteration.json')
    _download_resource(57, 'transliteration', out_file, 'Transliteration')


if __name__ == '__main__':
    print("Downloading from Quran.com API v4...")
    download_translation()
    download_transliteration()
