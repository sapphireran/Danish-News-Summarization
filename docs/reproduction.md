# Reproduction notes

A full 2023-style run needs a GPU, Hugging Face downloads, and the original (uncommitted) article dump. A laptop can still run the documentation examples.

## Two tracks

| Track | Purpose | Hardware | Network |
| --- | --- | --- | --- |
| Examples | Understand schemas, chunking, toy scores | Any CPU | None |
| Root scripts | Rebuild silver labels and train mT5 | CUDA GPU | Hugging Face Hub |

## Examples track (no models)

From the repository root:

```bash
python examples/export_sample_csvs.py
python examples/toy_pipeline.py
python examples/metrics_demo.py
python examples/inspect_samples.py
python -m unittest discover -s examples/tests -v
```

Expected: CSV snapshots rewritten in place (idempotent), a chunking report for `dn-006`, a metric table, a pretty-print of two articles, and a green unittest run.

Python 3.10+ is enough. No `pip install` is required for this track.

## Root-script track

### 1. Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt')"
```

`requirements.txt` uses major-version caps around the 2023 Transformers 4.x / datasets 2.x APIs. `evaluation_strategy` in `finetune.py` and `eval.py` was later renamed to `eval_strategy`. If you install Transformers 5, either edit the scripts or stay on 4.x.

### 2. Convert both OPUS-MT directions

Uncomment the `opus-mt-da-en` block in `Ctranslate_converter.py` (see [known-issues.md](known-issues.md)), then:

```bash
python Ctranslate_converter.py
```

Confirm you have:

```
models/opus-mt-da-en_ct2/
models/opus-mt-en-da_ct2/
```

### 3. Place the raw dump

`translate.py` reads `10000_articles_without_linebreaks.csv` with columns `id` and `article text`. To try the script on the example corpus without the 10k file:

```bash
# columns already match
cp examples/data/raw_articles.csv 10000_articles_without_linebreaks.csv
```

Then consider removing `[:10]` in `summary.py` if you want all ten labeled.

### 4. Label

```bash
python translate.py
python summary.py
python translate_back.py
```

Disk: each intermediate CSV is full article text plus translations. For 10k news stories budget a few hundred MB, not a few MB.

### 5. Split for fine-tuning

Create `datasets/` and write `train_dataset.csv`, `validation_dataset.csv`, `test_dataset.csv` with `id,body,summary`. A simple split is fine; stratifying by length is better if you have time.

The example split (6/2/2) is only for the fiction corpus. Do not train mT5-large on ten short stories and expect Nordjylland scores to move.

### 6. Train

```bash
python finetune.py
```

`google/mt5-large` + `fp16` + batch 8 + generate-on-eval is the expensive step. If you only have a small GPU, change `model_name` to `google/mt5-small` and lower `per_device_train_batch_size`. Remember that `eval.py` already assumes `small_model` and the small tokenizer.

### 7. Evaluate

Put weights where the inspect/eval scripts look (`small_model/`), or edit those paths, then:

```bash
python use_model.py
python eval.py
```

First BERTScore call downloads `xlm-roberta-large`.

## Seeds and determinism

The 2023 scripts do not set `seed`, `data_seed`, or `full_determinism`. Two fine-tunes will not match bit-for-bit. For a report, log the commit hash, the data snapshot, and the metric file even if you cannot replay the exact loss curve.

## Offline / air-gapped notes

Root scripts need Hub access unless you pre-seed the Hugging Face cache (`~/.cache/huggingface/`). The examples track does not.

## What “done” looked like in the course

1. Silver CSVs exist and ids line up.
2. `./large_model` or `small_model` contains `config.json` + weights.
3. `eval.py` prints a dict with ROUGE and BERTScore keys.
4. A short qualitative note on typical errors (wrong numbers, dropped locations, generic ledes).

This documentation repo adds a fifth check: `python -m unittest discover -s examples/tests -v` stays green so the schemas you think you have are the schemas the CSVs have.
