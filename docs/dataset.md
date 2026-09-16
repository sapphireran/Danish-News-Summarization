# Dataset

The course pipeline never used a single Hugging Face dataset for training.
It built silver labels from a local CSV of Danish news articles, then
evaluated on a *different* corpus that does have human summaries.

## Files the course scripts expect

| Stage | Default filename | Columns | Produced by |
| --- | --- | --- | --- |
| Raw scrape | `10000_articles_without_linebreaks.csv` | `id`, `article text` | scrape / export (not in this repo) |
| DA→EN | `translated_articles.csv` | `id`, `body`, `translated` | `translate.py` |
| EN summary | `summarized_file_ml80_rp5.0.csv` | `id`, `body`, `translated`, `summary` | `summary.py` |
| Silver DA | `labeled_dataset_ml80_rp5.0.csv` | `id`, `body`, `summary` | `translate_back.py` |
| Train split | `datasets/train_dataset.csv` | `id`, `body`, `summary` | manual split of the silver file |
| Validation | `datasets/validation_dataset.csv` | `id`, `body`, `summary` | same |
| Test (silver) | `datasets/test_dataset.csv` | `id`, `body`, `summary` | same |

`danish_news.schemas.STAGE_SCHEMAS` is the machine-readable copy of this
table. `examples/04_inspect_csv_schema.py` checks the fixture CSVs against
it.

The raw column is `article text` (with a space). After translation the same
string is stored as `body`. Fine-tuning never sees `translated`.

## What is not in the repository

The original 10k-article CSV, the CTranslate2 model directories, and the
`datasets/` splits are local artefacts. They were large, possibly
copyrighted news text, and are not committed. The eight rows in
`examples/data/` are original fictional stand-ins with the same columns.

## Nordjylland evaluation data

`eval.py` and `use_model.py` do **not** read the silver CSVs. They load a
public Danish summarization set:

| Script | Dataset id | Split | Text columns |
| --- | --- | --- | --- |
| `use_model.py` | `ScandEval/nordjylland-news-summarization-mini` | `test` | `input_text`, `target_text` |
| `eval.py` | `alexandrainst/nordjylland-news-summarization` | `test` | `input_text`, `target_text` |

Both also expose `text_len` and `summary_len`, which the tokenization
`remove_columns` lists mention. The mini split is a convenience sample;
the Alexandra Institute dump is the full evaluation set used for the
reported metrics.

That means the training distribution (silver labels from a generic Danish
news scrape, pivoted through English) and the evaluation distribution
(Nordjylland news with journalist/editor summaries) are not the same.
Scores on Nordjylland measure transfer, not reconstruction of the
silver labels.

## Suggested split recipe (historical)

The course scripts do not include the split. A reasonable default if you
rebuild silver labels:

* shuffle on `id`
* 80% train / 10% validation / 10% held-out silver test
* keep the Nordjylland test set as the *external* test

Do not tune on Nordjylland if you want the `eval.py` number to stay a
true test score.

## Fixture corpus

`examples/data/corpus.py` holds eight fictional items chosen to hit
pipeline edge cases:

| id | Notes |
| --- | --- |
| `wx-aarhus` | Three short sentences |
| `museum-aalborg` | Medium length, named entity (museum) |
| `harbour-plan` | Long municipal copy; multiple windows at a 40-word cap |
| `superliga-aab` | Sports score line |
| `offshore-wind` | Numbers and a consultation date |
| `library-budget` | `mio. kr.`, `bl.a.`, `f.eks.`, `kl.`, `pct.`, `dvs.` |
| `harbour-runon` | One sentence that exceeds a small word budget |
| `ferry-strike` | Strike / transport |

`sample_labeled.csv` is silver-style. `sample_references.csv` is a second
human headline used only by the toy evaluator.
