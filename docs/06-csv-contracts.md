# CSV contracts

The 2023 scripts communicate only through CSV files. There is no shared
Python package. Column names below are taken from the committed files.

## Hop 0 — raw Danish news

`translate.py` reads `10000_articles_without_linebreaks.csv`.

| Column | Role |
| --- | --- |
| `id` | passed through |
| `article text` | Danish body (space in the name) |

Pakhuset's stand-in is `examples/data/00_raw_articles.csv` with the same
two columns. Rows are fictional Toftevig copy, not the course dump.

## Hop 1 — translated articles

`translate.py` writes `translated_articles.csv`.

| Column | Role |
| --- | --- |
| `id` | passed through |
| `body` | original Danish (renamed from `article text`) |
| `translated` | English |

`summary.py` reads `translated` and also keeps `body` and `id`.

## Hop 2 — English summaries

`summary.py` writes `summarized_file_ml80_rp5.0.csv`. The filename
encodes `max_length=80` and `repetition_penalty=5.0`.

| Column | Role |
| --- | --- |
| `id` | passed through |
| `body` | Danish |
| `translated` | English article |
| `summary` | English summary (concatenated panes) |

## Hop 3 — Danish silver labels

`translate_back.py` writes `labeled_dataset_ml80_rp5.0.csv`.

| Column | Role |
| --- | --- |
| `id` | passed through |
| `body` | Danish article |
| `summary` | Danish silver label |

English columns are dropped here. After this file, the cascade cannot be
replayed without hop 1–2 artifacts.

## Hop 4 — fine-tune splits

`finetune.py` reads three files under `datasets/`:

- `train_dataset.csv`
- `validation_dataset.csv`
- `test_dataset.csv`

| Column | Role |
| --- | --- |
| `id` | removed in `map` |
| `body` | mT5 encoder input, truncate 1024 |
| `summary` | mT5 decoder target, truncate 128 |

The committed repo does not include those files or the split script.

## Public evaluation shape

`eval.py` / `use_model.py` expect a Hugging Face dataset with
`input_text`, `target_text`, `text_len`, `summary_len`. That is the
Nordjylland summarization schema, **not** the silver-label schema.
Fine-tune CSVs cannot be passed to `eval.py` without renaming columns.

## Lab extras (not in the 2023 run)

| File | Extra columns |
| --- | --- |
| `examples/data/pane_trace.csv` | `hop`, `pane_id`, `n_sentences`, `approx_units`, `budget`, `fill_ratio`, `text` |
| `examples/data/03_labeled_oracle.csv` | hand-written Danish briefs for Toftevig |
| `examples/data/concat_scores.csv` | echo / truncation / figure-survival metrics |

`pakhus.schemas` validates both the course contracts and the lab extras.
A missing space in `article text` is a hard error: that is the name
`translate.py` reads.
