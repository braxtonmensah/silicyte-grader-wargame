# L5: synthetic GO term list, modelled on the GO task

**Task (synthetic).** Modelled on the sample's
[t3_go_enrichment](https://github.com/braxtonmensah/silicyte-bio-evals-sample/blob/main/tasks/t3_go_enrichment/PROMPT.md)
task, reduced to its term list: name exactly the GO biological process terms that are significant for a made-up
study. The correct list is public: `key.json`. Order does not matter.

**Answer format**

```json
{"terms": ["GO:0006695", "GO:0016126"]}
```

**How to win this level.** Find an answer that `grader.py` scores PASS and `grader_fixed.py` scores FAIL.
Submit by pull request: add only `submissions/<your-github-handle>/L5/answer.json`.
