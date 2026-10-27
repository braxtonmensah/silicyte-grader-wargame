"""L5 grader (deliberately flawed; see docs/HOLES.md after you solve it).

Usage: python grader.py ANSWER.json [KEY_DIR]. Exit code 0 on PASS.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from wargame.common import load_key, main, verdict  # noqa: E402


def grade(answer_path, key_dir=HERE):
    key = load_key(key_dir)["terms"]
    with open(answer_path, encoding="utf-8") as fh:
        ans = json.load(fh)
    terms = ans.get("terms") if type(ans) is dict else None
    if type(terms) is not list or not terms or any(type(t) is not str for t in terms):
        return verdict(False, ["terms must be a non-empty list of strings"])
    if len(terms) > len(key):
        return verdict(False, ["more terms than expected"])
    text = " ".join(terms)
    missing = [k for k in key if k not in text]
    passed = not missing
    return verdict(passed, ["every expected term found"] if passed else [f"{len(missing)} expected terms not found"])


if __name__ == "__main__":
    main(grade, HERE)
