# Documentation index

These notes expand the original one-page README into something you can actually rerun years later. They describe **this personal course repo**, not a product.

Read in this order if you are coming back to the project cold:

1. [overview.md](overview.md) — what problem the 2023 project tried to solve
2. [setup.md](setup.md) — environment, disk, and tokenizer downloads
3. [pipeline.md](pipeline.md) — the six scripts and the files they pass around
4. [datasets.md](datasets.md) — column contracts and the two news sources
5. [models.md](models.md) — OPUS-MT, the English T5 summarizer, and mT5
6. [training.md](training.md) — `finetune.py` hyperparameter sheet
7. [evaluation.md](evaluation.md) — `use_model.py` vs `eval.py`
8. [limitations.md](limitations.md) — why silver labels are silver
9. [troubleshooting.md](troubleshooting.md) — mismatches the committed scripts still have
10. [file-map.md](file-map.md) — script-by-script reference
11. [reproducing-course-run.md](reproducing-course-run.md) — a checklist, not a promise

Companion code that you can run without a GPU lives in [`../examples/`](../examples/README.md).
