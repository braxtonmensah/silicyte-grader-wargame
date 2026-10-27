"""L5 grader with the hole patched: strict loading, every entry a well-formed GO ID, exact set equality.

Usage: python grader_fixed.py ANSWER.json [KEY_DIR]. Exit code 0 on PASS.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from wargame.common import load_key, main, verdict  # noqa: E402
from wargame.enrichment import GO_RE  # noqa: E402
from wargame.strictjson import AnswerError, load_answer, require_keys  # noqa: E402


def grade(answer_path, key_dir=HERE):
    key = set(load_key(key_dir)["terms"])
    try:
        ans = load_answer(answer_path)
        require_keys(ans, ["terms"])
        terms = ans["terms"]
        if type(terms) is not list or any(type(t) is not str or not GO_RE.fullmatch(t) for t in terms):
            raise AnswerError("terms must be a list of GO IDs like GO:0000000")
        if len(set(terms)) != len(terms):
            raise AnswerError("duplicate term")
    except AnswerError as exc:
        return verdict(False, [f"rejected: {exc}"])
    passed = set(terms) == key
    return verdict(passed, ["exact match" if passed else "term set differs from the key"])


if __name__ == "__main__":
    main(grade, HERE)
