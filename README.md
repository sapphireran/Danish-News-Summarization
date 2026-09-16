# Danish-News-Summarization

Personal 2023 final project for **ITU Advanced Natural Language Processing and
Deep Learning**: a Danish news summarizer trained on silver labels.

Danish articles are translated to English, summarized with an English news T5,
then translated back. Multilingual mT5 is fine-tuned on the resulting Danish
`(article, summary)` pairs so inference does not need a translation step.

This repository keeps the original course scripts and adds a personal archive
of notes plus **model-free examples** that show the CSV contracts and the
sentence-packing logic.

```text
Danish news  →  OPUS-MT da→en  →  English T5 summary  →  OPUS-MT en→da
                                                              │
                                                              ▼
                                            mT5 fine-tune on Danish pairs
```

## Original course workflow

### 1. Model conversion

Convert Helsinki-NLP OPUS-MT checkpoints with CTranslate2. As committed, only
the English→Danish model is active; uncomment the Danish→English block before
the next step. Details: [docs/models.md](docs/models.md).

```bash
python Ctranslate_converter.py
```

### 2. Translate the Danish news dump to English

```bash
python translate.py
```

Reads `10000_articles_without_linebreaks.csv` (`id`, `article text`) and
writes `translated_articles.csv` (`id`, `body`, `translated`).

### 3. Summarize the English articles

```bash
python summary.py
```

Uses `mrm8488/t5-base-finetuned-summarize-news`. The committed script only
processes the first 10 rows. Remove `[:10]` for a full run.

### 4. Translate summaries back to Danish

```bash
python translate_back.py
```

Writes `labeled_dataset_ml80_rp5.0.csv` (`id`, `body`, `summary`).

### 5. Fine-tune mT5

Split the labeled file into `datasets/train_dataset.csv`,
`datasets/validation_dataset.csv`, and `datasets/test_dataset.csv` (see
`examples/split_labeled_dataset.py`), then:

```bash
python finetune.py
```

### 6. Inspect and evaluate

```bash
python use_model.py
python eval.py
```

`use_model.py` prints generations. `eval.py` reports ROUGE and Danish
BERTScore on Nordjylland News.

## Personal docs

| Document | Topic |
| --- | --- |
| [docs/pipeline.md](docs/pipeline.md) | End-to-end flow |
| [docs/datasets.md](docs/datasets.md) | CSV column contracts |
| [docs/models.md](docs/models.md) | OPUS-MT, T5, mT5 |
| [docs/training-and-eval.md](docs/training-and-eval.md) | Trainer knobs and metrics |
| [docs/design-notes.md](docs/design-notes.md) | Rationale and known issues |
| [docs/reproduction.md](docs/reproduction.md) | Local runbook |
| [docs/script-map.md](docs/script-map.md) | File-by-file map |
| [docs/worked-example.md](docs/worked-example.md) | Article `dn-001` through every CSV |

## Model-free examples

No GPU and no Hugging Face weights. These exercise the same file formats the
course scripts use, with original sample articles:

```bash
python3 examples/validate_csvs.py --sample-dir examples/sample_data
python3 examples/inspect_dataset.py --path examples/sample_data/03_labeled_sample.csv
python3 examples/demo_chunking.py
python3 examples/toy_pipeline.py --sample-dir examples/sample_data --output-dir /tmp/dns-toy
python3 -m unittest discover -s tests -v
```

More detail: [examples/README.md](examples/README.md).

## Requirements

GPU scripts: [requirements.txt](requirements.txt).
Example scripts and unit tests: Python 3.10+ standard library only.

## License

MIT. See [LICENSE](LICENSE).
