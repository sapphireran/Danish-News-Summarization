# Example scripts

All commands assume the repository root as the working directory so
`examples/data/...` paths resolve.

```bash
python examples/scripts/<name>.py --help
```

`text_lib.py` is imported as a sibling module. Running the files as
scripts works because Python puts `examples/scripts/` on `sys.path[0]`.
The tests do the same.

| Script | Job |
| --- | --- |
| `inspect_dataset.py` | Check columns, empty cells, duplicate ids |
| `chunk_text.py` | Reconstruct the 2023 sentence packer |
| `extractive_summarize.py` | Lead-N baseline |
| `compute_overlap_metrics.py` | Tiny ROUGE-1/2/L overlap |
| `length_report.py` | Article vs summary length stats |
| `split_labeled_dataset.py` | Write `*_dataset.csv` splits |
| `dry_run_pipeline.py` | Source → labeled file contracts |
| `preview_article.py` | Side-by-side fixture dump |
| `validate_pipeline_config.py` | Example JSON still matches the repo |

Tests live in [`../tests/`](../tests/README.md).
