"""Check that a clone of the eval sample is at the pinned commit and that the files L6 relies on hash as recorded.

Usage: python -I tools/verify_pinned.py SAMPLE_DIR. Exit code 0 when every hash matches.
"""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    sample = sys.argv[1]
    pinned = json.load(open(os.path.join(ROOT, "levels", "L6", "PINNED.json"), encoding="utf-8"))
    head = subprocess.run(["git", "-C", sample, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    bad = []
    if head != pinned["commit"]:
        bad.append(f"HEAD is {head}, pinned {pinned['commit']}")
    for rel, want in pinned["sha256"].items():
        with open(os.path.join(sample, rel), "rb") as fh:
            got = hashlib.sha256(fh.read()).hexdigest()
        if got != want:
            bad.append(f"{rel}: sha256 {got} != pinned {want}")
    if bad:
        sys.exit("pinned sample check FAILED: " + "; ".join(bad))
    print(f"pinned sample OK at {head}: {len(pinned['sha256'])} files match")


if __name__ == "__main__":
    main()
