# Personal notes for Danish news summarization

This folder is a personal write-up of the ITU Advanced NLP and Deep Learning
(2023) course project. The scripts at the repository root are the original
course artifacts. The notes here reconstruct how those scripts were meant to
be run, which files they expect, and where the 2023 code is brittle.

Nothing in `docs/` or `examples/` is company work. It only documents this
personal repository.

## Why this project exists

Danish abstractive summarization data was (and still is) thinner than English
news data. The course project therefore built **silver labels** instead of
hiring annotators:

1. Translate Danish news into English.
2. Summarize the English text with an off-the-shelf English news T5.
3. Translate the English summaries back into Danish.
4. Fine-tune mT5 on the resulting Danish `(article, summary)` pairs.
5. Compare the fine-tuned model against a human-written Danish news
   summarization test set (Nordjylland News).

The idea is a **pivot-language pipeline**. English is used only as an
intermediate language because English summarizers were stronger and cheaper
to reuse in 2023 than training a Danish summarizer from scratch.

## Document map

| Note | What it covers |
| --- | --- |
| [pipeline.md](pipeline.md) | End-to-end stage order, artifacts, and data-flow diagram |
| [datasets.md](datasets.md) | CSV schemas, Hugging Face eval sets, and split conventions |
| [translation.md](translation.md) | OPUS-MT + CTranslate2 conversion and sentence packing |
| [summarization.md](summarization.md) | English T5 summarizer, chunking, and generation knobs |
| [finetuning.md](finetuning.md) | mT5 training arguments and local checkpoint layout |
| [evaluation.md](evaluation.md) | ROUGE, BERTScore, and the two inference scripts |
| [troubleshooting.md](troubleshooting.md) | Known bugs, version drift, and recovery steps |
| [design-notes.md](design-notes.md) | Why pivot-language silver labels, and what I would change |

Runnable stand-ins that do **not** require GPUs or Hugging Face downloads live
in [`../examples/`](../examples/README.md).
