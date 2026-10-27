"""Path, size and schema gate for a submission pull request.

Reads the PR only as data, through git plumbing (diff, cat-file). Nothing from the PR is executed or imported.

Usage:
  python -I tools/gate.py --repo PR_CLONE --base BASE_SHA --head HEAD_SHA --author LOGIN --out DIR

Writes DIR/gate.json and, when accepted, DIR/answer.json (the submitted bytes, unchanged).
Exit code 0 when accepted, 1 when rejected.
"""
import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_BYTES = 1_000_000
LEVELS = ("L0", "L1", "L2", "L3", "L4", "L5", "L6")
HANDLE_RE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})")
SHA_RE = re.compile(r"[0-9a-f]{40}")


def git(repo, *args, binary=False):
    out = subprocess.run(["git", "-C", repo, *args], check=True, capture_output=True, timeout=120)
    return out.stdout if binary else out.stdout.decode("utf-8", "replace")


def evaluate(repo, base, head, author):
    """Returns (accepted, reason, level, path, raw_bytes)."""
    if not SHA_RE.fullmatch(base) or not SHA_RE.fullmatch(head):
        return False, "base and head must be full commit SHAs", None, None, None
    if not HANDLE_RE.fullmatch(author):
        return False, "author is not a valid GitHub handle", None, None, None
    diff = git(repo, "diff", "--name-status", "--no-renames", "-z", f"{base}...{head}")
    parts = [p for p in diff.split("\0") if p]
    changes = list(zip(parts[0::2], parts[1::2]))
    if not changes:
        return False, "the pull request changes no files", None, None, None
    outside = [p for _, p in changes if not p.lower().startswith(f"submissions/{author.lower()}/")]
    if outside:
        return False, f"touches paths outside submissions/{author}/: {sorted(outside)[:5]}", None, None, None
    if len(changes) != 1:
        return False, f"must change exactly one file; changes {len(changes)}", None, None, None
    status, path = changes[0]
    if status not in ("A", "M"):
        return False, f"the file must be added or modified (status {status})", None, None, None
    m = re.fullmatch(r"submissions/([^/]+)/([^/]+)/answer\.json", path)
    if not m or m.group(1).lower() != author.lower() or m.group(2) not in LEVELS:
        return False, f"path must be submissions/{author}/<L0..L6>/answer.json, got {path}", None, None, None
    level = m.group(2)
    size = int(git(repo, "cat-file", "-s", f"{head}:{path}").strip())
    if size > MAX_BYTES:
        return False, f"file is {size} bytes; the limit is {MAX_BYTES}", level, path, None
    raw = git(repo, "cat-file", "blob", f"{head}:{path}", binary=True)
    try:
        obj = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        return False, f"invalid JSON: {type(exc).__name__}", level, path, None
    import jsonschema  # pinned in the workflow
    with open(os.path.join(ROOT, "schema", "answer.schema.json"), encoding="utf-8") as fh:
        schema = json.load(fh)
    try:
        jsonschema.validate(obj, schema)
    except jsonschema.ValidationError as exc:
        return False, f"answer does not match schema/answer.schema.json: {exc.message[:200]}", level, path, None
    return True, "accepted", level, path, raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", required=True)
    ap.add_argument("--author", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    try:
        ok, reason, level, path, raw = evaluate(a.repo, a.base, a.head, a.author)
    except subprocess.CalledProcessError as exc:
        ok, reason, level, path, raw = False, f"git error: {exc.stderr.decode('utf-8', 'replace')[:200]}", None, None, None
    if ok:
        with open(os.path.join(a.out, "answer.json"), "wb") as fh:
            fh.write(raw)
    result = {"accepted": ok, "reason": reason, "level": level, "path": path, "author": a.author, "head_sha": a.head}
    with open(os.path.join(a.out, "gate.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
    print(json.dumps(result, sort_keys=True))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
