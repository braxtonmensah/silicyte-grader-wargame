#!/usr/bin/env bash
# Acceptance test 5 (dynamic half): no L6 key bytes in any check.yml run's logs or artifacts.
# Downloads the logs and artifacts of the most recent completed check.yml runs (up to 20) and greps them for
# the key's SHA-256 prefix, the first 40 characters of the secret, and every q value string of 10 or more characters in the key.
# Needs: GH_TOKEN (actions: read), GITHUB_REPOSITORY, L6_KEY_B64.
set -euo pipefail
T="$(mktemp -d)"
printf '%s' "$L6_KEY_B64" | base64 -d > "$T/key.json"
SHA_PREFIX=$(sha256sum "$T/key.json" | cut -c1-16)
python3 -I - "$T/key.json" > "$T/needles.txt" <<'PY'
import json, sys
text = open(sys.argv[1], encoding="utf-8").read()
key = json.loads(text)
needles = {repr(t["q"]) for t in key["terms"] if len(repr(t["q"])) >= 10}

for n in sorted(needles):
    print(n)
PY
echo "$SHA_PREFIX" >> "$T/needles.txt"
printf '%s\n' "${L6_KEY_B64:0:40}" >> "$T/needles.txt"
sed -i '/^$/d' "$T/needles.txt"  # an empty pattern would match everything
echo "needles: $(wc -l < "$T/needles.txt") (SHA-256 prefix, secret base64 prefix, long q strings; not printed)"
runs=$(gh api "repos/$GITHUB_REPOSITORY/actions/workflows/check.yml/runs?status=completed&per_page=20" --jq '.workflow_runs[].id')
n=0
mkdir -p "$T/scan"
for id in $runs; do
  n=$((n + 1))
  mkdir -p "$T/scan/$id"
  gh api "repos/$GITHUB_REPOSITORY/actions/runs/$id/logs" > "$T/scan/$id/logs.zip" 2>/dev/null && (cd "$T/scan/$id" && unzip -qo logs.zip -d logs && rm -f logs.zip) || true
  gh run download "$id" --repo "$GITHUB_REPOSITORY" --dir "$T/scan/$id/artifacts" >/dev/null 2>&1 || true
done
files=$(find "$T/scan" -type f | wc -l)
echo "scanned $n check.yml runs, $files files"
if [ "$n" -eq 0 ]; then echo "FAIL: no completed check.yml runs to scan yet"; exit 1; fi
if grep -rFq -f "$T/needles.txt" "$T/scan"; then
  echo "FAIL: L6 key material found in check.yml logs or artifacts"; exit 1
fi
echo "ok: no L6 key material in any scanned check.yml log or artifact"
