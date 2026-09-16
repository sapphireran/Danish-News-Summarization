# Documentation index

This folder documents the personal ITU 2023 course project in
`Danish-News-Summarization`. The original repository only shipped seven
Python scripts and a short README. These notes reconstruct the method,
data contracts, and evaluation setup from those scripts so the pipeline
can be reread without reverse-engineering every file.

| Document | What it covers |
| --- | --- |
| [pipeline.md](pipeline.md) | End-to-end silver-label and fine-tuning flow |
| [design_notes.md](design_notes.md) | Why the project pivots through English |
| [datasets.md](datasets.md) | CSV schemas, Hugging Face eval sets, field-name mismatches |
| [models.md](models.md) | OPUS-MT, CTranslate2, English T5, mT5 |
| [script_reference.md](script_reference.md) | Per-file inputs, outputs, and hardcoded paths |
| [training.md](training.md) | Fine-tuning hyperparameters and hardware notes |
| [evaluation.md](evaluation.md) | ROUGE, BERTScore, and how to inspect generations |
| [reproduction.md](reproduction.md) | Practical reproduction checklist |
| [limitations.md](limitations.md) | Known gaps in the 2023 scripts |
| [glossary.md](glossary.md) | Terms used in the notes and examples |
| [course_context.md](course_context.md) | Course framing and related public work |

Runnable walkthroughs that do **not** download multi-gigabyte models live
in [`../examples/`](../examples/README.md).
