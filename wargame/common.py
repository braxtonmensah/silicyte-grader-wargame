"""Small helpers shared by the level graders."""
import json
import os
import sys


def load_key(key_dir):
    with open(os.path.join(key_dir, "key.json"), encoding="utf-8") as fh:
        return json.load(fh)


def verdict(passed, reasons, **metrics):
    return {"pass": bool(passed), "reasons": list(reasons), "metrics": metrics}


def main(grade, here):
    if len(sys.argv) < 2:
        print("usage: python grader.py ANSWER.json [KEY_DIR]", file=sys.stderr)
        sys.exit(2)
    try:
        result = grade(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else here)
    except Exception as exc:  # a grader crash is a FAIL, never a PASS
        result = verdict(False, [f"grader error: {type(exc).__name__}"])
    print(json.dumps(result, indent=1, sort_keys=True))
    sys.exit(0 if result["pass"] else 1)
