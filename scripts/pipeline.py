"""Run the full Quran import pipeline.

Usage:
    python scripts/pipeline.py              # Run all steps
    python scripts/pipeline.py --step download_tanzil   # Run only one step
    python scripts/pipeline.py --from import_arabic  # Start from a specific step
"""

import sys
import os
import time
import argparse
import importlib

# Ensure project root is on the path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)


def load_func(module_path, func_name):
    """Dynamically import a function from a module path."""
    mod = importlib.import_module(module_path)
    return getattr(mod, func_name)


# Lazy step definitions: (step_name, description, module_path, function_name)
STEP_DEFS = [
    ('schema', 'Create database schema',
     'scripts.import.create_schema', 'create_schema'),
    ('download_tanzil', 'Download Quran Arabic from Tanzil.net',
     'scripts.download.download_tanzil', 'download_tanzil'),
    ('download_translations', 'Download English translation',
     'scripts.download.download_translations', 'download_translation'),
    ('download_transliteration', 'Download transliteration',
     'scripts.download.download_translations', 'download_transliteration'),
    ('download_morphology', 'Download morphology data',
     'scripts.download.download_morphology', 'download_morphology'),
    ('import_arabic', 'Import Quran Arabic text',
     'scripts.import.import_quran_arabic', 'import_quran_arabic'),
    ('import_english', 'Import English translation',
     'scripts.import.import_translations', 'import_english'),
    ('import_transliteration', 'Import transliteration',
     'scripts.import.import_translations', 'import_transliteration'),
    ('import_morphology', 'Import morphology (words)',
     'scripts.import.import_morphology', 'import_morphology'),
    ('generate_letters', 'Generate letter breakdown',
     'scripts.import.generate_letters', 'generate_letters'),
    ('calculate_abjad', 'Calculate Abjad values',
     'scripts.import.calculate_abjad', 'calculate_abjad'),
    ('calculate_statistics', 'Calculate statistics',
     'scripts.import.calculate_statistics', 'calculate_statistics'),
    ('verify', 'Verify integrity',
     'scripts.verify.verify_integrity', 'verify'),
]


def run_pipeline(step_name=None, start_from=None):
    print("=" * 60)
    print("  Islamic Hive Mind - Quran Import Pipeline")
    print("=" * 60)
    print()

    steps = STEP_DEFS[:]

    if step_name:
        steps = [s for s in steps if s[0] == step_name]
        if not steps:
            print(f"Unknown step: {step_name}")
            print(f"Available: {', '.join(s[0] for s in STEP_DEFS)}")
            return False

    if start_from:
        found = False
        filtered = []
        for s in STEP_DEFS:
            if s[0] == start_from:
                found = True
            if found:
                filtered.append(s)
        if not found:
            print(f"Unknown step: {start_from}")
            return False
        steps = filtered

    total = len(steps)
    passed = 0

    for i, (name, desc, mod_path, func_name) in enumerate(steps, 1):
        print(f"\n[{i}/{total}] {desc} ({name})")
        print("-" * 40)

        start = time.time()
        try:
            func = load_func(mod_path, func_name)
            result = func()
            elapsed = time.time() - start
            if result is False:
                print(f"  [warn] Step completed with warnings ({elapsed:.1f}s)")
            else:
                print(f"  [ok] Done ({elapsed:.1f}s)")
                passed += 1
        except Exception as e:
            elapsed = time.time() - start
            print(f"  [error] ({elapsed:.1f}s): {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'=' * 60}")
    print(f"  Pipeline complete: {passed}/{total} steps successful")
    print(f"{'=' * 60}")

    return passed == total


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Quran Import Pipeline')
    parser.add_argument('--step', help='Run only this step')
    parser.add_argument('--from', dest='start_from', help='Start from this step')
    args = parser.parse_args()

    success = run_pipeline(step_name=args.step, start_from=args.start_from)
    sys.exit(0 if success else 1)
