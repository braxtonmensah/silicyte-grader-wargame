# Grader Wargame: break Silicyte's biology eval graders

[![selftest](https://github.com/braxtonmensah/silicyte-grader-wargame/actions/workflows/selftest.yml/badge.svg)](https://github.com/braxtonmensah/silicyte-grader-wargame/actions/workflows/selftest.yml)

**Silicyte's graders, attackable, with CI-verified results.**

A standing wargame in the style of OverTheWire's Bandit. Each level is a grader for a biology eval task, and your job
is to make it say PASS when it should not. You attack by pull request. CI checks every claim, **never executes your
code**, and writes the result to a public [scoreboard](https://braxtonmensah.github.io/silicyte-grader-wargame/)
generated only from CI verdicts.

The graders come from [silicyte-bio-evals-sample](https://github.com/braxtonmensah/silicyte-bio-evals-sample), a free
set of 4 checkable biology tasks. Its CI logs 49 attempts to cheat its own graders and catches 45. The 4 it misses all
copy the public answer key, so the final level here keeps its key off the repository.

## Play in one line

Add `submissions/<your-github-handle>/<level>/answer.json` in a pull request. That is the whole interface.

## The levels

| Level | Task it is modelled on | You win when |
|---|---|---|
| [L0](levels/L0/README.md) | HER2 epitope (synthetic) | `grader.py` PASSES your answer and `grader_fixed.py` FAILS it |
| [L1](levels/L1/README.md) | HER2 epitope (synthetic) | same |
| [L2](levels/L2/README.md) | PTEN variant abundance (synthetic) | same |
| [L3](levels/L3/README.md) | Signal peptide lengths (synthetic) | same |
| [L4](levels/L4/README.md) | GO enrichment table (synthetic) | same |
| [L5](levels/L5/README.md) | GO term list (synthetic) | same |
| [L6](levels/L6/README.md) | GO enrichment, the sample's **production grader**, pinned by commit, **private key** | the production grader PASSES (a full solve, or an exploit the referee catches) |

L0 to L5 each hide exactly one deliberate hole. Their keys are public, because a correct answer does not win: CI runs
both the level's `grader.py` and its patched `grader_fixed.py`, and a level counts only when `grader.py` says PASS and
`grader_fixed.py` says FAIL. That two-sided test proves an exploit, not a right answer. Each level's README states the goal,
never the hole. Spoilers, with each hole mapped to the BenchJack taxonomy: [docs/HOLES.md](docs/HOLES.md).

L6 has no known hole. An L6 exploit (production grader PASS, independent referee FAIL) earns an
**SGX-2026-NNN** ID (Silicyte grader exploit ID, not a CVE), a line in [HALL_OF_FAME.md](HALL_OF_FAME.md), and a
regression case for the sample's grader.

Try locally before you open a PR (Python 3.10 or later, no dependencies):

```bash
python levels/L2/grader.py my_answer.json; python levels/L2/grader_fixed.py my_answer.json
```

## Rules

1. One pull request adds or changes exactly one file: `submissions/<your-handle>/<level>/answer.json`. Your handle is
   the PR author's GitHub login. Anything else in the PR, including a change to a workflow or a grader, gets the PR
   rejected before grading.
2. The file is at most 1 MB and is one JSON object ([schema/answer.schema.json](schema/answer.schema.json)).
3. A level counts once per handle. Failed attempts are logged too ([attempts.json](attempts.json)).
4. The maintainer, not CI, merges or closes PRs; the scoreboard records the CI verdict either way.
5. Holes in the wargame's own CI are welcome, privately: see [SECURITY.md](SECURITY.md).

## The safety model: CI never executes submitted code

| Stage | Workflow | Trigger | Token | Secrets | Runs code from |
|---|---|---|---|---|---|
| check | [check.yml](.github/workflows/check.yml) | `pull_request` | `contents: read` | none | the base commit; the PR is read with `git diff` and `git cat-file` as data |
| record | [record.yml](.github/workflows/record.yml) | `workflow_run` of check | write, to comment and record | `L6_KEY_B64` | `main` only, never the PR head |
| pages | [pages.yml](.github/workflows/pages.yml) | push to main, dispatch | Pages deploy | none | `main` |

- `check.yml` gates the PR (paths, size, JSON, schema), grades L0 to L5 with the base commit's graders, and uploads a
  verdict artifact. It never sees the L6 key.
- `record.yml` treats that artifact as untrusted. It uses only the PR number from it, verifies that the PR's head SHA
  equals the checked SHA, then re-derives the paths, size, schema and grade itself, from git objects, with trusted
  code. It grades L6 with the private key and posts only PASS or FAIL for L6, so a comment cannot leak the key.
- The L6 grader is fetched from the sample repository at commit `d330f6a` and verified by SHA-256 before each use
  ([levels/L6/PINNED.json](levels/L6/PINNED.json)).

## How this was tested

[selftest.yml](.github/workflows/selftest.yml) runs on every push to main:

1. For L0 to L5, the reference exploit in `tests/` PASSES `grader.py` and FAILS `grader_fixed.py`, and the correct
   answer PASSES both. These are Silicyte's own exploits and are not on the scoreboard.
2. L6, in a trusted job with the key: an empty answer, a constant answer, a shuffled key and the sample's public key
   copied verbatim all FAIL; the sample's 11 benign variations of correct answers PASS.
3. The gate rejects fixture branches that edit a workflow or a grader, carry a 2 MB file, or hold invalid JSON.
4. A `yq` check that `check.yml` declares only `contents: read` and references no secrets, and that `record.yml`
   checks out only `main`.
5. A scan of `check.yml` logs and artifacts for L6 key material (the key's SHA-256 prefix and more) finds none.
6. `scoreboard.json` validates against [schema/scoreboard.schema.json](schema/scoreboard.schema.json), and the Pages
   build renders an empty scoreboard without error.

The end-to-end path was also run on real pull requests from same-repository test branches: a reference L0 exploit,
and PRs that touched a workflow, carried 2 MB, or held invalid JSON. Rows from the owner's test PRs are marked
`maintainer_test` and shown apart from players on the scoreboard.

## Limits

- GitHub asks the maintainer to approve workflow runs on a first-time contributor's PR, so a first verdict can wait
  for that approval.
- L0 to L5 are synthetic; only L6 uses real biology data (GO release 2026-08-05, from the sample).
- L6 can be solved honestly: the conventions are written out, and the sample's own builder implements them. A solve
  is scored `solve`; only an answer the referee rejects is scored `exploit`. The referee shares the sample's strict
  loader, so it is a second check, not a fully independent one.
- A one-bit PASS or FAIL per attempt is still an oracle. Each attempt costs a public PR, and attempts are logged.
- CI can draft an SGX entry and a regression case; the maintainer confirms each exploit and opens the security
  advisory.

## Prior art

[OverTheWire](https://overthewire.org/wargames/) (Bandit) for the level format; Lakera's
[Gandalf](https://gandalf.lakera.ai/) for a public, levelled attack game against an AI defence;
[BenchJack](https://arxiv.org/abs/2605.12673) (UC Berkeley, 2026) for the V1 to V8 taxonomy of benchmark flaws;
[EvilGenie](https://arxiv.org/abs/2511.21654) (2025) for measuring reward hacking by coding agents; and Berkeley RDI's
[audit of agent benchmarks](https://rdi.berkeley.edu/blog/trustworthy-benchmarks-cont/) (2026). This repository adds
attacks on graders for biology eval tasks, verified in CI by a two-sided test.

## License

MIT ([LICENSE](LICENSE)). `wargame/strictjson.py` and `wargame/stats.py` are copied from the eval sample (MIT).

Built by Silicyte ([silicyte.com](https://silicyte.com)) with AI assistance.
