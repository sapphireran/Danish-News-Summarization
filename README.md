# Danish-News-Summarization

ITU Advanced Natural Language Processing and Deep Learning (2023) final
project: a Danish news summarizer trained on **automatically generated**
labels.

Unlabeled Danish articles are translated to English, summarized with an
English news T5, and translated back to Danish. Those silver pairs
fine-tune multilingual T5. Public Nordjylland-News data is used only
for inspection and scoring.

This README is the short command list. The method, schemas, and the
gaps in the 2023 scripts are written out under [`docs/`](docs/README.md).
A fictional 10-article walkthrough that needs no GPU lives in
[`examples/`](examples/README.md).

```
Danish article  →  OPUS-MT da→en  →  English T5 summary  →  OPUS-MT en→da
                                                              │
                                                              ▼
                                                         dataset/*.csv
                                                              │
                                                              ▼
                                                           mT5 fine-tune
                                                              │
                                              ┌───────────────┴──────────┐
                                              ▼                          ▼
                                        use_model.py                  eval.py
                                        (qualitative)           (ROUGE + BERTScore)
```

## Workflow

### Step 1: Model conversion

Convert the Helsinki-NLP OPUS-MT checkpoints with CTranslate2. The
checked-in converter only emits `opus-mt-en-da`; uncomment the da→en
block before the next step. Details: [docs/models.md](docs/models.md).

```
python Ctranslate_converter.py
```

### Step 2: Translate the dataset

`translate.py` reads `10000_articles_without_linebreaks.csv`
(`id`, `article text`) and writes `translated_articles.csv`.

```
python translate.py
```

### Step 3: Extract the English summary

`summary.py` currently scores the **first 10 rows** only. Remove the
`[:10]` slice for a full run.

```
python summary.py
```

### Step 4: Translate summaries back to Danish

Writes `labeled_dataset_ml80_rp5.0.csv` with `id`, `body`, `summary`.
Split that file yourself into `datasets/train_dataset.csv`,
`datasets/validation_dataset.csv`, and `datasets/test_dataset.csv`.

```
python translate_back.py
```

### Fine-tune

`finetune.py` trains `google/mt5-large` and writes `./large_model`.
`eval.py` / `use_model.py` load `small_model`. Point those scripts at
the directory you actually trained, or fine-tune `mt5-small` as well.
Hyperparameters: [docs/training.md](docs/training.md).

```
python finetune.py
```

### Inspect and evaluate

`use_model.py` prints generations on the ScandEval Nordjylland-News
mini set. `eval.py` scores ROUGE and Danish BERTScore on the Alexandra
Institute test split. Column-name caveats:
[docs/datasets.md](docs/datasets.md).

```
python use_model.py
python eval.py
```

## Documentation and examples

| Path | Contents |
| --- | --- |
| [docs/pipeline.md](docs/pipeline.md) | Stage-by-stage data flow |
| [docs/design_notes.md](docs/design_notes.md) | Why the pipeline pivots through English |
| [docs/limitations.md](docs/limitations.md) | Known gaps in the 2023 scripts |
| [docs/reproduction.md](docs/reproduction.md) | Install and rerun checklist |
| [examples/README.md](examples/README.md) | Download-free demos |

```
python examples/run_all_demos.py
```

## Setup

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The example scripts do not use that extra stack. Generated weights,
CTranslate2 directories, and unlabeled news dumps are gitignored.

## License

MIT. See [LICENSE](LICENSE).
