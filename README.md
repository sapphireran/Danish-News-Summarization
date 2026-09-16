# Danish News Summarization

Personal ITU course project (Advanced Natural Language Processing and Deep Learning, 2023).

The goal is a **Danish abstractive news summarizer** trained on *automatically generated* labels. Danish news articles are pivoted through English: translate to English, summarize with an English news T5, then translate the summary back to Danish. Those silver labels fine-tune multilingual T5 (`google/mt5-large` in the training script). Held-out evaluation uses human-written Nordjylland news summaries.

This repository is personal academic work. It is not company code.

## Why a translation pivot?

In 2023 there were far more mature English news summarizers than Danish ones. The project treats English as a high-resource pivot:

1. Danish article → English article (`Helsinki-NLP/opus-mt-da-en`, CTranslate2)
2. English article → English summary (`mrm8488/t5-base-finetuned-summarize-news`)
3. English summary → Danish summary (`Helsinki-NLP/opus-mt-en-da`, CTranslate2)
4. Fine-tune `mT5` on `(Danish article, silver Danish summary)` pairs
5. Evaluate on `alexandrainst/nordjylland-news-summarization` with ROUGE and BERTScore

The silver labels are noisy. Translation error, English-centric compression, and back-translation artifacts all land in the training targets. The evaluation set is the honest signal.

Longer write-ups live under [`docs/`](docs/README.md). Runnable, dependency-light demos live under [`examples/`](examples/README.md).

## Repository layout

| Path | Role |
| --- | --- |
| `Ctranslate_converter.py` | Convert a Transformers OPUS-MT checkpoint to CTranslate2 |
| `translate.py` | Danish articles → English (`translated_articles.csv`) |
| `summary.py` | English articles → English summaries |
| `translate_back.py` | English summaries → Danish summaries |
| `finetune.py` | Fine-tune `google/mt5-large` on the silver CSV splits |
| `use_model.py` | Print a handful of generations from a local `small_model` |
| `eval.py` | ROUGE + BERTScore on the Nordjylland test split |
| `docs/` | Pipeline, datasets, models, evaluation, reproduction notes |
| `examples/` | Sample corpus, schema checks, chunking demo, toy metrics |

## Workflow

GPU is assumed for conversion, translation, summarization, and fine-tuning. The `examples/` scripts do **not** download models and run on CPU with the standard library.

### Step 1: Model conversion

`Ctranslate_converter.py` converts `Helsinki-NLP/opus-mt-en-da` to `models/opus-mt-en-da_ct2`. The Danish→English converter is present but commented out; uncomment it before `translate.py`, which loads `models/opus-mt-da-en_ct2`.

```bash
python Ctranslate_converter.py
```

### Step 2: Translate the Danish news set to English

Expects `10000_articles_without_linebreaks.csv` with columns `id` and `article text`.

```bash
python translate.py
```

Writes `translated_articles.csv` (`id`, `body`, `translated`).

### Step 3: Summarize the English side

```bash
python summary.py
```

Writes `summarized_file_ml80_rp5.0.csv`. The checked-in script slices `[:10]`, so it is a smoke path unless you remove that limit.

### Step 4: Translate summaries back to Danish

```bash
python translate_back.py
```

Writes `labeled_dataset_ml80_rp5.0.csv` (`id`, `body`, `summary`).

### Step 5: Fine-tune mT5

Place CSV splits at `datasets/train_dataset.csv`, `datasets/validation_dataset.csv`, and `datasets/test_dataset.csv` with columns `id`, `body`, `summary`. Then:

```bash
python finetune.py
```

Saves the adapter/checkpoint under `./large_model`.

### Step 6: Inspect and evaluate

```bash
python use_model.py
python eval.py
```

These two scripts load `small_model` and `google/mt5-small`, not the `large_model` directory from `finetune.py`. See [docs/known-issues.md](docs/known-issues.md).

## Examples without a GPU

```bash
python examples/export_sample_csvs.py
python examples/toy_pipeline.py
python examples/metrics_demo.py
python examples/inspect_samples.py
python -m unittest discover -s examples/tests -v
```

The sample articles are original fiction written for this repo. They are not scraped news and are safe to keep in git.

## Documentation map

- [Project overview and decisions](docs/README.md)
- [Labeling pipeline](docs/pipeline.md)
- [Dataset schemas and splits](docs/datasets.md)
- [Models and hyperparameters](docs/models.md)
- [Evaluation protocol](docs/evaluation.md)
- [Reproduction notes](docs/reproduction.md)
- [Known issues](docs/known-issues.md)
- [Script I/O reference](docs/script-reference.md)
- [Examples guide](examples/README.md)

## License

MIT. See [LICENSE](LICENSE).
