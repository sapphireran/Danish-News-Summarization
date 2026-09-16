# Examples

Everything under `examples/` is CPU-only and uses the standard library
plus the in-repo package. No `torch`, no Hub download, no GPU.

## Layout

```
examples/
  data/                         hand-written CSVs, one per pipeline stage
  chunk_articles.py             packed windows for each sample story
  compare_chunk_strategies.py   window counts at several budgets
  inspect_schema.py             CSV contracts + optional file check
  walk_one_article.py           one id through every stage
  dry_run_pipeline.py           write a fake four-stage run to output/
```

The same actions are also available as:

```bash
PYTHONPATH=. python -m danish_news_summarization.cli --help
```

## 1. Walk one article

```bash
PYTHONPATH=. python examples/walk_one_article.py dn-009
```

Prints the Danish body, the English translation, the English dek, the
Danish silver label, and the packed windows. Use this when a column
name in a doc does not match what you see in a CSV.

## 2. Chunk a corpus

```bash
PYTHONPATH=. python examples/chunk_articles.py --max-length 40
PYTHONPATH=. python examples/chunk_articles.py --id dn-002 --max-length 30
```

The budget is **whitespace tokens + 2 specials**, not OPUS-MT subwords.
Expect more windows in the real scripts.

## 3. Compare budgets

```bash
PYTHONPATH=. python examples/compare_chunk_strategies.py
PYTHONPATH=. python examples/compare_chunk_strategies.py --budgets 20 40 80 160
```

Each extra window is another GPU call in `translate.py` / `summary.py`.
The original pack budget is `int(512 * 0.9) = 460` *subword* tokens.

## 4. Validate a CSV

```bash
PYTHONPATH=. python examples/inspect_schema.py
PYTHONPATH=. python examples/inspect_schema.py --stage labeled \
  --csv examples/data/sample_labeled_dataset.csv
```

Exit code 1 means the file would crash `finetune.py` after you already
paid for translation.

## 5. Dry-run the silver-label loop

```bash
PYTHONPATH=. python examples/dry_run_pipeline.py
PYTHONPATH=. python examples/dry_run_pipeline.py --stubs --out examples/output/stubs
```

Default mode copies the hand-written translations and summaries (so the
CSVs look like a finished experiment). `--stubs` prefixes `[da→en]` /
`[en→da]` and keeps the first two sentences as a fake summary, which
makes error propagation visible.

Outputs (under `examples/output/` unless you override `--out`):

| file | stage |
| --- | --- |
| `sample_danish_articles.csv` | raw |
| `sample_translated_articles.csv` | translated |
| `sample_summarized_articles.csv` | summarized |
| `sample_labeled_dataset.csv` | labeled |
| `compression_stats.json` | word-count table |

## 6. Regenerate committed fixtures

```bash
PYTHONPATH=. python -m danish_news_summarization.cli export-data --out examples/data
```

Do this after editing `danish_news_summarization/sample_data.py`.

## Tests

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
```

The tests cover sentence splitting (including `t.eks.` and `2,4`),
packing, schema errors, the dry-run report, and the CLI writers.
They are the right first check after a refactor of `chunking.py`.
