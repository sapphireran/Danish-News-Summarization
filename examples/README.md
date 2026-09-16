# Examples

CPU-only walkthroughs of the 2023 pipeline. They read the fictional
articles in `data/` and never import `torch`.

Quick start from the repository root:

```bash
PYTHONPATH=. python examples/walk_one_article.py dn-001
PYTHONPATH=. python examples/chunk_articles.py --max-length 40
PYTHONPATH=. python examples/compare_chunk_strategies.py
PYTHONPATH=. python examples/inspect_schema.py --stage labeled \
  --csv examples/data/sample_labeled_dataset.csv
PYTHONPATH=. python examples/dry_run_pipeline.py
```

`data/` holds one CSV per pipeline stage plus `sample_article_index.csv`.
`output/` is created by the dry-run and is gitignored.

Full narrative: [docs/examples.md](../docs/examples.md).
