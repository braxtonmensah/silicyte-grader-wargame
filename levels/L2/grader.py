"""L2 grader (deliberately flawed; see docs/HOLES.md after you solve it).

Usage: python grader.py ANSWER.json [KEY_DIR]. Exit code 0 on PASS.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from wargame.abundance import BAR, rho  # noqa: E402
from wargame.common import load_key, main, verdict  # noqa: E402
from wargame.strictjson import AnswerError  # noqa: E402

TOLERANCE = 0.5  # allowance for measurement noise in the scores


def grade(answer_path, key_dir=HERE):
    truth = load_key(key_dir)["predictions"]
    try:
        r = rho(answer_path, truth)
    except AnswerError as exc:
        return verdict(False, [f"rejected: {exc}"])
    if r is None:
        return verdict(False, ["Spearman undefined (zero variance)"])
    passed = r >= BAR - TOLERANCE
    return verdict(passed, [f"Spearman {r:.4f}"], spearman=round(r, 6), bar=BAR)


if __name__ == "__main__":
    main(grade, HERE)
