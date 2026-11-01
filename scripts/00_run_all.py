#!/usr/bin/env python3
"""Run the manuscript analyses in order.

This wrapper assumes scripts 01--07 are present in the same directory.
It stops immediately if any analysis fails.
"""

from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent

SCRIPTS = [
    "01_tomats_audit_lift.py",
    "02_tomats_cross_overlap.py",
    "03_tomats_filtered_agreement.py",
    "04_brighter_diagnostics.py",
    "05_goemotions_diagnostics.py",
    "06_goemotions_split_half_reliability.py",
    "07_goemotions_pair_permutation.py",
]

for script_name in SCRIPTS:
    script = HERE / script_name
    if not script.exists():
        raise FileNotFoundError(
            f"Missing {script_name}. Add the existing manuscript analysis script to scripts/."
        )
    print(f"\n=== Running {script_name} ===", flush=True)
    subprocess.run([sys.executable, str(script)], check=True)

print("\nAll manuscript analyses completed successfully.")
