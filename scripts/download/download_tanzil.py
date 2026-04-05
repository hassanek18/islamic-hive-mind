"""Download Quran Arabic text from Tanzil.net (Uthmani + Simple scripts)."""

import os
import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'quran')

TANZIL_BASE = "https://tanzil.net/pub/download/index.php"

# Tanzil provides direct text downloads
DOWNLOADS = {
    'quran-uthmani.txt': {
        'url': 'https://tanzil.net/pub/download/index.php',
        'params': {'quranType': 'uthmani', 'outType': 'txt-2', 'agree': 'true'},
        'desc': 'Uthmani script (with diacritics)'
    },
    'quran-simple.txt': {
        'url': 'https://tanzil.net/pub/download/index.php',
        'params': {'quranType': 'simple', 'outType': 'txt-2', 'agree': 'true'},
        'desc': 'Simple script (no diacritics)'
    },
    'quran-uthmani.xml': {
        'url': 'https://tanzil.net/pub/download/index.php',
        'params': {'quranType': 'uthmani', 'outType': 'xml', 'agree': 'true'},
        'desc': 'Uthmani XML format'
    },
    'quran-simple.xml': {
        'url': 'https://tanzil.net/pub/download/index.php',
        'params': {'quranType': 'simple', 'outType': 'xml', 'agree': 'true'},
        'desc': 'Simple XML format'
    },
}


def download_tanzil(data_dir=DATA_DIR):
    data_dir = os.path.abspath(data_dir)
    os.makedirs(data_dir, exist_ok=True)

    for filename, info in DOWNLOADS.items():
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            print(f"  [skip] {filename} already exists")
            continue

        print(f"  Downloading {info['desc']} -> {filename}...")
        try:
            resp = requests.get(info['url'], params=info['params'], timeout=60)
            resp.raise_for_status()

            # Tanzil may return HTML if params are wrong; check content
            content = resp.text
            if '<html' in content[:500].lower() and 'bismillah' not in content[:2000].lower():
                print(f"  [warn] {filename}: got HTML instead of Quran text, trying alternate URL...")
                # Try direct URL format
                alt_url = f"https://tanzil.net/pub/download/{filename}"
                resp = requests.get(alt_url, timeout=60)
                resp.raise_for_status()
                content = resp.text

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  [done] {filename} ({len(content)} bytes)")
        except Exception as e:
            print(f"  [error] {filename}: {e}")

    print(f"\nTanzil data directory: {data_dir}")


if __name__ == '__main__':
    print("Downloading Quran text from Tanzil.net...")
    download_tanzil()
