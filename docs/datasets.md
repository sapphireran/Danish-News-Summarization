# Datasets and CSV contracts

Every stage of the course pipeline is a CSV. Column names change twice: once
when Danish `article text` becomes `body`, and once when evaluation switches
to the public Nordjylland News schema.

The tables below match the committed scripts. Example files that obey the same
contracts live in `examples/sample_data/`.

## Stage 0 — raw Danish articles

**Used by:** `translate.py`
**Default path:** `10000_articles_without_linebreaks.csv`

| Column | Required | Notes |
| --- | --- | --- |
| `id` | yes | Stable article id, carried through every later file |
| `article text` | yes | Danish body. The name includes a space. |

Line breaks were already stripped in the course dump (`without_linebreaks` in
the filename). The translator still sentence-splits the text.

## Stage 1 — English translations

**Written by:** `translate.py`
**Default path:** `translated_articles.csv`

| Column | Required | Notes |
| --- | --- | --- |
| `id` | yes | Copied from stage 0 |
| `body` | yes | Original Danish (`article text` renamed) |
| `translated` | yes | English article |

`summary.py` later reads `translated` for the model and keeps `body` so the
Danish source is not lost.

## Stage 2 — English summaries

**Written by:** `summary.py`
**Default path:** `summarized_file_ml80_rp5.0.csv`

| Column | Required | Notes |
| --- | --- | --- |
| `id` | yes | |
| `body` | yes | Danish source article |
| `translated` | yes | English article (still present) |
| `summary` | yes | English summary; may be several chunk summaries joined by spaces |

Filename convention from the course run:

```text
summarized_file_ml{max_length}_rp{repetition_penalty}.csv
```

`ml80` and `rp5.0` match `summary.py` as committed (`max_length=80`,
`repetition_penalty=5.0`).

## Stage 3 — Danish silver labels

**Written by:** `translate_back.py`
**Default path:** `labeled_dataset_ml80_rp5.0.csv`

| Column | Required | Notes |
| --- | --- | --- |
| `id` | yes | |
| `body` | yes | Danish source article |
| `summary` | yes | Danish summary (translated from the English T5 output) |

This is the file that should be shuffled and split before fine-tuning.

## Stage 4 — train / validation / test splits

**Read by:** `finetune.py`
**Default paths:**

- `datasets/train_dataset.csv`
- `datasets/validation_dataset.csv`
- `datasets/test_dataset.csv`

| Column | Required | Notes |
| --- | --- | --- |
| `id` | yes | Dropped after tokenization |
| `body` | yes | Encoder input, truncated at 1024 tokens |
| `summary` | yes | Labels, truncated at 128 tokens |

`finetune.py` loads each file with `datasets.load_dataset('csv', ...)` and
then wraps them in a `DatasetDict`. Empty files or missing columns fail inside
that map, not earlier.

There is no committed splitter. `examples/split_labeled_dataset.py` is a
small, deterministic stand-in for personal experiments.

Suggested split for a 10k-article dump, if you redo the course setup:

| Split | Fraction | Purpose |
| --- | ---: | --- |
| train | 0.80 | mT5 updates |
| validation | 0.10 | epoch metrics + `load_best_model_at_end` |
| test | 0.10 | held-out silver labels (optional; `eval.py` uses a public set) |

Keep ids unique across the three files. Do not put the same article in more
than one split.

## Public evaluation sets

Qualitative and quantitative evaluation use Hugging Face datasets, not the
silver CSVs.

| Script | Dataset | Split | Text columns |
| --- | --- | --- | --- |
| `use_model.py` | `ScandEval/nordjylland-news-summarization-mini` | `test` | `input_text`, `target_text` |
| `eval.py` | `alexandrainst/nordjylland-news-summarization` | `test` | `input_text`, `target_text` |

Both also expose `text_len` and `summary_len`, which the tokenizers drop.

`eval.py` contains a commented line that points at the mini set. The committed
path is the full Alexandra Institute set.

## Encoding and empty values

All course scripts write UTF-8 CSVs without an index column. Treat blank
`body` or `summary` cells as corrupt rows and drop them before training.
mT5 will tokenize an empty string, but the resulting example is useless and
can skew ROUGE.

## Sample stand-ins in this repo

| File | Stage |
| --- | --- |
| `examples/sample_data/00_articles_sample.csv` | Stage 0 |
| `examples/sample_data/01_translated_sample.csv` | Stage 1 |
| `examples/sample_data/02_summarized_sample.csv` | Stage 2 |
| `examples/sample_data/03_labeled_sample.csv` | Stage 3 |
| `examples/sample_data/04_train_split_sample.csv` | Stage 4 train |
| `examples/sample_data/04_validation_split_sample.csv` | Stage 4 validation |
| `examples/sample_data/04_test_split_sample.csv` | Stage 4 test |

The sample articles are original fiction written for this archive. They are
not excerpts from the 2023 news dump.
