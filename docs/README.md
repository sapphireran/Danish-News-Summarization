# Documentation

Personal notes for [sapphireran/Danish-News-Summarization](https://github.com/sapphireran/Danish-News-Summarization). ITU course project, 2023. Not employer documentation.

I split the pages so a future me can open one file instead of rereading the Python.

## Start here

1. [../README.md](../README.md) — what the repo is, and what is *not* in git.
2. [method-in-one-page.md](method-in-one-page.md) — the 2023 experiment in one screen.
3. [examples-guide.md](examples-guide.md) — the only path that runs without a GPU.
4. [dataset-schema.md](dataset-schema.md) — exact CSV headers, including the space in `article text`.
5. [script-contracts.md](script-contracts.md) — what each 2023 file reads, writes, and assumes.
6. [chunking-algorithm.md](chunking-algorithm.md) — the sentence packer, with a worked long sentence.
7. [toy-pipeline.md](toy-pipeline.md) — how the example hops map onto the original three models.
8. [hop-error-budget.md](hop-error-budget.md) — why translate–summarize–translate is leaky on purpose.

Runnable entry points live under [`../examples/`](../examples/README.md). The December 2023 training scripts stay at the repository root and are unchanged.

## Conventions

- **Silver label:** Danish summary from the pivot pipeline, not a journalist.
- **Gold / human label:** a Nordjylland (TV2 Nord) summary, evaluation only, not in this git tree.
- **Hop:** one model call (DA→EN, EN summarize, EN→DA).
- Paths are relative to the repository root.
- Descriptions of `translate.py` and friends refer to `main` at SHA `545fe87` (18 December 2023) unless a later commit says otherwise.

## Out of scope

- Invented ROUGE tables. The 2023 run did not leave numbers in git.
- Production serving, batch jobs, or cloud training recipes.
- Anything that is not this public student repository.
