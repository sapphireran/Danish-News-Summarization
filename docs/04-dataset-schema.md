# Dataset schema and file names

Every CSV the original scripts read or write is listed here, plus the synthetic example files that ship in this repository. Names are case-sensitive and include historical typos (`bodys` in variable names, spaces in column titles).

## Raw Danish corpus (not in git)

**File:** `10000_articles_without_linebreaks.csv`

| column | type | required by |
| --- | --- | --- |
| `id` | string or int | `translate.py` |
| `article text` | string | `translate.py` (`df['article text']`) |

Notes:

- The space in `article text` is real. Downstream files rename it to `body`.
- Line breaks should already be flattened to spaces. Embedded newlines inside quoted CSV fields will survive `pandas.read_csv` but will confuse mental diffs and some editors.
- Additional columns are ignored.

This file is **not** committed. The 2023 corpus was a local extract of Danish news and may not be redistributable. Use `examples/data/sample_articles.csv` for a public, original substitute.

## After Danish → English

**File:** `translated_articles.csv`

| column | source |
| --- | --- |
| `id` | passed through |
| `body` | original Danish (`article text`) |
| `translated` | English article |

Produced by `translate.py`. Consumed by `summary.py`.

## After English summarization

**File:** `summarized_file_ml80_rp5.0.csv`

The filename encodes two generation knobs: `max_length=80`, `repetition_penalty=5.0`. If you change those, rename the file or you will mix runs.

| column | language | source |
| --- | --- | --- |
| `id` | — | passed through |
| `body` | Danish | passed through |
| `translated` | English | passed through |
| `summary` | English | T5 output |

Consumed by `translate_back.py`, which reads only `summary`, `body`, and `id`.

## After English → Danish (silver labels)

**File:** `labeled_dataset_ml80_rp5.0.csv`

| column | language | source |
| --- | --- | --- |
| `id` | — | passed through |
| `body` | Danish | original article |
| `summary` | Danish | back-translated T5 lead |

This is the factory's finished product. English columns are dropped on purpose.

## Fine-tune splits (not produced by a script)

`finetune.py` expects three files that **you** create:

```
datasets/train_dataset.csv
datasets/validation_dataset.csv
datasets/test_dataset.csv
```

Each must have:

| column | used as |
| --- | --- |
| `id` | dropped after tokenization (`remove_columns=["id", "body", "summary"]`) |
| `body` | encoder input, truncated to 1024 |
| `summary` | decoder labels, truncated to 128 |

Recommended split practice (not enforced by code):

- Split **by article id**, never by row after exploding packs.
- Hold out entire outlets or dates if you can, to reduce leakage from follow-up stories.
- Do not put Nordjylland News evaluation articles in these CSVs. That would contaminate the official test.

A simple starting point for a revival:

```
80% train / 10% validation / 10% internal test
```

The internal test is for factory ablation. Official numbers still come from `eval.py`.

## External evaluation sets

These are Hugging Face datasets, not local CSVs.

### `ScandEval/nordjylland-news-summarization-mini`

Used by `use_model.py` (`split="test"`).

| column | role |
| --- | --- |
| `input_text` | Danish article |
| `target_text` | Danish reference summary |
| `text_len` | dropped |
| `summary_len` | dropped |

### `alexandrainst/nordjylland-news-summarization`

Used by `eval.py` (`split="test"`). Same column names. Larger. This is the score you quote.

Both loaders assume those four columns exist. If the Hub cards change, `remove_columns` will throw.

## Synthetic example files (committed)

All live under `examples/data/` and are original fiction.

| file | mirrors | columns |
| --- | --- | --- |
| `sample_articles.csv` | raw corpus | `id`, `article text` |
| `sample_translated.csv` | `translated_articles.csv` | `id`, `body`, `translated` |
| `sample_summaries_en.csv` | `summarized_file_ml80_rp5.0.csv` | `id`, `body`, `translated`, `summary` |
| `sample_labeled_da.csv` | `labeled_dataset_ml80_rp5.0.csv` | `id`, `body`, `summary` |
| `sample_finetune_split/train.csv` | train split | `id`, `body`, `summary` |
| `sample_finetune_split/validation.csv` | val split | `id`, `body`, `summary` |
| `sample_finetune_split/test.csv` | internal test | `id`, `body`, `summary` |

`examples/inspect_sample_dataset.py` checks that ids align across the four pipeline hops and that the fine-tune split is a partition of `sample_labeled_da.csv`.

## Identifier rules

- Ids in the original project were integers from the source dump.
- Example ids use the prefix `SYN-` so they cannot be mistaken for real CMS ids.
- Ids must be unique inside a file. `inspect_sample_dataset.py` and `tests/test_sample_data.py` enforce that for the synthetic set.
- Never reuse a `SYN-` id for a real article if you later mix files.

## Encoding

All writers use `encoding='utf-8'` without a BOM. Danish letters (`æøåÆØÅ`) must survive a round-trip. The tests read the sample CSVs with `pandas` and assert that those letters are still present in at least one body.

## Empty and null values

None of the original scripts drop NA rows. A missing `article text` becomes `nan` (the float), which then blows up `sent_tokenize`. Clean before you start:

```python
df = df.dropna(subset=["article text"])
df = df[df["article text"].str.strip().astype(bool)]
```

Silver summaries that come back empty should be dropped before fine-tune; otherwise mT5 learns a valid "say nothing" mode.

## Column-name cheat sheet

```
article text  →  body  →  body  →  body  →  body
                 translated → translated →  (dropped)
                              summary(en) → summary(da) → summary
```

Hugging Face eval sets use `input_text` / `target_text` instead of `body` / `summary`. `use_model.py` and `eval.py` are the only scripts that know those names.
