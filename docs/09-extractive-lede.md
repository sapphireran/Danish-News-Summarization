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

On the eight Sejerø briefs the numbers are less flattering to "just copy
the lede" than a slogan would like:

- **Manchet coverage** of `lead1` and `silver` is usually *tied*. Both
  keep a news first sentence. T5 is good at ledes.
- **Slot recall** of `lead2` (first two Danish sentences) often matches
  or beats silver (`SEJ-003`, `SEJ-004`, `SEJ-006`). Compression is not
  free: the second sentence holds WHY/HOW/figures.
- **Editorial gates** are where silver loses. Quotes, gold figures, and
  the contrast *men* fall out of `max_length=80` even when ROUGE-1
  against a human oracle still looks polite.

That is the point of silver labelling. The course pipeline taught mT5 to
imitate *silver*, so a model can learn to drop Karen Møller's name and
the extra-evening sailing because T5 already dropped them. The extractive
baseline is there so that drop is visible, not so we can pretend T5 did
no work.

```bash
PYTHONPATH=. python3 examples/compare_baselines.py
PYTHONPATH=. python3 -m sejeroe baseline --id SEJ-001
```

`summary.py` concatenates per-window T5 outputs. On a long Nordjylland
article that is worse than lead-1: you get several mini-ledes glued
together. The Sejerø briefs are short enough that the English hop is a
single window, so the comparison here is fairer than on the 10 000-row
dump.
