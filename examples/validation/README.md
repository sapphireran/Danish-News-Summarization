# Validation example

`schema.py` encodes the four CSV shapes used by the root scripts.

```bash
python examples/validation/validate_samples.py
```

Checks:

- exact column names and order for each stage
- unique, non-empty ids
- no empty required cells
- Danish `summary` shorter than `body`
- train / validation / test ids are disjoint and cover the labeled file
- the four full-corpus sample files share the same id order

It will not tell you whether a summary is factually true.
