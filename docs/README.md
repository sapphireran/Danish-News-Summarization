# Documentation

Personal notes for the ITU 2023 Danish news summarization project. Nothing here is employer documentation.

Read in this order if you are coming back to the repo cold:

1. [../README.md](../README.md) — what the project is and how the scripts are meant to run.
2. [pipeline.md](pipeline.md) — what each file reads, writes, and assumes.
3. [silver-labeling.md](silver-labeling.md) — why the pivot through English is the method, and where it fails.
4. [evaluation-notes.md](evaluation-notes.md) — intended metrics, scripts, and why I do not quote a leaderboard number.
5. [hyperparameters.md](hyperparameters.md) — values copied out of `finetune.py`, `summary.py`, and friends.
6. [reproduction.md](reproduction.md) — environment, artifacts, and a conservative rerun checklist.
7. [known-issues.md](known-issues.md) — mismatches I can see in the committed Python without rerunning training.

Personal / retrospective writing lives under [`../notes/`](../notes/README.md), not here. `docs/` is the “what does the code do” layer. `notes/` is the “what did I think, and what would I change” layer.

## Conventions used in these pages

- **Silver label:** a Danish summary produced by the translation pipeline, not written by a journalist.
- **Gold / human label:** a Nordjylland (TV2 Nord) summary used only at evaluation time.
- **Pivot language:** English. All abstractive compression happens there.
- **Hop:** one model call that can add error (DA→EN, EN summarize, EN→DA).
- Paths are relative to the repository root unless stated otherwise.
- I describe the scripts **as committed on `main` (SHA `545fe87`, 18 December 2023)**. If a later code change lands, these notes can go stale.

## What I am deliberately not documenting

- Employer stacks, internal datasets, or anything that is not in this public student repo.
- Invented ROUGE / BERTScore tables. The 2023 run did not leave numbers in git.
- How to deploy a summarizer in production. This was a course experiment.
