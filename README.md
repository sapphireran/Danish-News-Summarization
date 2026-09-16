# Danish-News-Summarization

ITU *Advanced Natural Language Processing and Deep Learning* (2023) final
project: a Danish summarization model trained on **silver labels** that
were produced by translating Danish news to English, summarizing with an
English T5, and translating the summaries back.

This repository still contains the seven course scripts from December
2023. They are unchanged. What is new on this branch is a personal
coursebook and a download-free workbook that measures **entity
attrition** across those hops, using original fiction about a made-up
island chain.

## 2023 GPU workflow

These commands need the private 10k dump, CTranslate2 model directories,
and a GPU. They are the historical pipeline, not the default laptop path.

### Step 1: Model conversion

```
python Ctranslate_converter.py
```

As committed, this writes `models/opus-mt-en-da_ct2` only. The da→en
conversion is commented out; see [docs/04-script-archaeology.md](docs/04-script-archaeology.md).

### Step 2: Translate dataset

```
python translate.py
```

Reads `10000_articles_without_linebreaks.csv` (`id`, `article text`).

### Step 3: Extract summary

```
python summary.py
```

The committed file slices `[:10]` rows before summarizing.

### Step 4: Translate back to Danish

```
python translate_back.py
```

### Fine-tuning

```
python finetune.py
```

Saves `./large_model`.

### Evaluation

```
python use_model.py
python eval.py
```

Both load `./small_model` and a Nordjylland-News split from the Hub.

## Laptop path (no weights)

CPython 3.11+, standard library only:

```bash
python3 -m kystlinje validate
python3 -m kystlinje ledger
python3 -m kystlinje quiz --answers
python3 -m kystlinje report
python3 examples/run_workbook.py
python3 -m unittest discover -s tests -t . -v
```

That path never calls HuggingFace, never downloads OPUS-MT/T5/mT5, and
never touches the uncommitted news dump. Open
[`examples/report/index.html`](examples/report/index.html) for the entity
telescope.

## Documentation

- [Coursebook index](docs/README.md)
- [Silver labels as a method](docs/01-silver-labels.md)
- [Entity attrition](docs/02-entity-attrition.md)
- [Examples](examples/README.md)

## What this is not

- Not employer code, not an internal eval harness.
- Not a republication of the 10k Danish news dump.
- Not a reconstructed 2023 ROUGE table. Those numbers were never in git.
