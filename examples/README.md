# Examples

All of these stay on the standard library.

| Command | What you see |
| --- | --- |
| `python3 examples/run_almanac.py` | fixtures, validator, ledger means, NLLB scar, HTML path |
| `python3 examples/inspect_brief.py bh-11` | one well, its measures, its planted comma shift |
| `python3 examples/pack_brief.py bh-05 --budget 36` | 2023 windows on the cycle-path note |
| `python3 -m maalestok report` | `examples/report/index.html` |

CSV fixtures:

| File | 2023 stage |
| --- | --- |
| `data/00_raw_articles.csv` | `id`, `article text` |
| `data/01_translated_articles.csv` | `id`, `body`, `translated` |
| `data/02_summarized_articles.csv` | plus English `summary` |
| `data/03_labeled_dataset.csv` | Danish silver `summary` |
| `data/03_labeled_oracle.csv` | faithful Danish `summary` |
| `data/04_{train,validation,test}_dataset.csv` | 10/3/3 |
| `data/05_public_eval_shape.csv` | Nordjylland-style columns |
| `data/planted_errors.csv` | the scars the ledger should name |

Regenerate with `python3 -m maalestok fixtures`.
