# Docs

Personal notes for the ITU 2023 Danish news summarization project.
The GPU scripts in the repository root are unchanged; these pages
explain them and point at the CPU-only examples.

| Page | What it covers |
| --- | --- |
| [pipeline.md](pipeline.md) | Translate → summarize → translate-back → mT5 |
| [dataset.md](dataset.md) | Silver-label CSVs vs. Nordjylland Hub sets |
| [models.md](models.md) | OPUS-MT, English T5, mT5, BERTScore backbone |
| [training.md](training.md) | Hyperparameters copied from `finetune.py` |
| [evaluation.md](evaluation.md) | ROUGE, BERTScore, qualitative checklist |
| [examples.md](examples.md) | How to run the CPU demos |
| [troubleshooting.md](troubleshooting.md) | Failures the scripts already hint at |
| [original-scripts.md](original-scripts.md) | One section per root `*.py` |
| [design-notes.md](design-notes.md) | What was extracted, and what was left alone |

Start here if you have one afternoon and no GPU:

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
PYTHONPATH=. python examples/walk_one_article.py dn-009
```
