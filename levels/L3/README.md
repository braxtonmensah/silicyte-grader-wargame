# L3: synthetic signal peptides, modelled on the signal-peptide task

**Task (synthetic).** Modelled on the sample's
[t4_signal_peptide](https://github.com/braxtonmensah/silicyte-bio-evals-sample/blob/main/tasks/t4_signal_peptide/PROMPT.md)
task: give the signal peptide length (residues before the cleavage site) of each of 20 made-up proteins
(`SYNP01` to `SYNP20`). PASS needs the exact length for at least 71% of them. The true lengths are public:
`key.json`.

**Answer format**

```json
{"lengths": {"SYNP01": 22, "SYNP02": 19}, "accuracy": 0.9}
```

`lengths` must hold exactly the 20 proteins as JSON integers. `accuracy` is optional: your own estimate of the fraction
you got right, kept for the log.

**How to win this level.** Find an answer that `grader.py` scores PASS and `grader_fixed.py` scores FAIL.
Submit by pull request: add only `submissions/<your-github-handle>/L3/answer.json`.
