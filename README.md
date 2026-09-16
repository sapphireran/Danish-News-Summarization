# Danish-News-Summarization

ITU Advanced Natural Language Processing and Deep Learning (2023) final
project: a Danish summarizer trained on **silver labels** produced by

```text
Danish news → OPUS-MT da→en → English news T5 → OPUS-MT en→da → mT5
```

The December 2023 GPU scripts at the repo root are unchanged. They still
hard-code filenames, still slice `summary.py` to ten rows, and still
need Hub weights.

This branch adds a personal, download-free lab — **maalestok** — that
tracks what those hops do to *measures* (decimal commas, `kr.`, clocks,
signed °C, feast days) on sixteen fictional briefs from **Blåhøj Sogn**.

## Read this first if you do not have a GPU

```bash
python3 -m maalestok list
python3 -m maalestok show bh-02
python3 -m maalestok ledger
python3 examples/run_almanac.py
python3 -m unittest discover -s tests -v
```

Open `examples/report/index.html` for the almanac. Notes live in
[`docs/`](docs/README.md).

## 2023 GPU workflow (as committed)

### 1. Model conversion

```bash
python Ctranslate_converter.py
```

Writes `models/opus-mt-en-da_ct2` only. The da→en convert is commented out.

### 2. Translate the Danish dump

```bash
python translate.py
```

Reads `10000_articles_without_linebreaks.csv`. Writes `translated_articles.csv`.

### 3. English summaries

```bash
python summary.py
```

Still does `[:10]`. Writes `summarized_file_ml80_rp5.0.csv`.

### 4. Translate summaries back

```bash
python translate_back.py
```

Writes `labeled_dataset_ml80_rp5.0.csv`.

### 5. Fine-tune

```bash
python finetune.py
```

Expects `datasets/{train,validation,test}_dataset.csv`. Saves `./large_model`.

### 6. Inspect / evaluate

```bash
python use_model.py
python eval.py
```

Both load `small_model`. `eval.py` talks to Nordjylland-News columns
(`input_text`, `target_text`), not the silver `body` / `summary` pair.

## What maalestok is

A closed parish yearbook plus a measure extractor. It names
`comma_shift`, `sign_drop`, `clock_12h`, `currency_swap`, and the rest,
and it keeps an oracle back-translation so silver is not the only Danish
line in the tree. No company code. No social tooling. No invented 2023
ROUGE table.
