"""L1 grader (deliberately flawed; see docs/HOLES.md after you solve it).

Strict loading; every reported residue must be an epitope residue with the right name and distance.
Usage: python grader.py ANSWER.json [KEY_DIR]. Exit code 0 on PASS.
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
    if not ans:
        return verdict(False, ["empty answer"])
    wrong = set(ans) - set(key)
    bad = residue_errors(ans, key)
    passed = not wrong and bad == 0
    return verdict(passed, ["every reported residue is correct"] if passed else ["some reported residues are wrong"],
                   n_answer=len(ans))


if __name__ == "__main__":
    main(grade, HERE)
# fixture edit
