# Reproduction notes

This repository can be cloned in one command. The experiment cannot. Weights, the 10k article dump, and the silver splits were never in git. This page is a conservative checklist for a **personal** rerun on a single GPU box.

## What a clone gives you

- Seven Python scripts and a MIT license
- This documentation
- An unpinned [`requirements.txt`](../requirements.txt) written in 2026 from import statements, not from a 2023 freeze

What a clone does **not** give you:

- `10000_articles_without_linebreaks.csv`
- any file matching `*.csv` used as input or output
- `models/opus-mt-da-en_ct2` or `models/opus-mt-en-da_ct2`
- `small_model/` or `large_model/`
- `datasets/train_dataset.csv` and friends
- a recorded `pip freeze` from the course environment
- a metric table

If those objects still exist, they are on an old ITU machine or a personal disk, not on GitHub.

## Suggested environment

I originally ran this on a CUDA Linux box with a recent-enough PyTorch for `fp16` mT5-large. A modern personal rerun should still be Linux + NVIDIA, not CPU, unless you only want to convert models and translate a handful of rows.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

`punkt_tab` is the newer NLTK split; 2023 only needed `punkt`. I download both so `sent_tokenize` works across NLTK versions.

Hub access: `eval.py` / `use_model.py` / `finetune.py` will pull datasets and models. You need outbound HTTPS to Hugging Face, or a pre-populated cache (`HF_HOME`).

Optional env vars I would set on a rerun:

```bash
export TOKENIZERS_PARALLELISM=false
export HF_HUB_DISABLE_TELEMETRY=1
```

I would **not** set `TRANSFORMERS_OFFLINE=1` until every checkpoint has been fetched once.

## Disk budget (order of magnitude)

These are planning numbers, not measurements from 2023.

| Object | Rough size |
| --- | --- |
| `opus-mt-da-en` + `opus-mt-en-da` (HF + CT2 copies) | a few hundred MB |
| `mrm8488/t5-base-finetuned-summarize-news` | ~900 MB |
| `google/mt5-large` | ~2.5 GB+ |
| `xlm-roberta-large` (BERTScore) | ~2 GB |
| 10k articles CSV | tens of MB |
| Intermediate CSVs | tens to low hundreds of MB |
| `mt5-summarize-large` checkpoints (even with `save_total_limit=1`) | several GB |
| `./large_model` | several GB |

Plan for **20+ GB** free if you fine-tune large and keep Hub caches.

## Artifact names the scripts expect

Create a working directory that is the repo root. The scripts do not take `--input` flags.

```text
./10000_articles_without_linebreaks.csv
./models/opus-mt-da-en_ct2/      # not produced by the converter as committed
./models/opus-mt-en-da_ct2/
./translated_articles.csv
./summarized_file_ml80_rp5.0.csv
./labeled_dataset_ml80_rp5.0.csv
./datasets/train_dataset.csv
./datasets/validation_dataset.csv
./datasets/test_dataset.csv
./small_model/                   # eval/use_model
./large_model/                   # finetune output
./mt5-summarize-large/           # Trainer dir
```

CSV schemas:

```text
10000_articles_without_linebreaks.csv
    id, article text

translated_articles.csv
    id, body, translated

summarized_file_ml80_rp5.0.csv
    id, body, translated, summary

labeled_dataset_ml80_rp5.0.csv
    id, body, summary

datasets/*_dataset.csv
    id, body, summary
```

`body` is always the **Danish** article after step 2. Do not replace it with English.

## Rerun checklist (conservative)

I would treat the committed Python as a draft and make a **local** (uncommitted, or a later personal branch) punch list before spending a GPU night:

1. Uncomment `opus-mt-da-en` conversion in `Ctranslate_converter.py`.
2. Remove NLLB `target_prefix` from both translate scripts; decode the full hypothesis.
3. Remove `[:10]` in `summary.py`.
4. Pass `text_max_length` into `translate_back.py`’s splitter; add a long-sentence breaker.
5. Write a tiny `split_csv.py` with `random.seed(2023)` and a recorded 90/5/5 or 80/10/10.
6. Save tokenizer in `finetune.py`: `mt5_tokenizer.save_pretrained("./large_model")`.
7. Point `eval.py` and `use_model.py` at `./large_model` and `google/mt5-large` (or the saved tokenizer).
8. Map Nordjylland columns after printing them, not before.
9. Set `dataloader_drop_last=False`.
10. Align `use_model.py` generate kwargs with `finetune.py` if the point is inspection of the trained system.

This documentation PR does **not** apply those code changes. They are listed so a future personal rerun is not a scavenger hunt.

## Minimal CPU smoke test (no claim of quality)

If you only want to see that imports resolve:

```bash
python -c "import pandas, torch, transformers, datasets, nltk, numpy"
```

CTranslate2 and a real GPU test are optional for import checking. I would not run `finetune.py` on CPU.

A safer smoke test for the **data** side, once a 10-row CSV exists:

- run conversion for `en-da` only (as committed)
- translate 1–2 short sentences in a REPL with OPUS-MT **without** prefixes
- summarize one English paragraph with the news T5
- back-translate that sentence

That validates hops. It does not validate training.

## Dataset revisions

Hugging Face datasets move. A serious rerun should pin:

```python
load_dataset("alexandrainst/nordjylland-news-summarization", revision="<commit>")
```

I do not have the 2023 revision hash. Record whatever `ds.cache_files` / dataset `fingerprint` you get.

ScandEval has been evolving into EuroEval. The mini dataset name may disappear or change schema. If the mini set 404s, qualitative eval should use 20 rows from the full test split.

## Licensing reminder (personal use)

- This repo: MIT.
- Nordjylland summarization: CC0-1.0 on the Hub card.
- OPUS-MT, T5, mT5, XLM-R: their Hub licenses (typically Apache 2.0 for the Google/Facebook families; check each card).
- The 10k dump: **unknown**. I would not republish it from this repo without knowing the news source license.

## If you only want to read, not rerun

Start at [evaluation-notes.md](evaluation-notes.md) and [known-issues.md](known-issues.md). The scientific caveats do not require a GPU.
