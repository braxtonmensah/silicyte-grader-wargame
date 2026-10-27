# L1: synthetic epitope, modelled on the HER2 task

**Task (synthetic).** Same setting as L0, modelled on the sample's
[t1_her2_epitope](https://github.com/braxtonmensah/silicyte-bio-evals-sample/blob/main/tasks/t1_her2_epitope/PROMPT.md)
task: report every antigen residue (chain C) within 4.0 A of the antibody, with residue name and minimum distance
(tolerance 0.01 A). The correct answer is public: `key.json`.

**Answer format**

```json
{"epitope": [{"chain": "C", "resnum": 558, "resname": "GLU", "min_distance": 3.33}]}
```

No other keys. Integers must be JSON integers.

**How to win this level.** Find an answer that `grader.py` scores PASS and `grader_fixed.py` scores FAIL.
Submit by pull request: add only `submissions/<your-github-handle>/L1/answer.json`.
