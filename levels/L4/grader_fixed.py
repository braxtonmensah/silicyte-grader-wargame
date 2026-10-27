"""L4 grader with the hole patched: strict loading rejects non-finite number tokens before any comparison.

Usage: python grader_fixed.py ANSWER.json [KEY_DIR]. Exit code 0 on PASS.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from wargame.common import load_key, main, verdict  # noqa: E402
from wargame.enrichment import parse_table, tables_match  # noqa: E402
from wargame.strictjson import AnswerError, load_answer  # noqa: E402


def grade(answer_path, key_dir=HERE):
    key = parse_table(load_key(key_dir))
    try:
        ans = parse_table(load_answer(answer_path))
    except AnswerError as exc:
        return verdict(False, [f"rejected: {exc}"])
    passed = tables_match(ans, key)
    return verdict(passed, ["table matches" if passed else "table differs from the key"])


if __name__ == "__main__":
    main(grade, HERE)
