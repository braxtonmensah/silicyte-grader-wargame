"""Build the private L6 key with the eval sample's own t3 builder, on a different study gene list.

Runs only in .github/workflows/l6-key.yml (workflow_dispatch, maintainer only). It prints nothing about the key except
a SHA-256 prefix and refuses to write a key with no significant terms. The caller encrypts the output to the
maintainer's public key (levels/L6/build_pubkey.pem) before upload, so the key never appears in clear in a log or
artifact.

Usage: python -I tools/build_l6_key.py SAMPLE_DIR OUT_DIR
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    sample, out_dir = sys.argv[1], sys.argv[2]
    sys.path.insert(0, sample)
    sys.path.insert(0, os.path.join(sample, "tasks", "t3_go_enrichment"))
    import build  # the sample's tasks/t3_go_enrichment/build.py at the pinned commit
    terms = build.parse_obo()
    rows = build.read_gaf()
    study = build.read_study(os.path.join(ROOT, "levels", "L6", "study_genes.txt"))
    key, det = build.enrich(terms, rows, study)
    if not key["terms"]:
        sys.exit("refusing: the study list gives no significant terms")
    public_t3 = json.load(open(os.path.join(sample, "tasks", "t3_go_enrichment", "key.json"), encoding="utf-8"))
    if key == public_t3:
        sys.exit("refusing: identical to the public t3 key")
    os.makedirs(out_dir, exist_ok=True)
    text = json.dumps(key, indent=1, sort_keys=True, ensure_ascii=True) + "\n"
    with open(os.path.join(out_dir, "key.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print("L6 key sha256 prefix:", hashlib.sha256(text.encode()).hexdigest()[:12])


if __name__ == "__main__":
    main()
