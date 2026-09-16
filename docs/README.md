# Documentation index

This folder is a personal write-up of the 2023 ITU Danish news summarization project. It describes the repository as it exists in git, including quirks in the original scripts.

Start here if you are returning to the project after a long gap.

## Suggested reading order

1. [pipeline.md](pipeline.md) — what each script reads and writes.
2. [datasets.md](datasets.md) — column names and Hugging Face splits.
3. [models.md](models.md) — OPUS-MT, CTranslate2, T5, and mT5 roles.
4. [hyperparameters.md](hyperparameters.md) — numbers copied out of the scripts.
5. [evaluation.md](evaluation.md) — ROUGE, BERTScore, and qualitative inspection.
6. [design-notes.md](design-notes.md) — why silver labels, and the error budget.
7. [reproducing.md](reproducing.md) — a checklist for a full GPU run.
8. [troubleshooting.md](troubleshooting.md) — known mismatches between README claims and code.

## What is in scope

- Personal academic notes for this repository.
- File-level contracts so sample CSVs and later scripts stay aligned.
- CPU-only examples under `../examples/` that demonstrate chunking and schemas.

## What is out of scope

- Company or course-internal datasets that are not in this git tree.
- A rewrite of the 2023 training scripts. Those files stay at the repo root.
- Hosted model cards or published numbers. This archive does not claim a public leaderboard score.

## Quick map from question to file

| Question | Document |
| --- | --- |
| Which CSV is produced after summarization? | [pipeline.md](pipeline.md), [datasets.md](datasets.md) |
| Why is the converter missing `da-en`? | [models.md](models.md), [troubleshooting.md](troubleshooting.md) |
| What does `ml80_rp5.0` mean? | [hyperparameters.md](hyperparameters.md) |
| How is the article packed into 512 tokens? | [pipeline.md](pipeline.md), `../examples/text_chunking.py` |
| How should I split train/val/test? | [datasets.md](datasets.md), [reproducing.md](reproducing.md) |
| Why evaluate on Nordjylland News? | [evaluation.md](evaluation.md), [design-notes.md](design-notes.md) |
| Can I try this without a GPU? | [reproducing.md](reproducing.md), `../examples/README.md` |
