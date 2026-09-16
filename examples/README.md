# Examples

CPU-only stand-ins for the 2023 pipeline. These files exist so the CSV
contracts, sentence packer, and split logic can be checked without
downloading OPUS-MT, T5, or mT5.

The fixtures are original fiction written for this repository. They are
not scraped news and they are not the ITU course dump.

## Layout

```text
examples/
  README.md                 (this file)
  configs/                  JSON snapshots of the 2023 knobs
  data/                     synthetic CSVs, one per pipeline stage
  scripts/                  small tools that run on the fixtures
```

Start with the data, then the scripts.

## Data

| File | Stage | Columns |
| --- | --- | --- |
| `data/sample_articles.csv` | source dump | `id`, `article text` |
| `data/sample_translated.csv` | after da→en | `id`, `body`, `translated` |
| `data/sample_summarized.csv` | after English summary | `id`, `body`, `translated`, `summary` |
| `data/sample_labeled.csv` | after en→da | `id`, `body`, `summary` |
| `data/sample_nordjylland_mini.csv` | eval-shaped | `input_text`, `target_text`, … |
| `data/expected_columns.json` | contracts | per-stage required columns |

English `translated` / `summary` columns are hand-written personal
translations of the same fiction, not model output. Treat them as
**shape examples**, not as a quality baseline for OPUS-MT or T5.

## Configs

| File | Mirrors |
| --- | --- |
| `configs/pipeline.example.json` | filenames and stage order |
| `configs/finetune.example.json` | `finetune.py` hyperparameters |
| `configs/evaluation.example.json` | the two eval scripts |

The root Python files do not read these JSONs. `validate_pipeline_config.py`
and `dry_run_pipeline.py` do.

## Scripts

Run them from the repository root.

```bash
# Column contracts, empty cells, id uniqueness
python examples/scripts/inspect_dataset.py --stage source \
  --path examples/data/sample_articles.csv

python examples/scripts/inspect_dataset.py --stage labeled \
  --path examples/data/sample_labeled.csv

python examples/scripts/inspect_dataset.py --stage nordjylland \
  --path examples/data/sample_nordjylland_mini.csv

# Sentence packing used by translate.py / summary.py
python examples/scripts/chunk_text.py \
  --path examples/data/sample_articles.csv \
  --column "article text" \
  --max-tokens 40

# Lead-N extractive stand-in for summary.py
python examples/scripts/extractive_summarize.py \
  --path examples/data/sample_translated.csv \
  --column translated \
  --sentences 2

# Walk source -> labeled using extractive stand-ins
python examples/scripts/dry_run_pipeline.py \
  --config examples/configs/pipeline.example.json \
  --input examples/data/sample_articles.csv \
  --output-dir /tmp/danish-news-dry-run

# Split a labeled file the way finetune.py expects
python examples/scripts/split_labeled_dataset.py \
  --input examples/data/sample_labeled.csv \
  --output-dir /tmp/danish-news-splits \
  --train 0.7 --validation 0.2 --test 0.1 --seed 2023

# Tiny ROUGE-style overlap (no evaluate / rouge-score install)
python examples/scripts/compute_overlap_metrics.py \
  --pred examples/data/sample_labeled.csv \
  --gold examples/data/sample_labeled.csv \
  --pred-col summary --gold-col summary

# Print one article with all aligned columns
python examples/scripts/preview_article.py --id demo-001

# Confirm the example JSONs parse and name the 2023 scripts
python examples/scripts/validate_pipeline_config.py \
  --config examples/configs/pipeline.example.json
```

`inspect_dataset.py --stage source` should report 10 rows and no
missing ids. The self-overlap metric command should print 1.0 for
ROUGE-1/2/L.

## What these examples deliberately do not do

- They do not call Hugging Face or CTranslate2.
- They do not download Nordjylland News.
- They do not train mT5.
- They do not claim to reproduce 2023 ROUGE numbers.

For the real GPU path, use the root scripts and the notes in
[`../docs/`](../docs/README.md).
