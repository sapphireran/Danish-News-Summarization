# Sample tables

Generated from `kystlinje.corpus` by `python3 -m kystlinje write-tables`.

| file | 2023 contract |
| --- | --- |
| `kystlinje_articles.csv` | `translate.py` input: `id`, `article text` |
| `kystlinje_translated.csv` | `id`, `body`, `translated` |
| `kystlinje_summarized.csv` | `id`, `body`, `translated`, `summary` |
| `kystlinje_labeled.csv` | `id`, `body`, `summary` (Danish silver) |
| `kystlinje_{train,validation,test}.csv` | `finetune.py` split shape, 12/3/3 |
| `kystlinje_ledger.csv` | entity survival flags per hop |
| `kystlinje_planted_errors.csv` | the handwritten scars |
| `kystlinje_briefs.json` | titles, themes, planted-error index |
| `course_schemas.json` | column contracts taken from the 2023 scripts |

Bodies are original fiction. They are not rows from
`10000_articles_without_linebreaks.csv`.
