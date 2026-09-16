# Dataset schemas and splits

Every CSV in this project is UTF-8. None of the original 10k articles are checked in. The files under `examples/data/` are **original sample rows** written for documentation — same column names, tiny scale, no scraped news text.

## External corpora referenced by the scripts

| File or Hub id | Used by | Role |
| --- | --- | --- |
| `10000_articles_without_linebreaks.csv` | `translate.py` | Local Danish news dump (not in git) |
| `ScandEval/nordjylland-news-summarization-mini` | `use_model.py` | Tiny Hub split for eyeballing generations |
| `alexandrainst/nordjylland-news-summarization` | `eval.py` | Full Nordjylland summarization test set |

Nordjylland columns are `input_text`, `target_text`, `text_len`, `summary_len`. That is **not** the same schema as the silver-label CSVs (`id`, `body`, `summary`).

## Stage files produced by this repo

### `10000_articles_without_linebreaks.csv` (input only)

| Column | Type | Notes |
| --- | --- | --- |
| `id` | string or int | Stable article id. Must survive every join. |
| `article text` | string | Full Danish body, line breaks already removed in the 2023 dump. |

`translate.py` reads exactly those two names. Extra columns are ignored.

### `translated_articles.csv`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | same as input | Copied through |
| `body` | string | Original Danish (`article text` renamed) |
| `translated` | string | English pivot of the whole article |

### `summarized_file_ml80_rp5.0.csv`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | same | Copied through |
| `body` | string | Original Danish |
| `translated` | string | English article (still present) |
| `summary` | string | **English** abstract from T5. Name is reused later for Danish. |

The filename encodes generate settings: `ml80` = `max_length=80`, `rp5.0` = `repetition_penalty=5.0`. If you change those knobs, rename the file or you will mix runs.

### `labeled_dataset_ml80_rp5.0.csv`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | same | Copied through |
| `body` | string | Original Danish article |
| `summary` | string | **Danish** silver label |

This is the file you split for training.

### `datasets/train_dataset.csv`, `validation_dataset.csv`, `test_dataset.csv`

Same three columns as the labeled file. `finetune.py` tokenizes `body` → `input_ids` / `attention_mask` and `summary` → `labels`, then **drops** `id`, `body`, and `summary` from the Arrow dataset. Keep `id` in the CSV anyway so you can debug a bad generation later.

## Suggested split

`finetune.py` does not shuffle or split. A simple, reproducible approach:

```python
# Illustrative only — not wired into finetune.py
from sklearn.model_selection import train_test_split
import pandas as pd

df = pd.read_csv("labeled_dataset_ml80_rp5.0.csv")
df = df.dropna(subset=["id", "body", "summary"]).drop_duplicates("id")

train, holdout = train_test_split(df, test_size=0.20, random_state=2023)
val, test = train_test_split(holdout, test_size=0.50, random_state=2023)

train.to_csv("datasets/train_dataset.csv", index=False)
val.to_csv("datasets/validation_dataset.csv", index=False)
test.to_csv("datasets/test_dataset.csv", index=False)
```

Rules that matter more than the exact percentages:

1. **No id overlap** across the three files.
2. Drop rows with empty `body` or `summary` before tokenizing. Empty targets still tokenize and will poison the loss.
3. Do not evaluate the silver-label test split and call it "Danish summarization quality." Prefer Nordjylland (or another human-written set) for claims. The silver test split is only useful as a *teacher-fidelity* check: did mT5 learn to copy the pipeline's style?

## Length expectations

These are observational targets from the script settings, not hard filters:

| Field | Typical | Hard cap in a script |
| --- | --- | --- |
| Danish `body` | news article, often >512 OPUS tokens | Packed into 460-token chunks in `translate.py` |
| English `translated` | similar length to `body` | Packed into 512-token chunks in `summary.py` |
| English `summary` | a few sentences | `max_length=80` T5 tokens per *chunk*; multi-chunk articles can exceed that after concat |
| Danish `summary` | a few sentences | 128 mT5 tokens at train and eval generate time |

`examples/inspection/inspect_dataset.py` prints character-length histograms for the sample CSVs so you can see the shape without loading tokenizers.

## Quality filters worth applying before fine-tune

None of these are in the original scripts. Apply them if you rebuild the corpus:

- Summary character length / body character length between ~0.02 and ~0.40. Far outside that band is usually a failed translate or an empty T5 decode.
- Reject summaries that are near-copies of the first English sentence after back-translation (optional n-gram overlap check).
- Reject rows where `summary` still contains obvious English residues (`the`, `and`, `of` as standalone tokens) if you want a cleaner Danish teacher.
- Keep a sidecar JSONL of rejected ids so you can audit the filter.

`examples/validation/schema.py` implements the structural checks (columns, uniqueness, non-empty, summary-shorter-than-body). It does not try to detect language ID.

## Sample files

| Path | Mirrors |
| --- | --- |
| `examples/data/raw_articles.sample.csv` | Stage-0 input (`id`, `article text`) |
| `examples/data/translated_articles.sample.csv` | After `translate.py` |
| `examples/data/summarized_articles.sample.csv` | After `summary.py` |
| `examples/data/labeled_dataset.sample.csv` | After `translate_back.py` |
| `examples/data/train_dataset.sample.csv` | Fine-tune train split |
| `examples/data/validation_dataset.sample.csv` | Fine-tune val split |
| `examples/data/test_dataset.sample.csv` | Fine-tune test split |

Ids in the samples are `sample-001` … `sample-010`. They are fictional municipal-news sketches, not real articles.
