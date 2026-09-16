# Sample CSVs

Five fictional North Jutland-style notices written for this repository. They are **not** scraped journalism and they are **not** model output.

They exist so the pipeline's column names can be tested without the original 10k-article dump.

| File | Stage | Columns |
| --- | --- | --- |
| `00_raw_articles.csv` | Raw dump | `id`, `article text` |
| `01_translated_articles.csv` | After da→en | `id`, `body`, `translated` |
| `02_summarized_articles.csv` | After T5 | `id`, `body`, `translated`, `summary` |
| `03_labeled_dataset.csv` | After en→da | `id`, `body`, `summary` |
| `04_train_dataset.csv` | Fine-tune split | `id`, `body`, `summary` |
| `04_validation_dataset.csv` | Fine-tune split | `id`, `body`, `summary` |
| `04_test_dataset.csv` | Fine-tune split | `id`, `body`, `summary` |

English `translated` / `summary` fields are author-written stand-ins for OPUS-MT and T5. Danish `summary` fields are author-written stand-ins for back-translation.

Ids were chosen so a SHA-256 first-byte 80/10/10 split yields 3 / 1 / 1:

| id | Split |
| --- | --- |
| `aalborg-library-hours` | train |
| `hjoerring-wind-meeting` | train |
| `frederikshavn-school-wing` | train |
| `viborg-museum-sunday` | validation |
| `skagen-harbor-festival` | test |

Recompute and rewrite the `04_*.csv` files with:

```bash
python -m examples.demo_pipeline --refresh-splits
```

Do not replace these texts with copyrighted news articles.
