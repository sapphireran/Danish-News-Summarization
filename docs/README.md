# Personal notes for Danish-News-Summarization

This folder is a later write-up of the ITU 2023 course project in this
repository. The original Python scripts at the repo root are unchanged
course code. The notes here explain what those scripts actually do, which
file schemas they expect, and where the 2023 assumptions have drifted.

Start here:

| Note | What it covers |
| --- | --- |
| [pipeline.md](pipeline.md) | DA→EN→summarize→DA labeling flow and how articles are chunked |
| [dataset-schema.md](dataset-schema.md) | Column contracts for every CSV the scripts read or write |
| [training.md](training.md) | mT5 fine-tune settings copied out of `finetune.py` |
| [evaluation.md](evaluation.md) | ROUGE / BERTScore setup and the Nordjylland field-name trap |
| [reproduction.md](reproduction.md) | What you need to re-run the neural pipeline vs the offline examples |
| [limitations.md](limitations.md) | Known bugs, debug leftovers, and metric caveats |
| [course-notes.md](course-notes.md) | Why the project used silver labels instead of human Danish summaries |

Runnable stand-ins that do **not** download models live in
[`examples/`](../examples/README.md).
