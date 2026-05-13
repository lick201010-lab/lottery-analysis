#!/usr/bin/env python3
"""
Unified MarkSix data update script.
Usage: python scripts/update.py
"""
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.resolve()
ROOT_DIR = SCRIPTS_DIR.parent

def run(name, *args):
    print(f"\n{'='*50}")
    print(f"Running: {name}")
    print(f"{'='*50}")
    result = subprocess.run(
        [sys.executable, *args],
        cwd=ROOT_DIR,
        capture_output=False,
    )
    if result.returncode != 0:
        print(f"ERROR: {name} failed with code {result.returncode}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    run("Fetch from lottery.hk", str(SCRIPTS_DIR / "fetch_marksix.py"))
    run("Merge & recalculate", str(SCRIPTS_DIR / "merge_marksix.py"))
    print("\n✅ Update complete!")
