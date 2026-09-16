# 2023-shaped sample tables

Written by `python -m fjordpress fixtures`. Column names match the
constructors in the 2023 scripts, including the space in
`article text`.

| file | schema | stands in for |
| --- | --- | --- |
| `00_raw_articles.csv` | `id`, `article text` | `10000_articles_without_linebreaks.csv` |
| `01_translated_articles.csv` | `id`, `body`, `translated` | `translated_articles.csv` |
| `02_summarised_articles.csv` | `id`, `body`, `translated`, `summary` | `summarized_file_ml80_rp5.0.csv` |
| `03_labeled_dataset.csv` | `id`, `body`, `summary` (gold DA) | `labeled_dataset_ml80_rp5.0.csv` |
| `03_labeled_oracle_back.csv` | `id`, `body`, `summary` (oracle hop) | what a perfect translator + extractive hop would file |
| `04_train_dataset.csv` | `id`, `body`, `summary` | `datasets/train_dataset.csv` |
| `04_validation_dataset.csv` | `id`, `body`, `summary` | `datasets/validation_dataset.csv` |
| `04_test_dataset.csv` | `id`, `body`, `summary` | `datasets/test_dataset.csv` |
| `05_public_eval_shape.csv` | `input_text`, `target_text`, `text_len`, `summary_len` | the HF set `eval.py` actually loads |

Regenerate after editing `fjordpress/corpus.py`:

```bash
python examples/validate_fixtures.py
```
