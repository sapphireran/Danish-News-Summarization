# Datasets

Three different “Danish news” objects show up in this project. They are not interchangeable.

## 1. Course dump — unlabeled Danish articles

**Filename the scripts expect:** `10000_articles_without_linebreaks.csv`

**Role:** raw material for silver labels.

**Columns `translate.py` reads:**

| Column | Type | Notes |
| --- | --- | --- |
| `id` | string or int | Must be unique. Copied through every later file. |
| `article text` | string | Full body. The course file had newlines already stripped. |

This file is **not** in git. It was a local 10k-row extract used for the 2023 run. The example stand-in is [`examples/data/raw_danish_articles.csv`](../examples/data/raw_danish_articles.csv) (same columns, 12 fictional articles).

### What “without linebreaks” means in practice

`nltk.sent_tokenize` is happier when paragraph breaks still exist, but the course dump flattened them. The chunker therefore relies on punctuation, not on `\n\n`. If you collect a fresh dump, keeping paragraphs is fine — the splitter will still work. Do not insert HTML.

### Recommended extra columns (optional)

The course scripts will ignore unknown columns if you drop them before `translate.py`. Useful extras if you rebuild a dump:

- `source` (outlet)
- `published_at`
- `url` (for dedup)
- `char_len` / `approx_tokens`

None of these are required.

## 2. Silver-label CSVs produced by the pipeline

These are the files the repo actually trains on.

### `translated_articles.csv`

| Column | Language | Source script |
| --- | --- | --- |
| `id` | — | pass-through |
| `body` | Danish | renamed from `article text` |
| `translated` | English | `translate.py` |

### `summarized_file_ml80_rp5.0.csv`

| Column | Language | Source script |
| --- | --- | --- |
| `id` | — | pass-through |
| `body` | Danish | pass-through |
| `translated` | English | pass-through |
| `summary` | **English** | `summary.py` |

The filename records generation settings (`max_length=80`, `repetition_penalty=5.0`), not a dataset version.

### `labeled_dataset_ml80_rp5.0.csv`

| Column | Language | Source script |
| --- | --- | --- |
| `id` | — | pass-through |
| `body` | Danish | pass-through |
| `summary` | **Danish** | `translate_back.py` |

### Fine-tune splits

`finetune.py`:

```python
train_dataset = load_dataset('csv', data_files='datasets/train_dataset.csv')['train']
validation_dataset = load_dataset('csv', data_files='datasets/validation_dataset.csv')['train']
test_dataset = load_dataset('csv', data_files='datasets/test_dataset.csv')['train']
```

Required columns: `id`, `body`, `summary`. The tokenizer map does `remove_columns=["id", "body", "summary"]`, so extra columns are only safe if you also change that list. Hugging Face `load_dataset('csv')` wraps a single CSV as a DatasetDict whose only split is named `'train'` — that is why validation is loaded with `['train']`.

Example splits: [`examples/data/finetune/`](../examples/data/finetune/).

### Suggested split policy (not enforced by the scripts)

For a 10k-article dump:

| Split | Fraction | Rule |
| --- | --- | --- |
| train | ~80% | unique ids |
| validation | ~10% | unique ids, used for `metric_for_best_model` |
| test | ~10% | unique ids, **do not** tune on this if you also score Nordjylland |

The silver test split is optional. The honest test set is Nordjylland (below). Keeping a silver test split is still useful for “did the model memorize translationese?” diagnostics.

## 3. Nordjylland news — human (or editorially written) Danish summaries

Two Hugging Face names appear in the scripts:

| Script | Dataset | Split | Why |
| --- | --- | --- | --- |
| `use_model.py` | `ScandEval/nordjylland-news-summarization-mini` | `test` | cheap qualitative sample |
| `eval.py` | `alexandrainst/nordjylland-news-summarization` | `test` | full metric run |

A commented line in `eval.py` shows the mini set was used during debugging.

### Columns `eval.py` / `use_model.py` expect

| Column | Meaning |
| --- | --- |
| `input_text` | Danish article |
| `target_text` | Danish reference summary |
| `text_len` | dropped after tokenize |
| `summary_len` | dropped after tokenize |

If the hub schema ever changes, the `remove_columns=[...]` lists will throw. That is the failure mode to look for first when `datasets` updates.

### Why this set is the real evaluation

Nordjylland summaries were not produced by this pipeline. Scoring on them answers: “does an mT5 trained on pivot-language silver labels write acceptable Danish news abstracts on an independent source?” Scoring on the silver test split only answers: “can mT5 imitate OPUS-MT ∘ T5 ∘ OPUS-MT?”

## Example corpus (this repo)

[`examples/data/`](../examples/data/) is a **fictional** 12-article mini-corpus written for documentation. It is not scraped news.

| File | Mirrors |
| --- | --- |
| `raw_danish_articles.csv` | course dump |
| `translated_articles.csv` | `translate.py` output |
| `summarized_articles.csv` | `summary.py` output |
| `labeled_danish.csv` | `translate_back.py` output |
| `finetune/train_dataset.csv` | `finetune.py` train |
| `finetune/validation_dataset.csv` | `finetune.py` val |
| `finetune/test_dataset.csv` | `finetune.py` test |
| `nordjylland_like_eval.csv` | `input_text` / `target_text` / lengths |

Articles cover typical Danish local-news shapes: weather, transport, culture, sport, municipal budget, research, labor, energy. They are long enough that the 460-token packer has something to do on a couple of rows, and short enough to read by eye.

## Length conventions used in the scripts

| Stage | Encoder cap | Decoder / generate cap |
| --- | --- | --- |
| OPUS-MT translate | 512, packed at 90% (460) | model default |
| English T5 | 512 | 80 |
| mT5 train | 1024 on `body` | 128 on `summary` |
| `use_model.py` tokenize | 1024 / 180 on labels | generate 128 |
| `eval.py` tokenize | 1024 / 128 on labels | trainer generate |

A silver summary that is a concatenation of many 80-token chunk summaries can exceed 128 tokens. Those targets are truncated in `tokenize_data`. Prefer fewer, tighter English summaries if you rerun labeling.

## Character encoding

All example CSVs are UTF-8. Danish letters (`æøåÆØÅ`) must survive every hop. `df.to_csv(..., encoding='utf-8')` is already in the course scripts. When you open a CSV in Excel on Windows, force UTF-8; otherwise you will think the translator is broken.

## Dedup and leakage

The course scripts do not hash articles. If you rebuild a dump from an outlet CMS, deduplicate on normalized body text before translation — OPUS-MT + T5 will otherwise amplify near-copies into the train set. Never put a Nordjylland article into the silver train set if you want a clean eval.
