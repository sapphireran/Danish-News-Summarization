# Reproducing a full run

This is a personal checklist for replaying the 2023 pipeline on a machine you control. The original article dump and checkpoints are not in git.

## What you can do without a GPU

You can already:

- Read this folder and the expanded README.
- Run schema checks on `examples/sample_data/`.
- Pack long text with `examples/text_chunking.py`.
- Walk the CSV stage names with `python -m examples.demo_pipeline`.
- Run `python -m unittest discover -s tests -v`.

That path needs Python 3.9+ and the standard library.

## What you need for a GPU reproduction

- A CUDA GPU if you want `fp16` training as written (`finetune.py` sets `fp16=True`).
- Disk for two OPUS-MT CTranslate2 folders, T5-base, mT5-large, Trainer checkpoints, and `xlm-roberta-large` at eval time. Budget tens of GB to be safe.
- A Danish article CSV with `id` and `article text`.
- Python packages from `requirements.txt`.

CPU-only translation and summarization will run but will be slow at 10k articles. CPU `fp16` training is not what the script expects.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt')"
```

Hugging Face downloads happen at runtime (`from_pretrained`, `load_dataset`). Make sure the environment can reach `huggingface.co`.

## One-time model conversion

Edit `Ctranslate_converter.py` so **both** directions convert, then:

```bash
python Ctranslate_converter.py
```

Confirm the folders exist:

```text
models/opus-mt-da-en_ct2
models/opus-mt-en-da_ct2
```

## Labeling

1. Place the raw dump at `10000_articles_without_linebreaks.csv` (or change the path in `translate.py`).
2. `python translate.py` → `translated_articles.csv`
3. Remove `[:10]` in `summary.py` if you want more than ten summaries.
4. `python summary.py` → `summarized_file_ml80_rp5.0.csv`
5. `python translate_back.py` → `labeled_dataset_ml80_rp5.0.csv`
6. Split into `datasets/train_dataset.csv`, `datasets/validation_dataset.csv`, `datasets/test_dataset.csv` with columns `id,body,summary`.

A quick split in Python (not in the original tree):

```python
import csv
import random
from pathlib import Path

random.seed(2023)
rows = list(csv.DictReader(Path("labeled_dataset_ml80_rp5.0.csv").open(encoding="utf-8")))
random.shuffle(rows)
n = len(rows)
cuts = (int(0.8 * n), int(0.9 * n))
splits = {
    "datasets/train_dataset.csv": rows[: cuts[0]],
    "datasets/validation_dataset.csv": rows[cuts[0] : cuts[1]],
    "datasets/test_dataset.csv": rows[cuts[1] :],
}
Path("datasets").mkdir(exist_ok=True)
for path, part in splits.items():
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "body", "summary"])
        writer.writeheader()
        writer.writerows(part)
```

`examples/demo_pipeline.py` does the same job on the five-row sample with a hash split instead of `random.shuffle`.

## Fine-tune

```bash
python finetune.py
```

When it finishes, `./large_model` should contain a Transformers seq2seq save. Trainer extras live under `mt5-summarize-large/`.

## Point eval at the model you trained

In `eval.py` and `use_model.py`, load `large_model` (or copy it to `small_model`) before:

```bash
python use_model.py
python eval.py
```

`eval.py` will download Nordjylland News and XLM-R large on first run.

## Smoke test on the sample CSVs

If you only want to see that `finetune.py`'s CSV mapping would accept the columns, you can copy the example splits:

```bash
mkdir -p datasets
cp examples/sample_data/04_train_dataset.csv datasets/train_dataset.csv
cp examples/sample_data/04_validation_dataset.csv datasets/validation_dataset.csv
cp examples/sample_data/04_test_dataset.csv datasets/test_dataset.csv
```

That is five fictional rows. It is enough to fail fast on a column typo, not enough to train.

## Environment notes

- `transformers.AutoTokenizer(..., use_auth_token=False)` will warn on current Transformers. Harmless if you are not using a gated model.
- `datasets.load_metric` will warn; functionality still works on older `datasets` but may disappear. `requirements.txt` pins a range that still has it, with a comment pointing at `evaluate`.
- `evaluation_strategy` was renamed to `eval_strategy` in newer TrainingArguments. If your Transformers install rejects the old name, use the name your version documents.

## Ethics and data

Use article text you have a right to process. The sample CSVs are fictional municipal-style notices written for this repository. Do not treat them as real reporting.
