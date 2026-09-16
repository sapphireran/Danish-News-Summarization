# Sejerø Tidende examples

These examples stay on the standard library. They do not download OPUS, T5,
mT5, NLTK `punkt`, or the Nordjylland corpus. The original course scripts at
the repository root are unchanged.

From the repository root:

```bash
PYTHONPATH=. python3 -m sejeroe all
PYTHONPATH=. python3 examples/inspect_manchet.py
PYTHONPATH=. python3 examples/pack_lede.py --id SEJ-001
PYTHONPATH=. python3 examples/score_slots.py
PYTHONPATH=. python3 examples/walk_ferry.py
PYTHONPATH=. python3 examples/run_desk.py
```

| Script | What it shows |
| --- | --- |
| `run_desk.py` | Write CSVs, validate, print desk notes, refresh HTML. |
| `inspect_manchet.py` | First-sentence coverage of WHO / WHAT / WHEN / WHERE. |
| `pack_lede.py` | Course-like packing budgets on one Danish body. |
| `score_slots.py` | Slot recall, quotes, connectives, and planted ROUGE-blind errors. |
| `walk_ferry.py` | Every hop of `SEJ-001` in the same order as the 2023 scripts. |

Sample tables live in [`data/`](data/README.md). The generated clipboard is
[`report/index.html`](report/index.html). Frozen CLI transcripts used by
`tests/test_expected_outputs.py` sit in [`expected_outputs/`](expected_outputs).
