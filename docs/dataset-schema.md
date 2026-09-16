# Dataset schema

Personal contract sheet for every CSV this repository names. Column names are copied from the December 2023 scripts, including the awkward space in `article text`.

Nothing here is an employer schema. The 10k dump was never committed; the only committed rows are the fictional fixtures under [`examples/data/`](../examples/data/README.md).

## Encoding and quoting

- UTF-8, no BOM.
- pandas `to_csv(..., index=False, encoding='utf-8')` on the write path (`translate.py`, `summary.py`, `translate_back.py`).
- Header row required. The scripts index columns by name, not position.
- Newlines inside a cell are legal in pandas CSV but the 2023 source filename (`10000_articles_without_linebreaks.csv`) says I had already flattened bodies. The toy articles are single-paragraph on purpose.

## Stage 0 — unlabeled Danish news

**Filename on `main`:** `10000_articles_without_linebreaks.csv`  
**Toy stand-in:** `examples/data/sample_articles.csv`

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | string | yes | Opaque in the real dump; slugs in the toy set. Must be unique. |
| `article text` | string | yes | Danish body. The space is part of the name. `translate.py` does `df['article text']`. |

`translate.py` does not check nulls. An empty body becomes an empty English string and still occupies a row.

## Stage 1 — after Danish → English

**Filename:** `translated_articles.csv`  
**Toy stand-in:** `examples/data/sample_translated.csv`

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | string | yes | Copied from stage 0. |
| `body` | string | yes | Original Danish. The input column was renamed from `article text`. |
| `translated` | string | yes | English pivot article. |

`summary.py` reads `translated` and `body`. It never looks at `article text`.

## Stage 2 — after English summarization

**Filename:** `summarized_file_ml80_rp5.0.csv`  
**Toy stand-in:** `examples/data/sample_summaries_en.csv`

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | string | yes | |
| `body` | string | yes | Still the original Danish article. |
| `translated` | string | yes | English article (kept, not needed by the next hop). |
| `summary` | string | yes | **English** summary. The filename suffix is `max_length=80`, `repetition_penalty=5.0`. |

`translate_back.py` translates only `summary`. `body` is passed through untouched so the silver pair stays aligned.

## Stage 3 — silver Danish pairs

**Filename:** `labeled_dataset_ml80_rp5.0.csv`  
**Toy stand-in:** `examples/data/sample_labeled.csv`

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | string | yes | |
| `body` | string | yes | Original Danish article (the mT5 source). |
| `summary` | string | yes | **Danish** silver label (the mT5 target). |

English columns are dropped here. After this file, the pipeline is monolingual Danish.

## Stage 4 — fine-tune splits

**Filenames on `main`:** `datasets/train_dataset.csv`, `datasets/validation_dataset.csv`, `datasets/test_dataset.csv`  
**Toy stand-ins:** `examples/data/splits/{train,validation,test}.csv`

Same three columns as stage 3: `id`, `body`, `summary`.

`finetune.py` tokenizes `body` → encoder (`max_length=1024`) and `summary` → labels (`max_length=128`), then **drops** `id`, `body`, and `summary`. If a split file has extra columns, `.map(..., remove_columns=["id", "body", "summary"])` leaves them in and `DataCollatorForSeq2Seq` may choke.

There is no committed splitter. In 2023 I cut the labeled CSV by hand. The toy 6/2/2 split is only a shape demo.

## Evaluation sets (not in this repo)

These are downloaded by `datasets.load_dataset` and must not be copied into git.

### `alexandrainst/nordjylland-news-summarization` (`eval.py`)

Public card (as of the 2023/2024 Hugging Face listing I used): article/summary pairs from TV2 Nord, CC0-1.0.

`eval.py` tokenizes `input_text` and `target_text` and removes `input_text`, `target_text`, `text_len`, `summary_len`. The card documents `text` / `summary`. That mismatch is a rerun blocker; see [script-contracts.md](script-contracts.md).

### `ScandEval/nordjylland-news-summarization-mini` (`use_model.py`)

Smaller qualitative split. Same column names as the ScandEval-shaped `eval.py` path. Do not assume it is a subset of the silver training ids.

## Validation rules the toy checker enforces

[`examples/validate_schema.py`](../examples/validate_schema.py) checks the fixtures (and any CSV you point at) for:

1. Exact header set — no missing, no extras unless `--allow-extra`.
2. Unique `id`.
3. No empty required cells.
4. Id alignment across stages (stage 1–3 must be the same id set as stage 0).
5. Split partition: train ∪ val ∪ test = labeled ids, pairwise disjoint.

It does **not** check Danish vs English. Language ID on ten hand-written rows would be theater.

## Worked row

`klintelund-cykelsti` through the four committed shapes:

| Stage | `body` / `article text` | `translated` | `summary` |
| --- | --- | --- | --- |
| 0 | Danish article | — | — |
| 1 | Danish article | English article | — |
| 2 | Danish article | English article | English summary |
| 3 | Danish article | — | Danish summary |

The only field that changes language twice is the compressed side. The source article stays Danish from stage 1 onward so mT5 never sees the English pivot.
