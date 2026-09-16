# Personal notes for the 2023 Danish summarizer

This folder is a personal workbook, not the course hand-in. The scripts at
the repository root are the ITU Advanced NLP and Deep Learning (2023)
pipeline. The Sejerø Tidende desk in `sejeroe/` is a later, download-free
way to look at what those hops do to a news manchet.

| Note | Topic |
| --- | --- |
| [01-sejeroe-desk.md](01-sejeroe-desk.md) | Why this island paper exists |
| [02-manchet.md](02-manchet.md) | Inverted pyramid and first-sentence coverage |
| [03-five-w.md](03-five-w.md) | 5W1H slot cards |
| [04-quotes-and-connectives.md](04-quotes-and-connectives.md) | Attribution and `men` / `hvis` / `fordi` |
| [05-length-and-packing.md](05-length-and-packing.md) | Compounds, budgets, overflow cuts |
| [06-course-scripts.md](06-course-scripts.md) | Archaeology of the 2023 root scripts |
| [07-workbook.md](07-workbook.md) | Exercises that run offline |
| [08-reproduction.md](08-reproduction.md) | How the GPU pipeline was actually run |
| [generated/](generated/README.md) | Frozen desk notes |

Original course workflow (needs models and a corpus that is not in git):

```bash
python Ctranslate_converter.py
python translate.py
python summary.py
python translate_back.py
python finetune.py
python use_model.py
python eval.py
```
