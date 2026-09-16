# Synthetic fixtures

These files copy the **column names** of the 2023 pipeline. The articles are invented. They are not from the 10k dump, Nordjylland-Posten, or any scraped site.

Use them with the demos in the parent folder. Do not train a real mT5 run on six rows and expect a summarizer.

| File | Stands in for |
| --- | --- |
| `sample_source_articles.csv` | `10000_articles_without_linebreaks.csv` (`id`, `article text`) |
| `sample_translated_articles.csv` | `translated_articles.csv` (`id`, `body`, `translated`) |
| `sample_summarized.csv` | `summarized_file_ml80_rp5.0.csv` (`id`, `body`, `translated`, `summary` in English) |
| `sample_labeled_dataset.csv` | `labeled_dataset_ml80_rp5.0.csv` (`id`, `body`, `summary` in Danish) |
| `sample_train_dataset.csv` | `datasets/train_dataset.csv` |
| `sample_validation_dataset.csv` | `datasets/validation_dataset.csv` |
| `sample_test_dataset.csv` | `datasets/test_dataset.csv` |
| `sample_public_eval.jsonl` | Nordjylland-style `input_text` / `target_text` rows |

`demo-006` is a single long Danish sentence. It exists so `demo_sentence_chunking.py` can show the 2023 long-sentence splitter.

English columns are human-written stand-ins for OPUS-MT and T5, not model output. Danish silver summaries are written as if a careful back-translation had happened, not as if CTranslate2 had been run in this repo.
