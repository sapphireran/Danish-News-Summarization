# Danish-News-Summarization

ITU Advanced Natural Language Processing and Deep Learning (2023)
final project: a Danish summarisation model trained on **silver
labels**. Raw Danish news is translated to English, summarised with an
English news T5, and translated back to Danish. mT5 is then fine-tuned
on `(Danish body, Danish silver summary)`.

This is a personal course archive. The 2023 scripts are unchanged.
The `fjordpress` study kit is an offline reconstruction of the same
four hops on an invented municipal gazette, so the method can be
inspected without downloading OPUS-MT or mT5.

## 2023 workflow (needs GPU + weights)

### Step 1: Model conversion

`Ctranslate_converter.py` as committed exports **en→da only**. Hop 1
still expects `models/opus-mt-da-en_ct2`. See
[docs/script-archaeology.md](docs/script-archaeology.md).

```
python Ctranslate_converter.py
```

### Step 2: Translate dataset

```
python translate.py
```

Reads `10000_articles_without_linebreaks.csv` (`id`, `article text`).
Writes `translated_articles.csv` (`id`, `body`, `translated`).

### Step 3: Extract summary

```
python summary.py
```

Uses `mrm8488/t5-base-finetuned-summarize-news`. The committed script
summarises **the first ten rows** (`df[:10]`). Output:
`summarized_file_ml80_rp5.0.csv`.

### Step 4: Translate back to Danish

```
python translate_back.py
```

Writes `labeled_dataset_ml80_rp5.0.csv` (`id`, `body`, `summary`).

### Fine-tuning

```
python finetune.py
```

`google/mt5-large` on `datasets/{train,validation,test}_dataset.csv`.
Saves `./large_model`.

### Model evaluation

```
python use_model.py
python eval.py
```

These load **`small_model`** and public Hugging Face test sets, not
the local CSVs. Column names differ (`input_text` / `target_text`).

## Study kit (no downloads)

```bash
python -m fjordpress corpus
python -m fjordpress pack --budget 40 -v
python -m fjordpress hops
python -m fjordpress ledger --article vk-001
python -m fjordpress lexicon
python -m fjordpress schemas
python -m fjordpress fixtures
python -m fjordpress report --snapshot
python -m pytest tests
```

Ten invented Vesterklit stories, a closed-world DA↔EN word list, an
extractive stand-in for the per-window T5, and a hop ledger that
tracks planted names and numbers. Notes:

* [docs/README.md](docs/README.md) — index of the reconstruction
* [examples/README.md](examples/README.md) — scripts and sample CSVs

`requirements-examples.txt` is pytest only. The 2023 stack is listed
in `requirements.txt` and is **not** installed by the study kit.

## Layout

```
Ctranslate_converter.py   # 2023: OPUS → CTranslate2
translate.py              # 2023: DA → EN
summary.py                # 2023: EN → EN summary
translate_back.py         # 2023: EN summary → DA
finetune.py               # 2023: mT5-large
use_model.py / eval.py    # 2023: qualitative + ROUGE/BERTScore
fjordpress/               # 2026 study kit (stdlib only)
docs/                     # personal reconstruction notes
examples/                 # laptop demos + 2023-shaped CSVs
tests/                    # kit tests, no GPU
```
