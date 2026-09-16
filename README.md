# Danish News Summarization

Personal ITU course project (Advanced Natural Language Processing and Deep Learning, 2023): a **Danish abstractive summarizer** trained on *automatically generated* labels.

The idea is a classic low-resource trick. There was no large, clean Danish news-summary corpus available for the course, so the pipeline:

1. translates Danish articles into English,
2. summarizes them with a strong English news model,
3. translates the summaries back into Danish,
4. fine-tunes multilingual T5 (`mT5`) on those silver labels,
5. evaluates on a real Danish news-summarization benchmark.

This README is the short path through the repo. Longer notes live under [`docs/`](docs/README.md). Runnable CPU-only walkthroughs live under [`examples/`](examples/README.md).

## Why this approach

Danish is a high-resource language for *translation*, but a low-resource language for *abstractive summarization*. English news summarizers (T5 fine-tunes, BART, PEGASUS, …) were far stronger in 2023 than anything trained only on Danish. Crossing through English lets the project borrow that quality, at the cost of translationese and compounded errors. The docs go into those trade-offs instead of pretending the silver labels are gold.

## Repository layout

| Path | Role |
| --- | --- |
| `Ctranslate_converter.py` | Convert Helsinki-NLP OPUS-MT checkpoints to CTranslate2 |
| `translate.py` | Danish → English article translation |
| `summary.py` | English news summarization (T5), with long-article chunking |
| `translate_back.py` | English → Danish summary translation (silver labels) |
| `finetune.py` | Fine-tune `google/mt5-large` on the generated CSV splits |
| `use_model.py` | Print a handful of model predictions vs references |
| `eval.py` | ROUGE + BERTScore on Nordjylland news |
| `docs/` | Setup, pipeline, datasets, training, evaluation, gotchas |
| `examples/` | Sample CSVs, schema checks, chunking demo, toy labeling run |

## Quick start (full GPU pipeline)

You need a CUDA GPU, several GB of disk for models, and the original Danish article dump (`10000_articles_without_linebreaks.csv`). The course run used that filename as the `translate.py` input.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt')"
```

### Step 1 — Convert both translation directions

`Ctranslate_converter.py` as committed only converts **English → Danish**. `translate.py` needs the other direction. Convert both before you start:

```bash
python Ctranslate_converter.py
# also convert Helsinki-NLP/opus-mt-da-en → models/opus-mt-da-en_ct2
```

See [docs/models.md](docs/models.md) for the exact converter snippet.

### Step 2 — Translate the Danish news dump into English

```bash
python translate.py
```

Reads `10000_articles_without_linebreaks.csv` (`id`, `article text`) and writes `translated_articles.csv` (`id`, `body`, `translated`).

### Step 3 — Summarize the English side

```bash
python summary.py
```

**Course-script caveat:** `summary.py` currently slices `df[:10]`. Remove that slice before a full run. Details in [docs/pipeline.md](docs/pipeline.md).

### Step 4 — Translate summaries back to Danish

```bash
python translate_back.py
```

Writes `labeled_dataset_ml80_rp5.0.csv` with columns `id`, `body`, `summary`.

### Step 5 — Split and fine-tune

Put train/validation/test CSVs in `datasets/` with columns `id`, `body`, `summary`, then:

```bash
python finetune.py
```

The trainer writes checkpoints under `mt5-summarize-large/` and a final copy under `./large_model`.

### Step 6 — Inspect and evaluate

```bash
python use_model.py
python eval.py
```

These two scripts load a local folder named `small_model` and evaluate on Nordjylland news. They do **not** automatically pick up `./large_model`. See [docs/evaluation.md](docs/evaluation.md).

## Quick start (examples only, no GPU)

The `examples/` tree is meant to be runnable on a laptop. It does **not** download OPUS-MT, T5, or mT5.

```bash
pip install -r requirements-examples.txt
python -c "import nltk; nltk.download('punkt')"
python examples/validate_example_data.py
python examples/sentence_chunking_demo.py
python examples/toy_labeling_pipeline.py
python examples/length_stats.py
```

That path exercises the same CSV schemas and the same sentence-chunking rules the GPU scripts use.

## Documentation map

- [Overview](docs/overview.md) — problem statement and design choices
- [Setup](docs/setup.md) — Python, CUDA, NLTK, disk, tokens
- [Pipeline](docs/pipeline.md) — every script, every filename, every column
- [Datasets](docs/datasets.md) — course dump vs Nordjylland vs example CSVs
- [Models](docs/models.md) — OPUS-MT, English T5, mT5
- [Training](docs/training.md) — hyperparameters copied from `finetune.py`
- [Evaluation](docs/evaluation.md) — ROUGE, BERTScore, how to read them
- [Limitations](docs/limitations.md) — translationese, error compounding, slice bugs
- [Troubleshooting](docs/troubleshooting.md) — the failures this repo actually hits
- [File map](docs/file-map.md) — one page per script
- [Reproducing the course run](docs/reproducing-course-run.md)

## License

MIT. See [LICENSE](LICENSE). The original course commit is from 2023.
