# Example fixture data

Hand-authored, fictional Danish news copy used by the CPU examples. These
rows are **not** model output and they are **not** from the original 10k
scrape (`10000_articles_without_linebreaks.csv`).

Canonical text lives in `corpus.py`. `python examples/build_sample_csvs.py`
writes the CSVs below from that module. Keep both in sync; the chunking
example compares them.

## Files

| File | Pipeline stage | Columns |
| --- | --- | --- |
| `sample_articles.csv` | `raw` | `id`, `article text` |
| `sample_translated.csv` | `translated` | `id`, `body`, `translated` |
| `sample_summaries_en.csv` | `summarized_en` | `id`, `body`, `translated`, `summary` |
| `sample_labeled.csv` | `labeled` | `id`, `body`, `summary` (Danish silver-style) |
| `sample_references.csv` | `labeled` | `id`, `body`, `summary` (independent headlines) |

Column names match the 2023 scripts on purpose. `eval.py` / `use_model.py`
read Nordjylland rows as `input_text` / `target_text`; that schema is
documented in `docs/dataset.md` and is not used by these fixtures.

## How the summaries differ

- `summary_en` / `summary_da` in `corpus.py` are **silver-style**: they stay
  close to the article and resemble what an English news T5 plus back-translation
  might keep.
- `reference_da` is a **headline-style** rewrite used only by
  `03_evaluate_toy_summaries.py`, so ROUGE is not trivially 1.0.

Treat the numbers from that example as a tutorial, not as the Nordjylland
scores from the course report.
