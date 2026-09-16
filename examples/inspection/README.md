# Inspection examples

```bash
python examples/inspection/inspect_dataset.py
python examples/inspection/print_pipeline_io.py
python examples/inspection/print_pipeline_io.py --id sample-010
python examples/inspection/print_pipeline_io.py --all-ids
```

`inspect_dataset.py` is the first thing to run on a new dump once you
have copied it into the same column shapes: if `summary/body` ratios
cluster near 1.0, the teacher hop probably failed.

`print_pipeline_io.py` is for reading, not scoring. The English columns
in the samples are hand-written stand-ins.
