#!/usr/bin/env bash
# Acceptance test 3 (offline half): the gate rejects fixture branches that touch workflows or graders, carry a 2 MB
# file, invalid JSON, a non-object answer, another player's folder, an unknown level or two files, and accepts a
# clean one. The online half opens real pull requests against this repository (README, "How this was tested").
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d)"
cd "$T"
git init -q -b main
git config user.email ci@example.invalid
git config user.name ci
mkdir -p .github/workflows levels/L0
echo "name: check" > .github/workflows/check.yml
echo "# grader" > levels/L0/grader.py
git add -A && git commit -qm base
BASE=$(git rev-parse HEAD)
GOOD='{"epitope": [{"chain": "C", "resnum": 1, "resname": "ALA", "min_distance": 9.9}]}'

put() { mkdir -p "$(dirname "$1")"; printf '%s\n' "$2" > "$1"; }
start() { git checkout -q -b "$1" "$BASE"; }
finish() { git add -A && git commit -qm "$1" && git rev-parse HEAD; }

declare -A HEADS EXPECT
start good;         put submissions/alice/L0/answer.json "$GOOD"; HEADS[good]=$(finish good); EXPECT[good]=0
start workflow;     put submissions/alice/L0/answer.json "$GOOD"; echo "# x" >> .github/workflows/check.yml; HEADS[workflow]=$(finish workflow); EXPECT[workflow]=1
start grader;       put submissions/alice/L0/answer.json "$GOOD"; echo "PASS = True" >> levels/L0/grader.py; HEADS[grader]=$(finish grader); EXPECT[grader]=1
start big;          mkdir -p submissions/alice/L0; { printf '{"pad": "'; head -c 2097152 /dev/zero | tr '\0' 'a'; printf '"}\n'; } > submissions/alice/L0/answer.json; HEADS[big]=$(finish big); EXPECT[big]=1
start invalid;      put submissions/alice/L0/answer.json '{"epitope": ['; HEADS[invalid]=$(finish invalid); EXPECT[invalid]=1
start array;        put submissions/alice/L0/answer.json '[1, 2, 3]'; HEADS[array]=$(finish array); EXPECT[array]=1
start other_author; put submissions/bob/L0/answer.json "$GOOD"; HEADS[other_author]=$(finish other_author); EXPECT[other_author]=1
start bad_level;    put submissions/alice/L9/answer.json "$GOOD"; HEADS[bad_level]=$(finish bad_level); EXPECT[bad_level]=1
start two_files;    put submissions/alice/L0/answer.json "$GOOD"; put submissions/alice/L1/answer.json "$GOOD"; HEADS[two_files]=$(finish two_files); EXPECT[two_files]=1

fail=0
for name in good workflow grader big invalid array other_author bad_level two_files; do
  set +e
  out=$(python -I "$ROOT/tools/gate.py" --repo "$T" --base "$BASE" --head "${HEADS[$name]}" --author alice --out "$T/out_$name")
  code=$?
  set -e
  want=${EXPECT[$name]}
  if [ "$code" = "$want" ]; then res=ok; else res=UNEXPECTED; fail=1; fi
  reason=$(printf '%s' "$out" | python -I -c 'import json,sys; print(json.load(sys.stdin)["reason"][:90])')
  printf '%-13s exit %s (want %s) %-10s %s\n' "$name" "$code" "$want" "$res" "$reason"
done
size=$(git -C "$T" cat-file -s "${HEADS[big]}:submissions/alice/L0/answer.json")
echo "big fixture size: $size bytes"
[ "$size" -gt 2000000 ] || { echo "big fixture is not over 2 MB"; fail=1; }
exit $fail
