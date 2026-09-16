# Sample hops

These CSVs are the eight Sejerø briefs projected into the column shapes the
2023 scripts actually wrote. They are fiction. They are not a slice of the
10 000-article dump.

| File | Course analogue | Columns |
| --- | --- | --- |
| `00_raw_articles.csv` | `10000_articles_without_linebreaks.csv` | `id`, `article text` |
| `01_translated_articles.csv` | `translated_articles.csv` | `id`, `body`, `translated` |
| `02_summarized_articles.csv` | `summarized_file_ml80_rp5.0.csv` | `id`, `body`, `translated`, `summary` |
| `03_labeled_dataset.csv` | `labeled_dataset_ml80_rp5.0.csv` | `id`, `body`, `summary` |
| `03_oracle_labels.csv` | (desk only) | `id`, `body`, `summary`, `oracle` |
| `04_train_dataset.csv` | `datasets/train_dataset.csv` | `id`, `body`, `summary` |
| `04_validation_dataset.csv` | `datasets/validation_dataset.csv` | `id`, `body`, `summary` |
| `04_test_dataset.csv` | `datasets/test_dataset.csv` | `id`, `body`, `summary` |
| `05_public_eval_shape.csv` | Nordjylland / ScandEval columns | `input_text`, `target_text`, `text_len`, `summary_len` |
| `06_slot_cards.csv` | (desk only) | `id`, `who`, `what`, `when`, `where`, `why`, `how` |
| `07_planted_errors.csv` | (desk only) | `id`, `kind`, `summary`, `dropped_slots`, `note` |
| `08_figures.csv` | (desk only) | `id`, `figures` |

Regenerate from the fixtures:

```bash
PYTHONPATH=. python3 -m sejeroe hops
```

The 5 / 2 / 1 split is `SEJ-001`–`SEJ-005` train, `SEJ-006`–`SEJ-007`
validation, `SEJ-008` test. That is a toy split for schema checks, not a
training set.
