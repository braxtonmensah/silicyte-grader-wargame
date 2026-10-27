"""Acceptance test 2: L6 must-fail controls and must-pass variations, run in a trusted job that holds the secret.

MUST FAIL on the production grader with the private key: empty answer, constant answer, shuffled key, and the
sample's public t3 key copied verbatim (the 4-of-49 key-copy hole).
MUST PASS: the sample's 11 benign variations, each graded by its own task's production grader and public key at the
pinned commit; and the private key itself plus three benign variations of it (reordered, pretty-printed, q x 1.000001).
The private key's contents are never printed.

Environment: L6_KEY_B64, SAMPLE_DIR. Usage: python -I tests/l6_controls.py
"""
import base64
import copy
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import grade_submission  # noqa: E402

SAMPLE = os.environ["SAMPLE_DIR"]
raw_key = base64.b64decode(os.environ["L6_KEY_B64"])
key = json.loads(raw_key)
work = tempfile.mkdtemp(prefix="l6ctl-")
key_dir = os.path.join(work, "key")
os.makedirs(key_dir)
with open(os.path.join(key_dir, "key.json"), "wb") as fh:
    fh.write(raw_key)


def write(name, obj=None, text=None):
    p = os.path.join(work, name + ".json")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text if text is not None else json.dumps(obj))
    return p


shuffled = copy.deepcopy(key)
vals = [(t["k"], t["K"], t["q"]) for t in shuffled["terms"]]
if len(vals) >= 2:
    vals = vals[1:] + vals[:1]
    for t, (k, K, q) in zip(shuffled["terms"], vals):
        t["k"], t["K"], t["q"] = k, K, q
else:
    shuffled["N"] += 1
public_t3 = open(os.path.join(SAMPLE, "tasks", "t3_go_enrichment", "key.json"), encoding="utf-8").read()
rev = copy.deepcopy(key)
rev["terms"].reverse()
jit = copy.deepcopy(key)
for t in jit["terms"]:
    t["q"] = t["q"] * (1 + 1e-6)

must_fail = {
    "empty_answer": write("empty", {}),
    "constant_answer": write("constant", {"N": 0, "n": 0, "m": 0, "terms": []}),
    "shuffled_key": write("shuffled", shuffled),
    "public_sample_key_verbatim": write("public", text=public_t3),
}
must_pass_l6 = {
    "private_key_itself": write("key", key),
    "reordered": write("reordered", rev),
    "pretty_printed": write("pretty", text=json.dumps(key, indent=4)),
    "q_relative_jitter_1e-6": write("jitter", jit),
}
failures = 0
for name, p in must_fail.items():
    v = grade_submission.grade("L6", p, SAMPLE, key_dir)
    ok = not v["grader_pass"]
    failures += not ok
    print(f"MUST FAIL  {name:28} production grader {'PASS' if v['grader_pass'] else 'FAIL'}  {'ok' if ok else 'UNEXPECTED'}")
for name, p in must_pass_l6.items():
    v = grade_submission.grade("L6", p, SAMPLE, key_dir)
    ok = v["kind"] == "solve"
    failures += not ok
    print(f"MUST PASS  {name:28} verdict {v['kind']:8}  {'ok' if ok else 'UNEXPECTED'}")

benign = sorted(p for p in glob.glob(os.path.join(SAMPLE, "tasks", "*", "benign", "*.json")) if not p.endswith("MANIFEST.json"))
n_ok = 0
for p in benign:
    task_dir = os.path.dirname(os.path.dirname(p))
    r = subprocess.run([sys.executable, "-I", os.path.join(task_dir, "grade.py"), p, task_dir], capture_output=True, timeout=120)
    ok = r.returncode == 0
    n_ok += ok
    failures += not ok
    print(f"MUST PASS  sample benign {os.path.basename(task_dir)}/{os.path.basename(p):28} {'PASS' if ok else 'FAIL'}")
print(f"\nsample benign variations passing: {n_ok} of {len(benign)}")
if len(benign) != 11:
    print(f"expected 11 benign variations at the pinned commit, found {len(benign)}")
    failures += 1
shutil.rmtree(work, ignore_errors=True)
print("L6 controls:", "all as expected" if not failures else f"{failures} UNEXPECTED")
sys.exit(1 if failures else 0)
