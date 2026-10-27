"""Acceptance test 1: for every level L0 to L5, the reference exploit PASSES grader.py and FAILS grader_fixed.py,
and the correct answer PASSES both. Also checks the scoring verdict CI derives from those outcomes.

Usage: python -I tests/run_levels.py   (exit code 0 when all 24 outcomes and 12 verdicts are as expected)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import grade_submission  # noqa: E402

failures = 0
print(f"{'level':6} {'answer':8} {'grader.py':10} {'fixed':10} {'verdict':8}")
for i in range(6):
    level = f"L{i}"
    d = os.path.join(ROOT, "levels", level)
    for name, want_g, want_f, want_kind in (("exploit", True, False, "exploit"), ("correct", True, True, "correct")):
        ans = os.path.join(ROOT, "tests", level, f"{name}.json")
        g, _ = grade_submission.run_grader(os.path.join(d, "grader.py"), ans)
        f, _ = grade_submission.run_grader(os.path.join(d, "grader_fixed.py"), ans)
        kind = grade_submission.grade(level, ans)["kind"]
        ok = (g, f, kind) == (want_g, want_f, want_kind)
        failures += not ok
        print(f"{level:6} {name:8} {'PASS' if g else 'FAIL':10} {'PASS' if f else 'FAIL':10} {kind:8} {'ok' if ok else 'UNEXPECTED'}")
print(f"\n{12 - failures} of 12 rows as expected (6 levels x exploit and correct; each row checks grader.py, grader_fixed.py and the verdict)")
sys.exit(1 if failures else 0)
