"""L0 grader with the hole patched: strict loading and the exact residue set.

Usage: python grader_fixed.py ANSWER.json [KEY_DIR]. Exit code 0 on PASS.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from wargame.common import load_key, main, verdict  # noqa: E402
from wargame.epitope import load_strict, parse, residue_errors  # noqa: E402
from wargame.strictjson import AnswerError  # noqa: E402


def grade(answer_path, key_dir=HERE):
    key = parse(load_key(key_dir))
    try:
        ans = load_strict(answer_path)
    except AnswerError as exc:
        return verdict(False, [f"rejected: {exc}"])
    bad = residue_errors(ans, key)
    passed = set(ans) == set(key) and bad == 0
    return verdict(passed, ["exact match"] if passed else ["residue set or fields differ from the key"],
                   n_answer=len(ans), n_key=len(key), wrong_fields=bad)


if __name__ == "__main__":
    main(grade, HERE)
