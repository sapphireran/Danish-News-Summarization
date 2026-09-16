# Frozen CLI transcripts

These files are the stdout of the example wrappers. Refresh them after a
deliberate fixture or formatter change:

```bash
PYTHONPATH=. python3 examples/walk_ferry.py > examples/expected_outputs/walk_ferry.txt
PYTHONPATH=. python3 examples/inspect_manchet.py --id SEJ-001 > examples/expected_outputs/inspect_manchet_sej001.txt
PYTHONPATH=. python3 examples/pack_lede.py --id SEJ-001 --policy manchet-tight > examples/expected_outputs/pack_lede_tight.txt
PYTHONPATH=. python3 -m sejeroe length > examples/expected_outputs/length_table.txt
PYTHONPATH=. python3 -m sejeroe baseline > examples/expected_outputs/compare_baselines.txt
PYTHONPATH=. python3 -m sejeroe gates --id SEJ-001 --role silver_da > examples/expected_outputs/gates_sej001_silver.txt
PYTHONPATH=. python3 -m sejeroe align --id SEJ-001 > examples/expected_outputs/align_sej001.txt
```
