# Sample data (fictional)

Every row in this folder is **invented**. Towns, councils, clubs, bakeries, and ferry lines are not real Danish news copy and are not taken from Nordjylland, DaNewsroom, or any scraped dump.

I wrote the Danish bodies, the English pivots, and the Danish silver summaries by hand so the toy pipeline can run without OPUS-MT, T5, or a GPU. That also means these files are **not** a measure of translation quality. They are fixtures.

## Files

| File | Columns | Role |
| --- | --- | --- |
| [`sample_articles.csv`](sample_articles.csv) | `id`, `article text` | Input shape of `translate.py` (the 2023 dump used the same two names). |
| [`sample_translated.csv`](sample_translated.csv) | `id`, `body`, `translated` | Output shape of `translate.py`. `body` is the original Danish. |
| [`sample_summaries_en.csv`](sample_summaries_en.csv) | `id`, `body`, `translated`, `summary` | Output shape of `summary.py`. `summary` is English. |
| [`sample_labeled.csv`](sample_labeled.csv) | `id`, `body`, `summary` | Output shape of `translate_back.py`. `summary` is Danish. |
| [`splits/train.csv`](splits/train.csv) | `id`, `body`, `summary` | Six-row stand-in for `datasets/train_dataset.csv`. |
| [`splits/validation.csv`](splits/validation.csv) | `id`, `body`, `summary` | Two-row stand-in for `datasets/validation_dataset.csv`. |
| [`splits/test.csv`](splits/test.csv) | `id`, `body`, `summary` | Two-row stand-in for `datasets/test_dataset.csv`. |

Ids are stable slugs (`klintelund-cykelsti`, …). The 2023 dump used opaque integers; the toy set uses readable names so hop reports stay readable.

## How the ten stories are split

| Split | Ids |
| --- | --- |
| train | `klintelund-cykelsti`, `vesteroe-robotter`, `nordkyst-storm`, `havneby-faerge`, `lund-bageri`, `groenmark-vind` |
| validation | `fc-klintelund`, `mosevang-budget` |
| test | `sandvig-bibliotek`, `oesterhavn-kvote` |

`oesterhavn-kvote` is deliberately one long comma-heavy sentence so [`pack_report.py`](../pack_report.py) has something to break.

## What this is not

- Not licensed news text.
- Not a substitute for `10000_articles_without_linebreaks.csv`.
- Not a gold Nordjylland evaluation set. Human TV2 Nord summaries live on Hugging Face and stay out of git.
