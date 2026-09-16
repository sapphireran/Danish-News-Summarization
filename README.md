# Danish News Summarization

Personal ITU course project from **Advanced Natural Language Processing and Deep Learning (2023)**.

The goal is a Danish abstractive news summarizer trained on **automatically generated** labels. Danish gold summaries were scarce for this project, so the pipeline pivots through English:

1. Translate Danish articles to English (`Helsinki-NLP/opus-mt-da-en` via CTranslate2).
2. Summarize the English text with a news-tuned T5 (`mrm8488/t5-base-finetuned-summarize-news`).
3. Translate those English summaries back to Danish (`Helsinki-NLP/opus-mt-en-da`).
4. Fine-tune multilingual T5 (`google/mt5-large` in `finetune.py`) on the resulting Danish `(article, summary)` pairs.
5. Inspect generations (`use_model.py`) and score a held-out Danish news set (`eval.py`) with ROUGE and BERTScore.

This is **not** a production system. The labels inherit translation error, English-centric summarizer bias, and the usual seq2seq failure modes. See [docs/08-limitations-and-ethics.md](docs/08-limitations-and-ethics.md).

## Repository layout

| Path | Role |
| --- | --- |
| [`Ctranslate_converter.py`](Ctranslate_converter.py) | Convert Helsinki OPUS-MT checkpoints to CTranslate2 |
| [`translate.py`](translate.py) | Danish → English article translation |
| [`summary.py`](summary.py) | English news summarization with sentence-aware chunking |
| [`translate_back.py`](translate_back.py) | English → Danish summary translation |
| [`finetune.py`](finetune.py) | Fine-tune mT5 on the labeled Danish CSV splits |
| [`use_model.py`](use_model.py) | Print a few model generations vs. references |
| [`eval.py`](eval.py) | ROUGE + BERTScore on Nordjylland news summarization |
| [`docs/`](docs/README.md) | Pipeline, dataset, training, and eval notes |
| [`examples/`](examples/README.md) | Sample CSVs, configs, and CPU-only helper scripts |

## Quick start (CPU examples)

The GPU scripts in the repo root expect large local weights and the original 10k-article CSV. The `examples/` helpers do **not**. They walk the same data shapes and chunking rules on a tiny original sample set.

```bash
python -m pip install -r requirements.txt
python examples/run_all.py
```

## Full GPU workflow

Paths and hyperparameters are hardcoded in the original scripts. Treat the commands below as the 2023 course run, not a packaged CLI.

### 1. Convert translation models

`Ctranslate_converter.py` currently converts **only** `Helsinki-NLP/opus-mt-en-da`. The Danish → English conversion is commented out. Uncomment the `opus-mt-da-en` block (or run a second converter) so both of these directories exist before translating:

- `models/opus-mt-da-en_ct2`
- `models/opus-mt-en-da_ct2`

```bash
python Ctranslate_converter.py
```

### 2. Translate the Danish corpus to English

Expects `10000_articles_without_linebreaks.csv` with columns `id` and `article text`. Writes `translated_articles.csv`.

```bash
python translate.py
```

### 3. Summarize the English text

`summary.py` currently slices `df[:10]` — a leftover debug cap. Remove that slice to process the full file. Writes `summarized_file_ml80_rp5.0.csv` (`max_length=80`, `repetition_penalty=5.0`).

```bash
python summary.py
```

### 4. Translate summaries back to Danish

Writes `labeled_dataset_ml80_rp5.0.csv` with columns `id`, `body`, `summary`.

```bash
python translate_back.py
```

### 5. Fine-tune mT5

`finetune.py` loads:

- `datasets/train_dataset.csv`
- `datasets/validation_dataset.csv`
- `datasets/test_dataset.csv`

Split the labeled file yourself (see [docs/02-datasets.md](docs/02-datasets.md)). The trainer writes checkpoints under `mt5-summarize-large/` and a final copy under `./large_model`.

```bash
python finetune.py
```

### 6. Inspect and evaluate

`use_model.py` loads `small_model` and the ScandEval mini split. `eval.py` loads `small_model` and the full `alexandrainst/nordjylland-news-summarization` test split.

```bash
python use_model.py
python eval.py
```

## Documentation

- [Documentation index](docs/README.md)
- [End-to-end pipeline](docs/01-pipeline.md)
- [Dataset schemas and splits](docs/02-datasets.md)
- [Translation stage](docs/03-translation.md)
- [English summarization stage](docs/04-summarization.md)
- [Fine-tuning](docs/05-training.md)
- [Evaluation](docs/06-evaluation.md)
- [Hyperparameter reference](docs/07-hyperparameters.md)
- [Limitations and ethics](docs/08-limitations-and-ethics.md)
- [Reproduction notes](docs/09-reproduction.md)

## Examples

See [examples/README.md](examples/README.md) for sample rows, YAML configs that mirror the hardcoded script settings, and utilities that validate those samples.

## License

MIT. See [LICENSE](LICENSE).
