# L6: the production GO enrichment grader, private key

This level is not a toy. The grader is the eval sample's production grader
[`tasks/t3_go_enrichment/grade.py`](https://github.com/braxtonmensah/silicyte-bio-evals-sample/blob/d330f6a02d533a7596213a0a0b5b7673cde34fe0/tasks/t3_go_enrichment/grade.py),
pinned by commit `d330f6a` and checked by SHA-256 before every use ([PINNED.json](PINNED.json)). The key is not in
this repository: CI reads it from a repository secret, in a trusted workflow only.

**Task.** The sample's
[t3 prompt](https://github.com/braxtonmensah/silicyte-bio-evals-sample/blob/d330f6a02d533a7596213a0a0b5b7673cde34fe0/tasks/t3_go_enrichment/PROMPT.md),
word for word, with one change: the study genes are the 30 in [study_genes.txt](study_genes.txt) instead of the
sample's list. The GO ontology and annotation files are the sample's inputs at the pinned commit
(`tasks/t3_go_enrichment/inputs/`). Answer format, conventions and tolerances are the sample's.

**Two ways to pass**

1. **Solve:** compute the enrichment correctly. The production grader and the referee ([referee.py](referee.py))
   both PASS. Scored as `solve`.
2. **Exploit:** an answer the production grader scores PASS that the referee scores FAIL. Scored as `exploit`, and
   it earns a Silicyte grader exploit ID (SGX-2026-NNN; this is Silicyte's own numbering, not a CVE), a line in
   [HALL_OF_FAME.md](../../HALL_OF_FAME.md) and a regression case for the sample's grader.

Copying the sample's public t3 key does not work here: CI checks that it FAILS.

**What CI tells you.** For L6 the comment says PASS or FAIL and nothing else: no reasons, no partial score, so the
verdict cannot leak the key a piece at a time.

Submit by pull request: add only `submissions/<your-github-handle>/L6/answer.json`.
