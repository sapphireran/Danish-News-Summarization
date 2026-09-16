# Personal project notes

These notes belong to the 2023 ITU course project **Danish-News-Summarization**.
They describe the pipeline that is actually in this repository, not a cleaned-up
rewrite. The original scripts are left as they were submitted.

Start here:

| Document | What it covers |
| --- | --- |
| [pipeline.md](pipeline.md) | End-to-end label-generation and training flow |
| [datasets.md](datasets.md) | CSV columns, filenames, and split conventions |
| [models.md](models.md) | Translation, summarization, and mT5 checkpoints |
| [training-and-eval.md](training-and-eval.md) | Fine-tuning arguments and evaluation metrics |
| [design-notes.md](design-notes.md) | Why the project is shaped this way, plus caveats |
| [reproduction.md](reproduction.md) | Local directory layout and a practical runbook |
| [script-map.md](script-map.md) | File-by-file map of the original course scripts |

Runnable, model-free walkthroughs live in [`examples/`](../examples/README.md).
They use small original sample articles so the CSV contracts can be inspected
without downloading Helsinki-NLP, T5, or mT5 weights.
