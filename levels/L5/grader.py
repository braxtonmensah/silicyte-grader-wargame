"""L5 grader (deliberately flawed; see docs/HOLES.md after you solve it).

Strict loading; the answer is exactly {"terms": [...]}.
Usage: python grader.py ANSWER.json [KEY_DIR]. Exit code 0 on PASS.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from wargame.common import load_key, main, verdict  # noqa: E402
from wargame.strictjson import AnswerError, load_answer, require_keys  # noqa: E402


def grade(answer_path, key_dir=HERE):
    key = load_key(key_dir)["terms"]
    try:
        ans = load_answer(answer_path)
        require_keys(ans, ["terms"])
    except AnswerError as exc:
        return verdict(False, [f"rejected: {exc}"])
    terms = ans["terms"]
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
