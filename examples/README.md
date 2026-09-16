# Examples

CPU-only walkthroughs of the 2023 ITU Danish news summarization pipeline.
They use eight fictional fixture articles in `examples/data/` and the
helpers in `danish_news/`. None of these scripts download OPUS-MT, T5, or
mT5.

The GPU course scripts in the repository root are unchanged. Use those when
you have CUDA, CTranslate2 weights, and the original 10k-article CSV.

## Setup

From the repository root (Python 3.9+):

```bash
python -m pip install -e ".[dev]"
python examples/build_sample_csvs.py
```

`build_sample_csvs.py` regenerates the stage CSVs from `examples/data/corpus.py`.
The generated files are also committed, so the command is only required after
you edit the corpus.

## Scripts

| Script | What it shows |
| --- | --- |
| `01_chunk_danish_article.py` | Sentence split + window packing on one article |
| `02_pipeline_dry_run.py` | DA→EN → English summary → EN→DA with a glossary backend |
| `03_evaluate_toy_summaries.py` | ROUGE-1/2/L, compression, novelty on fixture labels |
| `04_inspect_csv_schema.py` | Column contracts used by the course scripts |
| `05_window_budget.py` | How window count changes with the length budget |
| `build_sample_csvs.py` | Rebuild `examples/data/*.csv` from `corpus.py` |

## Commands

```bash
python examples/01_chunk_danish_article.py --article-id harbour-plan --max-units 40
python examples/01_chunk_danish_article.py --article-id library-budget --json
python examples/02_pipeline_dry_run.py
python examples/03_evaluate_toy_summaries.py
python examples/03_evaluate_toy_summaries.py --format markdown
python examples/04_inspect_csv_schema.py
python examples/05_window_budget.py --article-id harbour-plan
python examples/05_window_budget.py --article-id harbour-runon --unit chars --budgets 80,160,320
```

`example_config.json` sets the default CSV names and the word budget. Pass
`--config path/to.json` to any script that loads it.

Dry-run output is written to `examples/output/` and is gitignored. The
files in `examples/data/` are hand-authored (human DA/EN/summaries), not
glossary output.

## Fixture ids

| id | Why it is in the set |
| --- | --- |
| `wx-aarhus` | Short weather item, one window |
| `museum-aalborg` | Medium culture item |
| `harbour-plan` | Long municipal copy; several windows at a 40-word cap |
| `superliga-aab` | Sports proper names |
| `offshore-wind` | Energy / consultation wording |
| `library-budget` | Danish abbreviations (`mio. kr.`, `bl.a.`, `f.eks.`, `kl.`) |
| `harbour-runon` | Single overlong sentence; exercises `split_long_sentence` |
| `ferry-strike` | Transport / strike item |

See `examples/data/README.md` for the CSV column layout.
