# Reproduction checklist

This is a practical list for rerunning the 2023 course project on a
single machine. The [`examples/`](../examples/README.md) demos do not
require any of this.

## Machine

- Linux or macOS, Python 3.10+ (the original year was 2023; 3.10/3.11
  are the least surprising).
- NVIDIA GPU with ≥16 GB VRAM for `mt5-large` at the checked-in batch
  size, or accept `mt5-small` and edit `finetune.py`.
- Disk: plan for ~10 GB of Hub downloads (mT5-large, T5-base, two OPUS
  models, XLM-R large) plus CTranslate2 copies and trainer checkpoints.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

`punkt_tab` is required on recent NLTK versions; the 2023 scripts only
call `nltk.download('punkt')`.

## Data you must supply

1. A CSV named `10000_articles_without_linebreaks.csv` with `id` and
   `article text`. How those articles were collected is outside this
   repo. Do not commit them.
2. After silver-labeling, a manual split into
   `datasets/train_dataset.csv`, `datasets/validation_dataset.csv`,
   `datasets/test_dataset.csv` with `id`, `body`, `summary`.

The fictional files in `examples/data/` can be copied into `datasets/`
if you only want to smoke-test `finetune.py` on a few rows.

## Command order

```bash
# 1. Convert BOTH OPUS directions (enable the da→en block first)
python Ctranslate_converter.py

# 2. Silver labels
python translate.py          # → translated_articles.csv
python summary.py            # remove the [:10] slice for a full run
python translate_back.py     # → labeled_dataset_ml80_rp5.0.csv

# 3. Split labeled_dataset_*.csv into datasets/*.csv yourself

# 4. Train
python finetune.py           # → ./large_model

# 5. Point eval / use_model at the directory you actually trained
#    or train mt5-small into small_model
python use_model.py
python eval.py
```

## Hugging Face access

All default model ids are public. A Hub token is only needed if you
hit rate limits. The scripts pass `use_auth_token=False` on the OPUS
tokenizers.

`eval.py` / `use_model.py` call `load_dataset(...)` on public sets.
The Alexandra Institute Nordjylland-News card is CC0; still cache it
locally and avoid republishing article text from that set inside this
personal repo.

## Common failures

| Symptom | Likely cause |
| --- | --- |
| `Translator` cannot open `models/opus-mt-da-en_ct2` | converter only emitted en→da |
| `KeyError: 'input_text'` in `eval.py` | dataset columns are `text` / `summary` |
| `KeyError: 'body'` in `finetune.py` | wrong CSV, still has `article text` |
| OOM during `trainer.train()` | mT5-large + 1024 tokens + batch 8 |
| `datasets.load_metric` warning / error | migrate to `evaluate.load` |
| `evaluation_strategy` warning | renamed to `eval_strategy` in recent Transformers |
| Empty or English-looking Danish labels | OPUS target prefixes / conversion mix-up |
| `small_model` not found | you saved `./large_model` only |

## Minimal “did the code import” check

You do not need weights to validate the example layer:

```bash
python examples/run_all_demos.py
```

That command is the reproduction path for the documentation itself.
