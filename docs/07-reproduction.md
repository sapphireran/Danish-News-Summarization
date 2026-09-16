# Reproduction notes

How to get back to a 2023-shaped run, and how to run the documentation examples that do not need that run.

## Two reproduction targets

| Target | Needs GPU / Hub weights | What "success" looks like |
| --- | --- | --- |
| Docs and examples | No | `pytest` green, demo scripts print expected sections |
| Full silver-label + mT5 | Yes | `labeled_dataset_*.csv` filled, `./large_model` saved, `eval.py` prints a metrics dict |

This repository guarantees the first. The second depends on data you must supply and on Hub checkpoints remaining public.

## Docs / examples (minutes, CPU)

```bash
python -m pip install -r requirements-examples.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
python examples/run_chunking_demo.py
python examples/inspect_sample_dataset.py
python examples/metrics_toy_eval.py
python -m pytest tests/
```

`punkt_tab` is required on NLTK 3.8.2+ / 3.9. If download fails, an older `nltk.download('punkt')` is enough for many 3.8.x installs. The example code tries both.

Expected artifacts: stdout traces only. Nothing is written under `models/`.

## Full pipeline (historical)

### Hardware

- One NVIDIA GPU with ≥ 16 GB is the comfortable bar for mT5-large at batch 8 with fp16.
- mT5-small + batch 4 can squeeze onto 8 GB if you only want a smoke train.
- CTranslate2 translation is happy on GPU or CPU; CPU is just slower.

### Software

```bash
# Install a CUDA torch wheel first, then:
python -m pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

Pin revisions if you need bit-identical text: Hugging Face models move. Record `transformers`, `ctranslate2`, and each model commit hash in your run notes.

### Data you must obtain yourself

1. A Danish article CSV with `id` and `article text`.
2. Converted CTranslate2 directories for both OPUS-MT directions.
3. After labeling, a manual 80/10/10 (or similar) split into `datasets/*.csv`.
4. Hub access to Nordjylland News datasets for eval.

Do not commit those articles here.

### Command sequence

```bash
python Ctranslate_converter.py
# also convert opus-mt-da-en (uncomment or duplicate the converter)

python translate.py
# edit summary.py to remove [:10] for a full run
python summary.py
python translate_back.py

# then split labeled_dataset_ml80_rp5.0.csv into datasets/{train,validation,test}_dataset.csv

python finetune.py
python use_model.py
python eval.py
```

Align `use_model.py` / `eval.py` `local_model_path` with the directory you actually saved (`./large_model` vs `small_model`).

### Known reproduction traps

1. **`use_auth_token=False`** is a deprecated Transformers argument. Newer releases want `token=False` or nothing.
2. **`datasets.load_metric`** was removed from recent `datasets`. Install an older `datasets` or rewrite metrics with `evaluate.load`.
3. **`evaluation_strategy`** was renamed to `eval_strategy` in recent Transformers. The 2023 scripts use the old name.
4. **OPUS-MT + `dan_Latn` prefixes:** verify outputs; see [01-pipeline.md](01-pipeline.md).
5. **Hub dataset names** (`ScandEval/...`, `alexandrainst/...`) can move. If load fails, check the current card; do not silently swap in silver labels.

## Recording a run

Copy this block into a gist or a local `runs/` note (and keep `runs/` gitignored):

```
date:
gpu:
torch / transformers / ctranslate2 / datasets:
opus-mt-da-en revision:
opus-mt-en-da revision:
t5 news revision:
mt5 revision:
article count:
factory filename:
split seed:
train hours:
eval ROUGE-1/2/L:
eval BERTScore F1:
qualitative verdict:
```

## What "reproduced" should mean

Bit-identical silver labels are unlikely across CTranslate2 versions. Aim for:

- Same code path (these scripts, or a documented fork).
- Same decoding knobs.
- Eval numbers within a small band (e.g. ±0.02 ROUGE-1) on the same official test set.
- No evaluation on the silver test split when you quote official numbers.

## CI-sized subset

`examples/data/` plus `tests/` is the subset meant to stay green on a laptop. It does not download models and does not require network after `pip install` and the NLTK download.
