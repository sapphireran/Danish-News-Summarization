# Examples

CPU-only companions to the 2023 GPU scripts. Nothing here downloads OPUS-MT, T5, or mT5. The sample rows are original fictional municipal news, written so the column names match the real pipeline.

## What you can run without weights

```bash
# regenerate the CSVs from the checked-in builder (idempotent)
python examples/data/build_samples.py

# pack a long article the same way translate.py / summary.py do
python examples/chunking/demo_chunking.py

# column names, uniqueness, empty cells, summary-vs-body length
python examples/validation/validate_samples.py

# character-length tables for every sample CSV
python examples/inspection/inspect_dataset.py

# print one id through every stage (Danish → English → EN summary → DA summary)
python examples/inspection/print_pipeline_io.py
```

Add `--help` to the inspection / validation / chunking demos for flags.

## Layout

| Path | Role |
| --- | --- |
| [`data/build_samples.py`](data/build_samples.py) | Source of truth for the fictional rows |
| [`data/*.sample.csv`](data/) | One file per pipeline artifact + train/val/test |
| [`chunking/article_chunker.py`](chunking/article_chunker.py) | Sentence packer extracted from the root scripts |
| [`chunking/demo_chunking.py`](chunking/demo_chunking.py) | Prints packed groups for `sample-010` |
| [`validation/schema.py`](validation/schema.py) | Shared CSV checks |
| [`validation/validate_samples.py`](validation/validate_samples.py) | Runs those checks on `data/` |
| [`inspection/inspect_dataset.py`](inspection/inspect_dataset.py) | Length stats |
| [`inspection/print_pipeline_io.py`](inspection/print_pipeline_io.py) | Side-by-side stage dump |
| [`configs/`](configs/) | YAML mirrors of hardcoded script knobs |

## Sample ids

| Id | Topic (fictional) | Split |
| --- | --- | --- |
| `sample-001` | Cycleway opening, Granebæk | train |
| `sample-002` | Municipal budget, Østerhavn | train |
| `sample-003` | Storm-surge warning, Lindefjord | train |
| `sample-004` | Football promotion, IF Granebæk | train |
| `sample-005` | Library workshop rebuild, Nabekøbing | train |
| `sample-006` | District-heating price rise | train |
| `sample-007` | Harbour festival | validation |
| `sample-008` | Hospital knee-wait times | validation |
| `sample-009` | School merger consultation | test |
| `sample-010` | Ten-year port plan (long; good for chunking) | test |

English `translated` / `summary` columns are **hand-written stand-ins** for Marian + T5, not model output. Use them to learn the schema, not to benchmark a translator.

## Configs are documentation

The YAML files are not loaded by `finetune.py` or friends. Copy values from them when you change a script, or keep them next to a future experiment log.
