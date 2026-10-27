"""L0 grader (deliberately weak; see docs/HOLES.md after you solve it).

Usage: python grader.py ANSWER.json [KEY_DIR]. Exit code 0 on PASS.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from wargame.common import main, verdict  # noqa: E402

FIELDS = {"chain": str, "resnum": int, "resname": str, "min_distance": (int, float)}


def grade(answer_path, key_dir=HERE):
    with open(answer_path, encoding="utf-8") as fh:
        obj = json.load(fh)
    items = obj.get("epitope") if isinstance(obj, dict) else None
    if not isinstance(items, list) or not items:
        return verdict(False, ["epitope must be a non-empty list"])
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            return verdict(False, [f"epitope[{i}] must be an object"])
        for f, t in FIELDS.items():
            if not isinstance(it.get(f), t):
                return verdict(False, [f"epitope[{i}].{f} has the wrong type"])
    return verdict(True, ["answer is well formed"], n_answer=len(items))


if __name__ == "__main__":
    main(grade, HERE)
