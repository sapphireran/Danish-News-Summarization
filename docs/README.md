# Documentation

Personal notes for the 2023 ITU final project on Danish news summarization.
The course scripts in the repository root are the historical pipeline.
`danish_news/` and `examples/` are a later, CPU-only layer so the same
ideas can be inspected without CTranslate2 or mT5.

| Document | Contents |
| --- | --- |
| [pipeline.md](pipeline.md) | DA→EN → English T5 → EN→DA → mT5 fine-tune |
| [dataset.md](dataset.md) | CSV columns, splits, Nordjylland eval data |
| [models.md](models.md) | OPUS-MT, CTranslate2, T5, mT5 |
| [evaluation.md](evaluation.md) | ROUGE, BERTScore, generation settings |
| [design-notes.md](design-notes.md) | Why pivot translation, and known script quirks |
| [reproduction.md](reproduction.md) | GPU path vs CPU examples |
| [../examples/README.md](../examples/README.md) | Runnable walkthroughs |

Course context: Advanced Natural Language Processing and Deep Learning,
IT University of Copenhagen, 2023. License: MIT (see `LICENSE`).
