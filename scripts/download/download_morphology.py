"""Download morphological data from the Quranic Arabic Corpus (Leeds University).

The corpus provides word-by-word analysis with root, lemma, POS, and morphology.
Available at: https://corpus.quran.com
Data format: tab-separated with columns for location, form, tag, features.
"""

import os
import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'quran', 'morphology')

# The Quranic Arabic Corpus morphological data
# This is a publicly available dataset from Leeds University
CORPUS_URL = "https://raw.githubusercontent.com/q-ran/quran/master/data/quranic-corpus-morphology-0.4.txt"
ALT_URLS = [
    "https://raw.githubusercontent.com/mustafa0x/quran-morphology/master/quranic-corpus-morphology-0.4.txt",
    "https://corpus.quran.com/download/quranic-corpus-morphology-0.4.txt",
]


def download_morphology(data_dir=DATA_DIR):
    data_dir = os.path.abspath(data_dir)
    os.makedirs(data_dir, exist_ok=True)

    filepath = os.path.join(data_dir, 'quranic-corpus-morphology.txt')
    if os.path.exists(filepath):
        print("  [skip] Morphology data already exists")
        return

    print("  Downloading Quranic Arabic Corpus morphology data...")

    urls_to_try = [CORPUS_URL] + ALT_URLS
    for url in urls_to_try:
        try:
            print(f"    Trying: {url}")
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()

            content = resp.text
            # Verify it looks like morphology data (has location markers like (1:1:1:1))
            if '(1:1:1' in content[:5000]:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  [done] Morphology data saved ({len(content)} bytes)")
                return
            else:
                print(f"    [warn] Content doesn't look like morphology data, trying next URL...")
        except Exception as e:
            print(f"    [error] {url}: {e}")

    print("  [warn] Could not download morphology data automatically.")
    print("         Please download manually from https://corpus.quran.com/download/")
    print(f"         Save as: {filepath}")

    # Create a placeholder README
    readme = os.path.join(data_dir, 'README.md')
    with open(readme, 'w') as f:
        f.write("# Morphology Data\n\n")
        f.write("Download from: https://corpus.quran.com/download/\n")
        f.write("Save the morphology file as `quranic-corpus-morphology.txt` in this directory.\n")


if __name__ == '__main__':
    download_morphology()
