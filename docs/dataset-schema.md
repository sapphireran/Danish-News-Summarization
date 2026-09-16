# Dataset schemas

All course scripts talk to one another through CSVs. None of them read a
config file; the names below are the strings hardcoded in the Python.

The curated files in `examples/data/` follow the same contracts on six
invented articles. Validate them with:

```
python3 examples/schema_check.py
python3 examples/schema_check.py --list-schemas
```

## Stage 0 — raw Danish dump

**File:** `10000_articles_without_linebreaks.csv`  
**Reader:** `translate.py`

| Column | Role |
| --- | --- |
| `id` | Stable article id |
| `article text` | Danish body. The space in the name is real. |

The dump is not in this git repository (it is large and was local course
data). The example stand-in is `examples/data/sample_articles.csv`.

## Stage 1 — translated articles

**File:** `translated_articles.csv`  
**Writer:** `translate.py`  
**Reader:** `summary.py`

| Column | Role |
| --- | --- |
| `id` | Copied |
| `body` | Original Danish, renamed from `article text` |
| `translated` | English article |

## Stage 2 — English summaries

**File:** `summarized_file_ml80_rp5.0.csv`  
**Writer:** `summary.py`  
**Reader:** `translate_back.py`

| Column | Role |
| --- | --- |
| `id` | Copied |
| `body` | Original Danish |
| `translated` | English article |
| `summary` | English abstractive summary |

## Stage 3 — Danish silver labels

**File:** `labeled_dataset_ml80_rp5.0.csv`  
**Writer:** `translate_back.py`

| Column | Role |
| --- | --- |
| `id` | Copied |
| `body` | Original Danish |
| `summary` | Danish summary (English column dropped) |

## Stage 4 — fine-tune splits

**Files:** `datasets/train_dataset.csv`, `datasets/validation_dataset.csv`,
`datasets/test_dataset.csv`  
**Reader:** `finetune.py`

Same three columns as stage 3. The split itself is not scripted in this
repo; it was done by hand / notebook outside the committed files. The
example catalog tags each invented article with `train`, `validation` or
`test` so `examples/write_sample_csvs.py` can emit a tiny analogue.

`finetune.py` also drops `id` during tokenization:

```python
remove_columns=["id", "body", "summary"]
```

If a split file has extra columns, `datasets.Dataset.map` will keep them
unless they are listed here. Stick to the three-column contract.

## Evaluation sets (not produced by the pipeline)

`use_model.py` and `eval.py` do **not** read the silver-label CSVs.
They pull public Hugging Face datasets and expect these names:

| Column | Used as |
| --- | --- |
| `input_text` | Danish article |
| `target_text` | Danish reference summary |
| `text_len` | unused after `remove_columns` |
| `summary_len` | unused after `remove_columns` |

That matches `ScandEval/nordjylland-news-summarization-mini` as the
scripts were written. The public card for
`alexandrainst/nordjylland-news-summarization` now documents `text` /
`summary` instead of `input_text` / `target_text`. See
[evaluation.md](evaluation.md) before re-running `eval.py` against a
current snapshot.

## Character vs token length

`text_len` / `summary_len` on the Nordjylland sets are character counts.
The training tokenizer uses SentencePiece token counts with ceilings
1024 / 128. A Danish article that is short in characters can still
truncate if it is morphologically heavy; the opposite is also possible.
The example inspect script reports word counts, which sit between those
two measures and need no model download.
