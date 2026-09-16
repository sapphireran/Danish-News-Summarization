# Examples

Stdlib-only companions to the 2023 root scripts. They use the same CSV
column names and the same sentence-packing idea, but they never download
OPUS-MT, T5, or mT5.

The ten articles in `corpus.py` are original fiction. They are not the
course dump and they are not a benchmark.

## What you can run

From the repository root:

```bash
python examples/export_sample_csvs.py
python examples/toy_pipeline.py
python examples/metrics_demo.py
python examples/inspect_samples.py
python examples/inspect_samples.py --list
python -m unittest discover -s examples/tests -v
```

`toy_pipeline.py --json /tmp/pipeline_report.json` writes the same report
as structured data.

No `pip install` is required.

## Layout

| Path | Role |
| --- | --- |
| `corpus.py` | Source of truth: Danish/English bodies, both summaries, toy predictions |
| `schema.py` | Column contracts per pipeline stage |
| `text_chunking.py` | Port of the 2023 sentence packer without NLTK |
| `export_sample_csvs.py` | Writes `data/*.csv` from the corpus |
| `toy_pipeline.py` | Schema + id alignment + chunking report |
| `metrics_demo.py` | Unigram / LCS scores vs `toy_predictions.csv` |
| `inspect_samples.py` | Pretty-print selected articles |
| `data/` | Committed CSV snapshots (UTF-8) |
| `tests/` | `unittest` coverage for the above |

## How this maps to the course pipeline

| Course script | Example stand-in |
| --- | --- |
| `translate.py` input | `data/raw_articles.csv` (`id`, `article text`) |
| `translate.py` output | `data/translated_articles.csv` (`id`, `body`, `translated`) |
| `summary.py` output | `data/summarized_articles.csv` (adds English `summary`) |
| `translate_back.py` output | `data/labeled_dataset.csv` (`id`, `body`, Danish `summary`) |
| `finetune.py` splits | `data/train_dataset.csv` / `validation_dataset.csv` / `test_dataset.csv` |
| `eval.py` ROUGE | `metrics_demo.py` unigram + LCS (not the same numbers) |

English fields in the snapshots are **written**, not model output. They
show the shape of a successful pivot, not OPUS-MT quality.

## Chunking demo

`toy_pipeline.py` packs every Danish body with a word budget of 28
(`whitespace words + 2 special tokens`). That budget is smaller than the
460-token labeling budget so the short fiction articles still split.

`dn-006` (Frederikshavn harbor) is the long piece. The report prints each
packed chunk. `text_chunking.split_long_sentence` still uses the original
character-count rule when a single sentence overflows.

## Toy predictions

`data/toy_predictions.csv` is not a model. Each row is a hand-written
mistake that the course pipeline also made in the wild:

| Id | Injected error |
| --- | --- |
| dn-001 | Drops the clock time |
| dn-002 | Wrong city |
| dn-003 | Over-compressed weather warning |
| dn-004 | Hallucinated swimming hall |
| dn-005 | Near-copy of the gold summary |
| dn-006 | Drops the 187 million kroner figure |
| dn-007 | Swaps 19 and 12 weeks |
| dn-008 | Drops side details |
| dn-009 | “Cancelled” becomes “delayed” |
| dn-010 | Generic rewrite, loses names and numbers |

Read the notes on each `SampleArticle` in `corpus.py` while looking at
the metric table.

## Regenerating snapshots

If you edit `corpus.py`:

```bash
python examples/export_sample_csvs.py
python -m unittest discover -s examples/tests -v
```

Tests fail if a committed CSV header, id set, or Danish letter check
drifts away from the corpus.
