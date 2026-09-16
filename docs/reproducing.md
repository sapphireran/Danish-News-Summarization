# Reproducing the personal course run

This is a working order, not a promise that the 2023 numbers will come
back bit-for-bit. Weights, library versions, and the private news dump all
moved.

## What you need

- A machine with a CUDA GPU if you want the 10k-article labeling run or
  mT5-large. CPU is enough for the examples and tests.
- Python 3.10 or newer.
- Disk for two OPUS-MT CTranslate2 models, one English T5, and one mT5.
- The private CSV `10000_articles_without_linebreaks.csv`, or a substitute
  with the same two columns.

If you only want to read the project, skip to [What you can run without
weights](#what-you-can-run-without-weights).

## Install

```
python -m pip install -r requirements.txt
```

`nltk.download("punkt")` is called from the original scripts. If the
machine cannot reach the NLTK servers, download `punkt` once elsewhere and
point `NLTK_DATA` at that folder.

## Full labeling run

1. In `Ctranslate_converter.py`, uncomment the `opus-mt-da-en` converter
   and its output directory.
2. Run `python Ctranslate_converter.py`.
3. Confirm both model directories exist under `models/`.
4. Place the Danish dump next to `translate.py`.
5. Run `python translate.py`.
6. Edit `summary.py` and remove `[:10]` unless you only want a smoke test.
7. Run `python summary.py`.
8. Run `python translate_back.py`.
9. Split `labeled_dataset_ml80_rp5.0.csv` into
   `datasets/train_dataset.csv`, `datasets/validation_dataset.csv`, and
   `datasets/test_dataset.csv`. Keep a row's `id` in only one split.

Expected intermediate columns are listed in [datasets.md](datasets.md).

## Fine-tune and score

1. Run `python finetune.py` if you have the GPU budget for mT5-large.
2. For a laptop-sized run, switch `model_name` to `google/mt5-small` and
   save to `./small_model`.
3. `python use_model.py` prints a few Nordjylland mini generations.
4. `python eval.py` scores the full Nordjylland test split. It will
   download `xlm-roberta-large` for BERTScore.

Read [limitations.md](limitations.md) before comparing a new score to an
old note. Inspection and evaluation do not use the same decode settings.

## What you can run without weights

These commands stay inside the repository and do not download models:

```
python -m unittest discover -s tests -v
python examples/inspect_csv_schema.py
python examples/chunk_sample_articles.py
python examples/simulate_labeling_pipeline.py
python examples/print_training_recipe.py
```

They are the intended on-ramp. The sample articles are fictional Danish
news written for this repo, so the chunking demo is readable without the
private dump.

## If a root script fails immediately

| Symptom | First check |
| --- | --- |
| `FileNotFoundError` on a CSV | you are on the example path, or the dump is missing |
| `FileNotFoundError` on `models/opus-mt-da-en_ct2` | da-en converter still commented out |
| tokenizer download hangs | egress / Hugging Face cache |
| `datasets.load_metric` errors | replace with `evaluate.load` |
| CUDA OOM in `finetune.py` | drop batch size before disabling fp16 |
| empty or clipped translations | NLLB prefix skip on OPUS-MT, see [translation.md](translation.md) |

## Personal-only scope

This repository is a student project. Do not copy company data, internal
prompts, or private work notes into the sample files or docs. The checked-in
examples stay fictional on purpose.
