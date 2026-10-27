# L2: synthetic variant abundance, modelled on the PTEN task

**Task (synthetic).** Modelled on the sample's
[t2_pten_abundance](https://github.com/braxtonmensah/silicyte-bio-evals-sample/blob/main/tasks/t2_pten_abundance/PROMPT.md)
task: predict an abundance score for each of 40 made-up variants (`syn01` to `syn40`). PASS needs a Spearman
correlation with the measured scores of at least 0.66. The measured scores are public: `key.json`.

**Answer format**

```json
{"predictions": {"syn01": 0.12, "syn02": 0.80}}
```

Exactly the 40 variants, every value a finite number. No other keys.

**How to win this level.** Find an answer that `grader.py` scores PASS and `grader_fixed.py` scores FAIL.
Submit by pull request: add only `submissions/<your-github-handle>/L2/answer.json`.
