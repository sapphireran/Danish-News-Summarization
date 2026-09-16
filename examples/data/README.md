# Lab CSVs

Generated from `pakhus.corpus` (fictional Toftevig municipal news). Column
names follow the 2023 scripts; see [docs/06-csv-contracts.md](../../docs/06-csv-contracts.md).

| File | Course analogue |
| --- | --- |
| `00_raw_articles.csv` | `10000_articles_without_linebreaks.csv` (`id`, `article text`) |
| `01_translated_articles.csv` | `translated_articles.csv` |
| `02_summarized_articles.csv` | `summarized_file_ml80_rp5.0.csv` |
| `03_labeled_dataset.csv` | `labeled_dataset_ml80_rp5.0.csv` (silver-sim) |
| `03_labeled_oracle.csv` | hand-written Danish briefs |
| `04_train_dataset.csv` / `04_validation_dataset.csv` / `04_test_dataset.csv` | `datasets/*.csv` |
| `05_public_eval_shape.csv` | Nordjylland-like `input_text` / `target_text` |
| `pane_trace.csv` | lab sidecar (not in 2023) |
| `concat_scores.csv` | lab sidecar (not in 2023) |

Regenerate:

```bash
python examples/write_lab_csvs.py
```
