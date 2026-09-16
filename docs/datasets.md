# Datasets

Two families of data appear in this project:

1. **Local CSVs** produced or consumed by the root scripts.
2. **Hugging Face datasets** used only at inspection and evaluation time.

Silver-label training never reads the Hugging Face Nordjylland sets. Those sets are treated as an external Danish reference.

## Local CSV contracts

All local tables are UTF-8 CSVs with a header row. The example files under `examples/sample_data/` use the same names and columns.

### `10000_articles_without_linebreaks.csv` (raw)

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | string | yes | Stable key. Used again in every later file. |
| `article text` | string | yes | Danish body. The original dump had line breaks stripped. |

`translate.py` does not look at any other column. Extra columns are dropped when the output frame is built.

### `translated_articles.csv`

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | string | yes | Copied |
| `body` | string | yes | Original Danish, renamed from `article text` |
| `translated` | string | yes | English article |

From this point on the Danish text is always called `body`.

### `summarized_file_ml80_rp5.0.csv`

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | string | yes | Copied |
| `body` | string | yes | Original Danish |
| `translated` | string | yes | English article |
| `summary` | string | yes | **English** summary |

If you change `max_length` or `repetition_penalty` in `summary.py`, rename the file or you will overwrite a previous decode setting.

### `labeled_dataset_ml80_rp5.0.csv`

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | string | yes | Copied |
| `body` | string | yes | Original Danish |
| `summary` | string | yes | **Danish** silver summary |

`translated` is dropped here. Fine-tuning does not need the English pivot.

### `datasets/{train,validation,test}_dataset.csv`

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | string | yes | `finetune.py` drops this column after tokenize |
| `body` | string | yes | Encoder input |
| `summary` | string | yes | Decoder target |

`finetune.py` calls `remove_columns=["id", "body", "summary"]` after tokenization. If a CSV is missing one of those names, the map fails.

Suggested hygiene before training:

- Drop rows with empty `body` or `summary`.
- Drop exact duplicate `id`s. Keep the last write if you merged files.
- Confirm Danish on both sides (a leaked English summary is a labeling bug, not a tokenizer bug).
- Record the source labeled filename (`ml80_rp5.0` or otherwise) next to the split, so metrics stay attached to a decode setting.

## Example sample tables

`examples/sample_data/` ships a five-article walkthrough:

| File | Stage |
| --- | --- |
| `00_raw_articles.csv` | Raw Danish |
| `01_translated_articles.csv` | After da→en (hand-written English, not model output) |
| `02_summarized_articles.csv` | After English summarization (hand-written) |
| `03_labeled_dataset.csv` | After en→da (hand-written Danish summaries) |
| `04_train_dataset.csv` | 3 rows |
| `04_validation_dataset.csv` | 1 row |
| `04_test_dataset.csv` | 1 row |

The translations and summaries in those files are **author-written fixtures**, not CTranslate2 or T5 output. They exist so schema checks and demos stay deterministic.

## Hugging Face sets used in the scripts

### `ScandEval/nordjylland-news-summarization-mini`

Used by `use_model.py` (`split="test"`).

Columns referenced in code:

| Column | Role |
| --- | --- |
| `input_text` | Danish article |
| `target_text` | Danish reference summary |
| `text_len` | Dropped after tokenize |
| `summary_len` | Dropped after tokenize |

This is the small inspection set. It is not used for training.

### `alexandrainst/nordjylland-news-summarization`

Used by `eval.py` (`split="test"`).

Same column names as the mini set (`input_text`, `target_text`, `text_len`, `summary_len`).

This is a real Danish news summarization benchmark from the North Jutland / Alexandrainst line of work. The silver-label train set and this eval set are **not** guaranteed to share style, length, or lead bias. That domain gap is part of the experiment: can a model trained on translate-summarize-back labels transfer to a human (or professionally edited) Danish summary set?

## Length conventions

| Field | Typical tokenizer | Truncation in scripts |
| --- | --- | --- |
| Raw Danish article | OPUS-MT da-en | Packed to ~460 tokens per chunk, not truncated as a whole |
| English article | T5 news | Packed to 512 tokens per chunk |
| English summary | OPUS-MT en-da | Packed to ~460 tokens; usually one chunk |
| mT5 `body` | `google/mt5-*` | `max_length=1024` |
| mT5 `summary` | `google/mt5-*` | `max_length=128` (`use_model.py` uses 180 for labels) |

`use_model.py` tokenizes references to 180 tokens while generation is capped at 128. That mismatch can make printed references look longer than anything the model is allowed to emit.

## Recommended id format

Nothing in the 2023 scripts requires a particular `id` shape. The example data uses kebab-case slugs (`aalborg-library-hours`) so diffs stay readable. Integer ids from a scrape are fine.

`examples/schemas.py` accepts any non-empty string id.

## Splitting advice

Silver labels are generated independently per article, so a random split is acceptable. Still avoid leaking the same `id` into two splits.

`examples.demo_pipeline.split_labeled_rows` assigns each id to train/validation/test with a stable SHA-256 of the id string and a 80/10/10 cut on the first byte. That is good enough for the five-row demo. For a 10k-row dump you may prefer `sklearn.model_selection.train_test_split` with an explicit seed; that dependency is not required by this repo.

## What this repo does not include

- The original 10k Danish article dump.
- Trained `small_model` / `large_model` weights.
- CTranslate2 exports.
- Course hand-in reports or slides.

Those artifacts were local to the 2023 machine. The sample CSVs are the only tables that travel with git.
