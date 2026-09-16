# Danish News Summarization

Personal course project from the 2023 ITU course **Advanced Natural Language Processing and Deep Learning**. The goal was to train a Danish abstractive news summarizer when human-written Danish summaries were scarce.

The approach is a **silver-label pipeline**:

1. Translate Danish news articles into English.
2. Summarize the English text with an off-the-shelf English news summarizer.
3. Translate the English summaries back into Danish.
4. Fine-tune a multilingual seq2seq model (`google/mt5-large` in the original run) on the resulting Danish article–summary pairs.
5. Evaluate against a held-out Danish news summarization benchmark using ROUGE and BERTScore.

This repository keeps the original 2023 training scripts at the repo root and adds a documentation set plus runnable, GPU-free examples under `docs/` and `examples/`.

## Why this design

Danish summarization data in 2023 was thin compared with English. Instead of discarding English-only summarizers, the project treated translation as a **label-generation tool**. That is cheaper than hiring annotators, but it also injects translationese, entity drift, and English-centric summary style into the training signal. The docs in this repo spell out those trade-offs so the pipeline is easy to revisit later.

See [docs/00-overview.md](docs/00-overview.md) for the project map and [docs/06-limitations-and-ethics.md](docs/06-limitations-and-ethics.md) for the caveats.

## Repository layout

| Path | Role |
| --- | --- |
| `Ctranslate_converter.py` | Convert Helsinki-NLP OPUS-MT checkpoints to CTranslate2 |
| `translate.py` | Danish → English article translation |
| `summary.py` | English abstractive summarization |
| `translate_back.py` | English → Danish summary translation |
| `finetune.py` | Fine-tune mT5 on silver Danish pairs |
| `use_model.py` | Print a handful of qualitative generations |
| `eval.py` | ROUGE + BERTScore on a Danish test set |
| `docs/` | Methodology, schemas, evaluation, reproduction |
| `examples/` | Synthetic sample data and GPU-free demos |
| `tests/` | Checks for the example utilities and sample CSVs |

Original training scripts are left as they were submitted in 2023. Documentation describes them, including historical quirks, rather than silently rewriting the course code.

## Original GPU pipeline

The commands below match the 2023 workflow. They expect CUDA, converted CTranslate2 models, and a local CSV of Danish articles.

### Step 1 — Convert translation models

```bash
python Ctranslate_converter.py
```

The checked-in converter exports `Helsinki-NLP/opus-mt-en-da`. The Danish→English direction used by `translate.py` is the same converter pointed at `Helsinki-NLP/opus-mt-da-en` (commented in the script). Outputs land under `models/`.

### Step 2 — Translate the Danish corpus to English

```bash
python translate.py
```

Reads `10000_articles_without_linebreaks.csv` and writes `translated_articles.csv`. Long articles are split into sentence packs that fit the 512-token OPUS-MT window. Details: [docs/01-pipeline.md](docs/01-pipeline.md) and [docs/02-chunking-and-length.md](docs/02-chunking-and-length.md).

### Step 3 — Summarize the English text

```bash
python summary.py
```

Uses `mrm8488/t5-base-finetuned-summarize-news`. The script as committed processes the first 10 rows (`df[:10]`) and writes `summarized_file_ml80_rp5.0.csv` (max summary length 80, repetition penalty 5.0).

### Step 4 — Translate summaries back to Danish

```bash
python translate_back.py
```

Produces `labeled_dataset_ml80_rp5.0.csv` with columns `id`, `body`, `summary`.

### Fine-tune mT5

```bash
python finetune.py
```

Expects `datasets/train_dataset.csv`, `datasets/validation_dataset.csv`, and `datasets/test_dataset.csv`. Checkpoints go to `mt5-summarize-large/`; the best model is copied to `./large_model`.

### Inspect and evaluate

```bash
python use_model.py
python eval.py
```

`use_model.py` loads `small_model` and prints generations on `ScandEval/nordjylland-news-summarization-mini`. `eval.py` scores `small_model` on `alexandrainst/nordjylland-news-summarization` with ROUGE and Danish BERTScore (`xlm-roberta-large`).

## GPU-free examples (this PR)

You can exercise the *ideas* in the pipeline without downloading models:

```bash
python -m pip install -r requirements-examples.txt
python examples/run_chunking_demo.py
python examples/inspect_sample_dataset.py
python examples/metrics_toy_eval.py
python -m pytest tests/
```

Start at [examples/README.md](examples/README.md). Sample rows are **synthetic original Danish**, not scraped news.

## Documentation index

1. [Overview and design rationale](docs/00-overview.md)
2. [Silver-label pipeline](docs/01-pipeline.md)
3. [Chunking and length budgets](docs/02-chunking-and-length.md)
4. [Models and hyperparameters](docs/03-models-and-hyperparameters.md)
5. [Dataset schema and file names](docs/04-dataset-schema.md)
6. [Evaluation protocol](docs/05-evaluation.md)
7. [Limitations, leakage, and ethics](docs/06-limitations-and-ethics.md)
8. [Reproduction notes](docs/07-reproduction.md)
9. [Troubleshooting](docs/08-troubleshooting.md)
10. [Glossary](docs/09-glossary.md)

## Requirements

- Python 3.9+ recommended
- Full training stack: `requirements.txt` plus a matching CUDA `torch` wheel
- Docs/examples only: `requirements-examples.txt`

NLTK's `punkt` (and on newer NLTK releases, `punkt_tab`) is required for sentence splitting.

## License

MIT. See [LICENSE](LICENSE). The original course scripts and this documentation are personal academic work, not affiliated with any employer.
