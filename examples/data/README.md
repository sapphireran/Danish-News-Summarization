# Sample data

Fictional North Jutland local-news tables that mirror the CSV contracts
in the 2023 scripts. Bodies, translations, and summaries were written
for this documentation. They are **not** TV2 Nord copy and must not be
treated as a benchmark.

Regenerate the CSV files after editing `corpus.py`:

```bash
python examples/data/write_tables.py
```

| File | Matches | Columns |
| --- | --- | --- |
| `sample_danish_articles.csv` | `translate.py` input | `id`, `article text` |
| `sample_translated_articles.csv` | `translate.py` output | `id`, `body`, `translated` |
| `sample_english_summaries.csv` | `summary.py` output | `id`, `body`, `translated`, `summary` (English) |
| `sample_labeled_dataset.csv` | `translate_back.py` output | `id`, `body`, `summary` (Danish) |
| `sample_train_split.csv` | `finetune.py` train | `id`, `body`, `summary` |
| `sample_validation_split.csv` | `finetune.py` validation | `id`, `body`, `summary` |
| `sample_test_split.csv` | `finetune.py` test | `id`, `body`, `summary` |
| `sample_predictions.csv` | evaluation demo | `id`, `reference`, `prediction` |
| `hyperparameters.json` | `finetune.py` defaults | structured copy of the training args |

`prediction` column values are intentionally imperfect stand-ins for a
fine-tuned model: they stay on topic but drop a constraint, invent a
minor emphasis, or collapse two facts. `examples/run_rouge_demo.py`
scores them against `reference`.

Split sizes: train 6 / validation 2 / test 2. That is only enough to
show the three-file layout `finetune.py` expects.
