"""L4 grader (deliberately flawed; see docs/HOLES.md after you solve it).

Usage: python grader.py ANSWER.json [KEY_DIR]. Exit code 0 on PASS.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from wargame.common import load_key, main, verdict  # noqa: E402
from wargame.strictjson import AnswerError, _no_duplicate_keys  # noqa: E402

REL_TOL = 1e-4


def grade(answer_path, key_dir=HERE):
    key = load_key(key_dir)
    try:
        with open(answer_path, encoding="utf-8") as fh:
            ans = json.load(fh, object_pairs_hook=_no_duplicate_keys)
    except AnswerError as exc:
        return verdict(False, [f"rejected: {exc}"])
    if type(ans) is not dict or set(ans) != {"N", "n", "m", "terms"} or type(ans["terms"]) is not list:
        return verdict(False, ["answer needs exactly N, n, m and terms"])
    if any(type(ans[f]) is not int or ans[f] != key[f] for f in ("N", "n", "m")):
        return verdict(False, ["N, n or m is wrong"])
    kt = {t["go_id"]: t for t in key["terms"]}
    at = {}
    for t in ans["terms"]:
        if type(t) is not dict or set(t) != {"go_id", "k", "K", "q"} or type(t["go_id"]) is not str or t["go_id"] in at:
            return verdict(False, ["malformed or duplicate term"])
        at[t["go_id"]] = t
    if set(at) != set(kt):
        return verdict(False, ["term set differs from the key"])
    for g, k in kt.items():
        a = at[g]
        if type(a["k"]) is not int or type(a["K"]) is not int or (a["k"], a["K"]) != (k["k"], k["K"]):
            return verdict(False, [f"wrong counts for {g}"])
        if type(a["q"]) not in (int, float):
            return verdict(False, [f"q for {g} is not a number"])
        if a["q"] < 0 or a["q"] > 1:
            return verdict(False, [f"q for {g} is outside [0, 1]"])
        if abs(a["q"] - k["q"]) > REL_TOL * k["q"]:
            return verdict(False, [f"q for {g} is outside tolerance"])
    return verdict(True, ["table matches"])


if __name__ == "__main__":
    main(grade, HERE)
