"""Record a CI verdict for one submission pull request. Runs only in .github/workflows/record.yml.

Trust model: this file comes from the base branch. The only thing taken from the untrusted check.yml artifact is the
pull request number, and even that is verified: the PR's current head SHA must equal the head SHA of the check run
that triggered this workflow. Everything else (changed paths, sizes, schema, grades) is recomputed here from git
objects read as data, with trusted graders.

Environment: GH_TOKEN, GITHUB_REPOSITORY, GITHUB_SERVER_URL, GITHUB_RUN_ID, WF_HEAD_SHA, WF_RUN_URL,
             SAMPLE_DIR (pinned sample clone), L6_KEY_B64 (secret; used only for L6).
Usage: python -I tools/record.py UNTRUSTED_VERDICT_DIR
"""
import base64
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import gate  # noqa: E402
import grade_submission  # noqa: E402

REPO = os.environ["GITHUB_REPOSITORY"]
SERVER = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
RUN_URL = f"{SERVER}/{REPO}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
OWNER = REPO.split("/")[0]


def sh(*cmd, check=True, input_text=None):
    p = subprocess.run(list(cmd), capture_output=True, text=True, cwd=ROOT, input=input_text, timeout=300)
    if check and p.returncode != 0:
        raise RuntimeError(f"{cmd[0]} {cmd[1] if len(cmd) > 1 else ''} failed: {p.stderr[:300]}")
    return p.stdout


def gh_json(path):
    return json.loads(sh("gh", "api", path))


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load(path, default):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return default


def dump(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(obj, indent=1, sort_keys=True) + "\n")


def next_sgx_id():
    text = open(os.path.join(ROOT, "HALL_OF_FAME.md"), encoding="utf-8").read()
    used = [int(x) for x in re.findall(r"SGX-2026-(\d{3})", text)]
    return f"SGX-2026-{(max(used) + 1 if used else 1):03d}"


def grade_l6(answer_path):
    key_b64 = os.environ.get("L6_KEY_B64", "")
    if not key_b64:
        raise RuntimeError("L6_KEY_B64 is not available to this run")
    key_dir = tempfile.mkdtemp(prefix="l6key-")
    try:
        with open(os.path.join(key_dir, "key.json"), "wb") as fh:
            fh.write(base64.b64decode(key_b64))
        return grade_submission.grade("L6", answer_path, os.environ["SAMPLE_DIR"], key_dir)
    finally:
        shutil.rmtree(key_dir, ignore_errors=True)


def main():
    vdir = sys.argv[1]
    untrusted = load(os.path.join(vdir, "verdict.json"), {})
    pr_number = untrusted.get("pr")
    if type(pr_number) is not int or pr_number < 1:
        print("no valid PR number in the check artifact; nothing to record")
        return
    pr = gh_json(f"repos/{REPO}/pulls/{pr_number}")
    head_sha = pr["head"]["sha"]
    if head_sha != os.environ["WF_HEAD_SHA"]:
        print("PR head moved since the check ran (or the artifact lies); a newer check run will record it")
        return
    if pr["base"]["repo"]["full_name"] != REPO:
        print("PR is not against this repository")
        return
    author = pr["user"]["login"]
    base_sha = pr["base"]["sha"]
    sh("git", "fetch", "--no-tags", "origin", f"+refs/pull/{pr_number}/head:refs/remotes/pr/{pr_number}")
    sh("git", "fetch", "--no-tags", "origin", base_sha, check=False)

    ok, reason, level, path, raw = gate.evaluate(ROOT, base_sha, head_sha, author)
    attempt = {"handle": author, "pr": pr_number, "head_sha": head_sha, "run_url": RUN_URL,
               "check_run_url": os.environ["WF_RUN_URL"], "utc": now_utc(), "level": level,
               "maintainer_test": author.lower() == OWNER.lower()}
    sgx = None
    if not ok:
        attempt.update(outcome="rejected", reason=reason)
        body = f"**REJECTED** before grading: {reason}\n\nRules: one file, `submissions/{author}/<level>/answer.json`, at most 1 MB, one JSON object."
    else:
        tmp = tempfile.mkdtemp(prefix="answer-")
        answer_path = os.path.join(tmp, "answer.json")
        with open(answer_path, "wb") as fh:
            fh.write(raw)
        v = grade_l6(answer_path) if level == "L6" else grade_submission.grade(level, answer_path)
        shutil.rmtree(tmp, ignore_errors=True)
        attempt.update(outcome=v["kind"])
        if level == "L6":
            if v["kind"] == "solve":
                body = "**PASS L6** (solve): the production grader and the referee both PASS."
            elif v["kind"] == "exploit":
                sgx = next_sgx_id()
                body = (f"**PASS L6** (exploit): the production grader PASSES an answer the referee FAILS. "
                        f"Assigned **{sgx}** (Silicyte grader exploit ID, not a CVE). The maintainer will confirm it, "
                        f"open a draft security advisory and add a regression case to the sample's grader.")
            else:
                body = "**FAIL L6**. (For L6 the verdict carries no reasons, so it cannot leak the private key.)"
        else:
            if v["kind"] == "exploit":
                body = (f"**PASS {level}** (exploit verified): `grader.py` PASS, `grader_fixed.py` FAIL.")
            elif v["kind"] == "correct":
                body = (f"**FAIL {level}**: this is a correct answer (both graders PASS). The level asks for an answer "
                        f"`grader.py` PASSES and `grader_fixed.py` FAILS.")
            else:
                body = f"**FAIL {level}**: `grader.py` {'PASS' if v['grader_pass'] else 'FAIL'}, `grader_fixed.py` {'PASS' if v['fixed_pass'] else 'FAIL'}."
                if v.get("grader_reasons"):
                    body += f"\n\n`grader.py` said: {'; '.join(v['grader_reasons'])[:300]}"
        if v["level_passed"]:
            board = load(os.path.join(ROOT, "scoreboard.json"), {"entries": []})
            kind = "exploit" if v["kind"] == "exploit" else "solve"
            dup = any(e["handle"].lower() == author.lower() and e["level"] == level and e["kind"] == kind
                      for e in board["entries"])
            if not dup:
                row = {"handle": author, "level": level, "kind": kind, "pr": pr_number, "run_url": RUN_URL,
                       "check_run_url": os.environ["WF_RUN_URL"], "utc": attempt["utc"], "head_sha": head_sha,
                       "maintainer_test": attempt["maintainer_test"]}
                if sgx:
                    row["sgx_id"] = sgx
                board["entries"].append(row)
                dump(os.path.join(ROOT, "scoreboard.json"), board)
                body += "\n\nRecorded in [scoreboard.json](../blob/main/scoreboard.json)."
            else:
                body += "\n\nAlready on the scoreboard for this level; not added twice."
    if sgx:
        with open(os.path.join(ROOT, "HALL_OF_FAME.md"), "a", encoding="utf-8", newline="\n") as fh:
            fh.write(f"- {sgx} (Silicyte grader exploit ID, not a CVE): @{author}, L6, PR #{pr_number}, {RUN_URL}\n")
        os.makedirs(os.path.join(ROOT, "regressions"), exist_ok=True)
        with open(os.path.join(ROOT, "regressions", f"{sgx}.json"), "wb") as fh:
            fh.write(raw)
        advisory = {"summary": f"{sgx}: L6 production grader accepts an answer the referee rejects",
                    "description": f"Found by @{author} in PR #{pr_number}. CI run: {RUN_URL}. Regression case: regressions/{sgx}.json",
                    "severity": "low",
                    "vulnerabilities": [{"package": {"ecosystem": "other", "name": "silicyte-bio-evals-sample"}}]}
        # Best effort: the workflow token may lack permission to draft advisories; the comment says the maintainer does it.
        adv = subprocess.run(["gh", "api", "-X", "POST", f"repos/{REPO}/security-advisories", "--input", "-"],
                             input=json.dumps(advisory), capture_output=True, text=True, cwd=ROOT)
        attempt["advisory_draft_created"] = adv.returncode == 0
        attempt["sgx_id"] = sgx
    attempts = load(os.path.join(ROOT, "attempts.json"), {"attempts": []})
    attempts["attempts"].append(attempt)
    dump(os.path.join(ROOT, "attempts.json"), attempts)

    body += f"\n\nVerified by [this run]({RUN_URL}). CI never executes submitted code. The maintainer, not CI, merges or closes this PR; the scoreboard records the CI verdict either way."
    sh("gh", "pr", "comment", str(pr_number), "--repo", REPO, "--body-file", "-", input_text=body)

    sh("git", "add", "scoreboard.json", "attempts.json", "HALL_OF_FAME.md")
    if os.path.isdir(os.path.join(ROOT, "regressions")):
        sh("git", "add", "regressions")
    if sh("git", "diff", "--cached", "--name-only").strip():
        sh("git", "config", "user.name", "github-actions[bot]")
        sh("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
        sh("git", "commit", "-m", f"record: PR #{pr_number} {level or ''} {attempt['outcome']}")
        for _ in range(3):
            if subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=ROOT).returncode == 0:
                break
            sh("git", "pull", "--rebase", "origin", "main")
        else:
            raise RuntimeError("could not push the record commit")
        subprocess.run(["gh", "workflow", "run", "pages.yml", "--repo", REPO, "--ref", "main"], cwd=ROOT)
    print(json.dumps({"pr": pr_number, "level": level, "outcome": attempt["outcome"], "sgx": sgx}))


if __name__ == "__main__":
    main()
