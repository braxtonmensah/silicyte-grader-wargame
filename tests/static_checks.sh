#!/usr/bin/env bash
# Acceptance test 4 (permissions) and the static half of test 5 (secret placement). Needs mikefarah yq v4.
set -uo pipefail
cd "$(dirname "$0")/.."
W=.github/workflows
fail=0
check() { if eval "$2"; then echo "ok    $1"; else echo "FAIL  $1"; fail=1; fi; }

perm=$(yq -o=json -I=0 '.permissions' $W/check.yml)
check "check.yml top-level permissions are exactly {contents: read} (got $perm)" '[ "$perm" = "{\"contents\":\"read\"}" ]'
jobperm=$(yq '[.jobs[] | has("permissions")] | any' $W/check.yml)
check "check.yml has no job-level permissions (got $jobperm)" '[ "$jobperm" = "false" ]'
trig=$(yq -o=json -I=0 '.on | keys' $W/check.yml)
check "check.yml triggers only on pull_request (got $trig)" '[ "$trig" = "[\"pull_request\"]" ]'
check "check.yml references no secrets" '! grep -nE "secrets\." $W/check.yml'
check "check.yml never mentions the L6 key" '! grep -n "L6_KEY" $W/check.yml'
check "check.yml never grades L6 (no --sample-dir)" '! grep -n "sample-dir" $W/check.yml'

rtrig=$(yq -o=json -I=0 '.on | keys' $W/record.yml)
check "record.yml triggers only on workflow_run (got $rtrig)" '[ "$rtrig" = "[\"workflow_run\"]" ]'
refs=$(yq -o=json -I=0 '[.jobs[].steps[] | select(.uses != null and (.uses | test("^actions/checkout")) and .with.repository == null) | .with.ref]' $W/record.yml)
check "every checkout of this repo in record.yml uses ref main, the base branch (got $refs)" '[ -n "$(echo "$refs" | grep -E "^\[\"main\"(,\"main\")*\]$")" ]'
other=$(yq -o=json -I=0 '[.jobs[].steps[] | select(.uses != null and (.uses | test("^actions/checkout")) and .with.repository != null) | .with.repository + "@" + .with.ref]' $W/record.yml)
pinned=$(python3 -I -c 'import json; print(json.load(open("levels/L6/PINNED.json"))["commit"])')
check "the only other checkout in record.yml is the eval sample at the pinned commit (got $other)" '[ "$other" = "[\"braxtonmensah/silicyte-bio-evals-sample@$pinned\"]" ]'
check "record.yml never checks out the PR head" '! yq ".jobs[].steps[] | select(.uses != null and (.uses | test(\"^actions/checkout\"))) | .with.ref" $W/record.yml | grep -iE "head|pull|workflow_run"'

users=$(grep -l "L6_KEY_B64" $W/*.yml | xargs -n1 basename | sort | tr "\n" " ")
check "L6_KEY_B64 appears only in record.yml and selftest.yml (got: $users)" '[ "$users" = "record.yml selftest.yml " ]'
check "pages.yml references no secrets" '! grep -nE "secrets\." $W/pages.yml'
exit $fail
