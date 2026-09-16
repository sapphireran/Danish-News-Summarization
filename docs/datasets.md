# Datasets and file schemas

Two families of data show up in this project:

1. **Silver data** you build with the labeling pipeline (or inspect via `examples/data/`).
2. **Human eval data** pulled from Hugging Face at evaluation time.

Nothing in the first family is committed at the original 10k scale. The example snapshots are a ten-article fiction corpus with the same column names.

## Silver pipeline schemas

All paths below are the filenames hardcoded in the 2023 scripts unless noted.

### Raw articles

**File:** `10000_articles_without_linebreaks.csv`  
**Used by:** `translate.py`

| Column | Type | Meaning |
| --- | --- | --- |
| `id` | string or int | Stable article id |
| `article text` | string | Danish body, line breaks already stripped |

The original course dump is not in git. For schema experiments use `examples/data/raw_articles.csv`.

### After Danish → English

**File:** `translated_articles.csv`  
**Used by:** `summary.py`

| Column | Meaning |
| --- | --- |
| `id` | Same id |
| `body` | Original Danish article (`article text` renamed) |
| `translated` | English article from OPUS-MT |

### After English summarization

**File:** `summarized_file_ml80_rp5.0.csv`  
**Used by:** `translate_back.py`

| Column | Meaning |
| --- | --- |
| `id` | Same id |
| `body` | Original Danish article |
| `translated` | English article |
| `summary` | English silver summary (possibly concatenated chunks) |

The filename encodes generation knobs: `ml80` is `max_length=80`, `rp5.0` is `repetition_penalty=5.0`.

### After English → Danish (silver pairs)

**File:** `labeled_dataset_ml80_rp5.0.csv`

| Column | Meaning |
| --- | --- |
| `id` | Same id |
| `body` | Original Danish article |
| `summary` | Danish silver summary |

This is the table you split for fine-tuning.

### Fine-tune splits

**Directory:** `datasets/`  
**Files:** `train_dataset.csv`, `validation_dataset.csv`, `test_dataset.csv`  
**Used by:** `finetune.py`

| Column | Meaning |
| --- | --- |
| `id` | Same id |
| `body` | Danish article (encoder input) |
| `summary` | Danish summary (decoder target) |

`finetune.py` tokenizes `body` to 1024 tokens and `summary` to 128 tokens, then drops the raw text columns.

The example repo mirrors these files under `examples/data/` with a 6 / 2 / 2 split:

| Split | Ids |
| --- | --- |
| train | `dn-001` `dn-002` `dn-003` `dn-004` `dn-006` `dn-009` |
| validation | `dn-005` `dn-008` |
| test | `dn-007` `dn-010` |

## Example corpus (committed)

`examples/corpus.py` is the source of truth. `python examples/export_sample_csvs.py` rewrites the CSV snapshots.

Properties of the fiction set:

- Original Danish and English prose, written for this repository. Not scraped from news sites.
- One deliberately long article (`dn-006`) so the chunker has something to pack.
- Parallel fields: `body_da`, `body_en`, `summary_en`, `summary_da`.
- A separate `toy_predictions.csv` with intentionally imperfect Danish summaries for `examples/metrics_demo.py`.

Do not treat the example ROUGE-like scores as project results. They only show that the metric helpers run.

## Human evaluation sets

### `alexandrainst/nordjylland-news-summarization`

Loaded in `eval.py` as `split="test"`. Columns used after tokenization:

| Column | Role |
| --- | --- |
| `input_text` | Danish article |
| `target_text` | Human Danish summary |
| `text_len` | Dropped after tokenize |
| `summary_len` | Dropped after tokenize |

This is the fuller Nordjylland summarization set and is the one `eval.py` scores.

### `ScandEval/nordjylland-news-summarization-mini`

Loaded in `use_model.py` as `split="test"`. Same column names, smaller. Used only to print a few generations, not for the reported metric table.

The two scripts therefore **do not evaluate the same sample**. If you compare qualitative prints from `use_model.py` to numbers from `eval.py`, you are looking at different draws.

## Encoding and length

- All project CSVs should be UTF-8. The writers pass `encoding="utf-8"`.
- Danish characters (`æøåÆØÅ`) must survive the round trip. `examples/tests/test_schema.py` checks that the committed snapshots still contain them.
- `finetune.py` truncates bodies at 1024 sentencepiece tokens. A long municipal story can lose the tail. The labeling-time chunker does **not** apply that 1024 limit; only training does.

## Validation helpers

```bash
python examples/toy_pipeline.py
```

Checks:

- Every committed snapshot matches the schema for its stage.
- Ids are unique inside a file.
- Ids align across raw → translated → summarized → labeled.
- Train / validation / test are disjoint and cover the ten example ids.
- `toy_predictions.csv` uses the same ids as the labeled file.

`examples/schema.py` is the single list of column names. If you add a stage, add it there and in a test.
