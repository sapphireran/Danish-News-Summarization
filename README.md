# Danish-News-Summarization

ITU Advanced Natural Language Processing and Deep Learning (2023) final
project: a Danish summarization model trained on **automatically generated
labels**.

Danish news bodies are translated to English, summarized with an English
news T5, and translated back. Those silver pairs fine-tune mT5. The
detour is documented — including the ways it fails — in [`docs/`](docs/).

This README is the map. The 2023 GPU scripts still live in the
repository root and still do the training. [`examples/`](examples/) is a
CPU-only twin that you can run without downloading a model.

## Two ways in

| You have | Start with |
| --- | --- |
| An afternoon, no GPU | [`docs/examples.md`](docs/examples.md) and the commands below |
| A GPU and the original news dump | [Workflow (GPU)](#workflow-gpu) and [`docs/pipeline.md`](docs/pipeline.md) |
| A checkpoint and a metrics question | [`docs/evaluation.md`](docs/evaluation.md) |
| A crash in a root script | [`docs/troubleshooting.md`](docs/troubleshooting.md) |

## CPU examples (no models)

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
PYTHONPATH=. python examples/walk_one_article.py dn-009
PYTHONPATH=. python examples/compare_chunk_strategies.py
PYTHONPATH=. python examples/dry_run_pipeline.py
PYTHONPATH=. python -m danish_news_summarization.cli stages
```

Ten fictional regional-news stories ship in `examples/data/`. They exist
so chunking, CSV schemas, and compression ratios are inspectable. They
are not a benchmark. See [`docs/dataset.md`](docs/dataset.md).

## Workflow (GPU)

### Step 1: Model conversion

Convert Helsinki-NLP OPUS-MT to CTranslate2. The checked-in file
enables **en→da only** — uncomment da→en before the next step.

```bash
python Ctranslate_converter.py
```

### Step 2: Translate the Danish dump to English

```bash
python translate.py
```

Reads `10000_articles_without_linebreaks.csv` (`id`, `article text`).
Writes `translated_articles.csv` (`id`, `body`, `translated`).

### Step 3: Summarize the English side

```bash
python summary.py
```

Uses `mrm8488/t5-base-finetuned-summarize-news` with `max_length=80`
and `repetition_penalty=5.0`. The script slices to the first **10**
rows; remove `[:10]` for a full run.

### Step 4: Translate summaries back to Danish

```bash
python translate_back.py
```

Writes `labeled_dataset_ml80_rp5.0.csv` (`id`, `body`, `summary`).
Split that into `datasets/train|validation|test_dataset.csv`.

### Fine-tune mT5

```bash
python finetune.py
```

`google/mt5-large`, 20 epochs, Adafactor, `3e-4`, best checkpoint by
ROUGE-1 mid F. Details: [`docs/training.md`](docs/training.md).

### Inspect and evaluate

```bash
python use_model.py
python eval.py
```

These two score **Nordjylland** Hub datasets, not the silver labels.
`use_model.py` is qualitative; `eval.py` adds BERTScore (`lang='da'`).

## Package

`danish_news_summarization/` is a small stdlib package extracted from
the 2023 scripts:

- sentence packing (`chunking.py`) that mirrors `translate.py` / `summary.py`
- CSV contracts (`schema.py`) for every stage
- named stage configs (`config.py`) with the original filenames
- a dry-run pipeline (`pipeline.py`) used by the examples

The root GPU scripts do not import it yet. That is intentional; see
[`docs/design-notes.md`](docs/design-notes.md).

## Docs index

- [Pipeline](docs/pipeline.md)
- [Dataset](docs/dataset.md)
- [Models](docs/models.md)
- [Training](docs/training.md)
- [Evaluation](docs/evaluation.md)
- [Examples](docs/examples.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Original scripts](docs/original-scripts.md)
- [Design notes](docs/design-notes.md)

## License

MIT. See [`LICENSE`](LICENSE).
