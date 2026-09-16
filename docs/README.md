# Pakhuset notes

This folder is a personal reconstruction of the **windowing** that the 2023 ITU
course scripts actually do. The original Python files in the repository root
are left untouched. They are a frozen exam artifact, not a library.

The lab that accompanies these notes lives in `pakhus/` and `examples/`.
It does not download OPUS-MT, T5, or mT5. It packs fictional Toftevig
articles with the same budgets the course scripts hardcoded, then shows
what happens when every hop **repacks** the text.

| Note | What it is for |
| --- | --- |
| [01-why-windows.md](01-why-windows.md) | Why 512-token panes dominate this project |
| [02-packing-algorithm.md](02-packing-algorithm.md) | Line-level reconstruction of `translate.py` / `summary.py` |
| [03-repacking.md](03-repacking.md) | Windows are not preserved from hop to hop |
| [04-concatenation.md](04-concatenation.md) | Multi-pane summaries grow, then training truncates them |
| [05-script-scars.md](05-script-scars.md) | Hardcoded mismatches still in the 2023 files |
| [06-csv-contracts.md](06-csv-contracts.md) | Column names each script reads and writes |
| [07-danish-sentences.md](07-danish-sentences.md) | Abbreviations, ordinal dates, quotes |
| [08-reproduction.md](08-reproduction.md) | GPU course run vs CPU packing lab |
| [09-workbook.md](09-workbook.md) | Exercises against the Toftevig fixtures |
| [10-if-i-redid-this.md](10-if-i-redid-this.md) | What I would change in a later personal rerun |

Course context: ITU *Advanced Natural Language Processing and Deep Learning*
(2023), personal final project. Silver labels for Danish news summarization
were produced by a DA→EN→English-news-T5→EN→DA cascade, then used to
fine-tune mT5. Public evaluation was intended against Nordjylland-style
Danish news summarization data.
