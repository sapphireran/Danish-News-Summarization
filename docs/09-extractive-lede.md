# Extractive lede as a baseline

The 2023 `eval.py` never printed an extractive score. That hides a boring
but important fact about Danish news: **the first sentence is already a
summary**. If copying that sentence beats the silver label on WHO / WHAT /
WHEN / WHERE, the T5 hop is not earning its compression.

The desk reports four texts per brief:

| Name | What it is |
| --- | --- |
| `lead1_da` | First Danish sentence |
| `lead2_da` | First two Danish sentences |
| `silver_da` | Back-translated T5-shaped label |
| `oracle_da` | Human manchet written against the gold card |

On Sejerø briefs, `lead1` often **wins manchet coverage** and **wins slot
recall**. Silver wins on shortness. Oracle sits in between: short enough
to print, complete enough to pass a night editor.

That gap is the point of silver labelling. The course pipeline taught mT5
to imitate *silver*, so a model can learn to drop Karen Møller's name
because T5 already dropped it.

```bash
PYTHONPATH=. python3 examples/compare_baselines.py
PYTHONPATH=. python3 -m sejeroe baseline --id SEJ-001
```

`summary.py` concatenates per-window T5 outputs. On a long Nordjylland
article that is worse than lead-1: you get several mini-ledes glued
together. The Sejerø briefs are short enough that the English hop is a
single window, so the comparison here is fairer than on the 10 000-row
dump.
