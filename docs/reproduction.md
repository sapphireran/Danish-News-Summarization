# Reproduction

Two tracks. They do not share checkpoints.

## A. CPU examples (this documentation pass)

No CUDA, no Hugging Face downloads, no 10k CSV.

```bash
python -m pip install -e ".[dev]"
python examples/build_sample_csvs.py
python examples/04_inspect_csv_schema.py
python examples/01_chunk_danish_article.py --article-id harbour-plan --max-units 40
python examples/05_window_budget.py --article-id harbour-plan
python examples/02_pipeline_dry_run.py
python examples/03_evaluate_toy_summaries.py --format markdown
python -m pytest
```

`02_pipeline_dry_run.py` writes glossary output under `examples/output/`.
That directory is gitignored. The committed CSVs in `examples/data/` stay
human-authored.

## B. GPU course pipeline (historical)

You need a machine with CUDA, the Python stack in `requirements.txt`, and
the original article CSV (not in git).

1. Convert **both** OPUS-MT directions to CTranslate2. Uncomment the
   `opus-mt-da-en` block in `Ctranslate_converter.py` first.
2. `python translate.py` → `translated_articles.csv`
3. In `summary.py`, remove `[:10]` if you want more than ten rows.
   `python summary.py` → `summarized_file_ml80_rp5.0.csv`
4. `python translate_back.py` → `labeled_dataset_ml80_rp5.0.csv`
5. Split that file into `datasets/train_dataset.csv`,
   `datasets/validation_dataset.csv`, `datasets/test_dataset.csv`.
6. `python finetune.py` → `./large_model`
7. Point `eval.py` / `use_model.py` at that directory (they currently load
   `small_model`) and run evaluation on Nordjylland.

Approximate disk: OPUS-MT CT2 dirs, T5-base, mT5-large, and 10k CSVs.
The first translation pass is the long job; CTranslate2 on GPU makes it
tractable. Fine-tuning mT5-large for 20 epochs is the expensive step.

NLTK `punkt` is downloaded at import time in several scripts. On a
fresh machine that needs network egress.

## Environment notes

* The course scripts assume a Transformers release from 2023. Current
  `Seq2SeqTrainingArguments` parameter names have shifted; see
  [design-notes.md](design-notes.md).
* `nltk.download('punkt')` in imported modules makes the scripts noisy
  and non-hermetic. The CPU package does not use NLTK.
* Do not commit `models/`, `*_model/`, or news CSVs. `.gitignore` already
  lists those paths.

## Checking that the docs still match the scripts

The default filenames and column names are centralized in
`danish_news/schemas.py` (`DEFAULT_FILENAMES`, `STAGE_SCHEMAS`). If a
root script is edited, update that module and `docs/dataset.md` in the
same change. `examples/04_inspect_csv_schema.py` will not catch a rename
inside `translate.py`; it only checks the fixtures.
