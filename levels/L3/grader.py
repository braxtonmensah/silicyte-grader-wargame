"""L3 grader (deliberately flawed; see docs/HOLES.md after you solve it).

Usage: python grader.py ANSWER.json [KEY_DIR]. Exit code 0 on PASS.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from wargame.common import load_key, main, verdict  # noqa: E402
from wargame.sigpep import BAR, load, measured_accuracy  # noqa: E402
from wargame.strictjson import AnswerError  # noqa: E402


def grade(answer_path, key_dir=HERE):
    key = load_key(key_dir)["lengths"]
    try:
        lengths, reported = load(answer_path, key)
    except AnswerError as exc:
        return verdict(False, [f"rejected: {exc}"])
    acc = reported if reported is not None else measured_accuracy(lengths, key)
    passed = acc >= BAR
    return verdict(passed, [f"accuracy {acc:.3f}"], accuracy=round(acc, 6), bar=BAR)


if __name__ == "__main__":
    main(grade, HERE)
