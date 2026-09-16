# Example configs

These JSON files are a personal index of knobs that the 2023 scripts
hard-code in Python. They are documentation you can load, not a new
training framework.

| File | Loaded by |
| --- | --- |
| `pipeline.example.json` | `dry_run_pipeline.py`, `validate_pipeline_config.py` |
| `finetune.example.json` | `validate_pipeline_config.py` |
| `evaluation.example.json` | `validate_pipeline_config.py` |

If you change a filename in a root script, change the matching JSON
here in the same commit so the examples stay honest.
