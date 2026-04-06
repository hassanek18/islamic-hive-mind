"""Run the Phase 2 import pipeline: hadiths, duas, and verification.

Usage:
    python scripts/pipeline_phase2.py                     # Run all steps
    python scripts/pipeline_phase2.py --step import_sunni # Run only one step
    python scripts/pipeline_phase2.py --from import_shia  # Start from a specific step
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
    ('schema', 'Create hadith/dua/narrator schema',
     'scripts.import.create_hadith_schema', 'create_hadith_schema'),
    ('download_sunni', 'Download Sunni hadith collections',
     'scripts.download.download_sunni_hadith', 'download_sunni_hadith'),
    ('download_shia', 'Download Shia hadith collections',
     'scripts.download.download_shia_hadith', 'download_shia_hadith'),
    ('download_duas', 'Download duas from duas.org',
     'scripts.download.download_duas', 'download_duas'),
    ('import_sunni', 'Import Sunni hadiths',
     'scripts.import.import_sunni_hadith', 'import_sunni_hadith'),
    ('import_shia', 'Import Shia hadiths',
     'scripts.import.import_shia_hadith', 'import_shia_hadith'),
    ('import_duas', 'Import duas',
     'scripts.import.import_duas', 'import_duas'),
    ('verify', 'Verify hadith and dua integrity',
     'scripts.verify.verify_hadith_integrity', 'verify_hadith_integrity'),
]


def run_pipeline(step_name=None, start_from=None):
    print("=" * 60)
    print("  Islamic Hive Mind - Phase 2 Import Pipeline")
    print("  (Hadiths, Duas, Narrators)")
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
    parser = argparse.ArgumentParser(description='Phase 2 Import Pipeline')
    parser.add_argument('--step', help='Run only this step')
    parser.add_argument('--from', dest='start_from', help='Start from this step')
    args = parser.parse_args()

    success = run_pipeline(step_name=args.step, start_from=args.start_from)
    sys.exit(0 if success else 1)
