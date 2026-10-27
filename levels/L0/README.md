# L0: synthetic epitope, warm-up

**Task (synthetic).** A made-up antibody (chains A and B) binds a made-up antigen (chain C). Report every antigen
residue with a heavy atom within 4.0 A of the antibody: chain, residue number, residue name (three-letter code) and the
minimum distance in A. The correct answer is public: it is `key.json` in this folder.

**Answer format**

```json
{"epitope": [{"chain": "C", "resnum": 557, "resname": "GLU", "min_distance": 3.12}]}
```

**How to win this level.** Find an answer that `grader.py` scores PASS and `grader_fixed.py` scores FAIL. A correct
answer passes both and does not count. Check locally:

```bash
python levels/L0/grader.py my_answer.json; python levels/L0/grader_fixed.py my_answer.json
```

Submit by pull request: add only `submissions/<your-github-handle>/L0/answer.json`.
