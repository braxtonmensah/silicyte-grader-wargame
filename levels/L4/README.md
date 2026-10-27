# L4: synthetic GO enrichment table, modelled on the GO task

**Task (synthetic).** Modelled on the sample's
[t3_go_enrichment](https://github.com/braxtonmensah/silicyte-bio-evals-sample/blob/main/tasks/t3_go_enrichment/PROMPT.md)
task: report the universe size N, study size n, number of tested terms m, and every significant term with its counts
k and K and its q value. The GO IDs are real; the counts and q values are made up for the game. The correct table is
public: `key.json`. PASS needs N, n, m, the term set, k and K exactly, and each q within 1e-4 relative.

**Answer format**

```json
{"N": 1200, "n": 30, "m": 410, "terms": [{"go_id": "GO:0016126", "k": 12, "K": 40, "q": 3.1e-14}]}
```

**How to win this level.** Find an answer that `grader.py` scores PASS and `grader_fixed.py` scores FAIL.
Submit by pull request: add only `submissions/<your-github-handle>/L4/answer.json`.
