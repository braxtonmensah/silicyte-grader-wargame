# Spoilers: the hole in each level

Read this after you play. Each of L0 to L5 has exactly one deliberate hole, and its `grader_fixed.py` patches that
hole and nothing else. The class names are from the eight-class taxonomy (V1 to V8) in BenchJack: Hao Wang, Hanchen
Li, Qiuyang Mang, Alvin Cheung, Koushik Sen and Dawn Song, "Do Androids Dream of Breaking the Game? Systematically
Auditing AI Agent Benchmarks with BenchJack", arXiv:2605.12673 (2026). Where no class fits exactly, the closest one is
named and the gap is said.

| Level | Modelled on (sample task) | Hole | BenchJack class | Reference exploit |
|---|---|---|---|---|
| L0 | t1 HER2 epitope | Checks the answer's format only, never its content | V6, evaluation logic gaps | [tests/L0/exploit.json](../tests/L0/exploit.json) |
| L1 | t1 HER2 epitope | Every reported residue must be right, but nothing checks that all of them are reported (no set-size or coverage check) | V6, evaluation logic gaps | [tests/L1/exploit.json](../tests/L1/exploit.json) |
| L2 | t2 PTEN abundance | A "noise tolerance" of 0.5 lowers the Spearman bar from 0.66 to 0.16 | V6, evaluation logic gaps | [tests/L2/exploit.json](../tests/L2/exploit.json) (Spearman 0.451) |
| L3 | t4 signal peptide | Uses the answer's own `accuracy` field when present instead of measuring it | V7, trusting untrusted output | [tests/L3/exploit.json](../tests/L3/exploit.json) |
| L4 | t3 GO enrichment | Plain `json.load` accepts `NaN`, and every comparison with NaN is false, so a NaN q passes the range and tolerance checks | Closest: V6, evaluation logic gaps (an input-validation gap; the taxonomy has no class for non-finite numbers) | [tests/L4/exploit.json](../tests/L4/exploit.json) |
| L5 | t3 GO enrichment | Checks that each expected GO ID occurs somewhere in the joined answer text (substring match) | V5, weak string matching | [tests/L5/exploit.json](../tests/L5/exploit.json) |
| L6 | t3 GO enrichment, production grader | None known. The key is kept off the repository, which closes the key-copy hole (V2, answers shipped with the test) that let 4 of the sample's 49 logged attempts through | V2 closed by design | none |

The sample's production graders already defend against L0 to L5's holes: strict loading (no NaN, no duplicate keys,
no booleans as numbers), exact sets, computed scores only, and regular-expression-checked identifiers. The levels put
each defence back one at a time, so a player can see what each one is for.
