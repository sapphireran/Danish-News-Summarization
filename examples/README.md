# Examples

These scripts do not download models and do not need a GPU. They exist so the
CSV contracts and the sentence-packing logic can be inspected on a laptop.

All commands below assume the repository root is the working directory.

## Sample data

`sample_data/` holds twelve original fictional municipal-news articles in every
pipeline format. They are **not** from the 2023 news dump.

| File | Stage |
| --- | --- |
| `00_articles_sample.csv` | raw Danish (`id`, `article text`) |
| `01_translated_sample.csv` | English articles |
| `02_summarized_sample.csv` | English summaries |
| `03_labeled_sample.csv` | Danish silver labels |
| `04_train_split_sample.csv` | 8-row train split |
| `04_validation_split_sample.csv` | 2-row validation split |
| `04_test_split_sample.csv` | 2-row test split |

Regenerate the CSVs from `sample_articles.py`:

```bash
python3 examples/build_sample_data.py
```

The builder is deterministic (seed `2023` for the 8/2/2 split). A unit test
rebuilds into a temp directory and diffs against the committed files.

## Commands

Validate every sample CSV, including cross-stage id/body alignment and
train/val/test leakage:

```bash
python3 examples/validate_csvs.py --sample-dir examples/sample_data
```

Check one file:

```bash
python3 examples/validate_csvs.py \
  --path examples/sample_data/03_labeled_sample.csv \
  --stage labeled
```

Length stats and a 128-word hint for the mT5 label cap:

```bash
python3 examples/inspect_dataset.py \
  --path examples/sample_data/03_labeled_sample.csv
```

See encoder windows for one article (shrink the budget to force multiple
windows):

```bash
python3 examples/demo_chunking.py --id dn-001 --text-max-length 180
python3 examples/demo_chunking.py --all --text-max-length 220
```

Run the four-file format demo with mocks (no gold English/Danish):

```bash
python3 examples/toy_pipeline.py \
  --sample-dir examples/sample_data \
  --output-dir /tmp/dns-toy
```

Replay the gold fields from `sample_articles.py` instead of mocks:

```bash
python3 examples/toy_pipeline.py \
  --sample-dir examples/sample_data \
  --output-dir /tmp/dns-gold \
  --replay-gold
```

Split a labeled CSV the way `finetune.py` wants:

```bash
python3 examples/split_labeled_dataset.py \
  --input examples/sample_data/03_labeled_sample.csv \
  --output-dir /tmp/dns-splits \
  --train-ratio 0.8 \
  --val-ratio 0.1 \
  --seed 2023
```

## Modules

| File | Role |
| --- | --- |
| `sample_articles.py` | Twelve bilingual articles + short summaries |
| `chunking.py` | Sentence split, long-sentence cut, window packing |
| `schema.py` | Required columns per stage |
| `csv_util.py` | UTF-8 DictReader / DictWriter |
| `validate_csvs.py` | Contract + alignment checks |
| `inspect_dataset.py` | Row/length report |
| `split_labeled_dataset.py` | Seeded train/val/test split |
| `toy_pipeline.py` | Format walk without models |
| `demo_chunking.py` | Print packed windows |
| `build_sample_data.py` | Rewrite `sample_data/` |

`chunking.py` documents a quirk from the course scripts: token length decides
whether a sentence is “too long”, but the inner splitter counts characters.
The example copy keeps that mix so a personal rerun is not surprised by it.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

The tests import the example modules by putting `examples/` on `sys.path`.
They cover packing, schema inference, sample-data validation, split
leakage, toy-pipeline output, and a rebuild round-trip.
