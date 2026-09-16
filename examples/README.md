# Examples: personal methods lab

The December 2023 scripts need OPUS-MT conversions, a private 10k CSV, and a
GPU. This folder does not. It drives `silverlab`, a stdlib package that treats
the course project as a **methods question**:

1. What does an extractive Danish baseline already recover?
2. What does a from-scratch ROUGE say when the gold is a hand rewrite?
3. What hop errors would I have tagged if I had kept an error sheet?

```text
examples/
  data/fiction_briefs.json      16 original fictional briefs (lab-01 … lab-16)
  data/error_items.json         14 typed hop-error fixtures
  data/fiction_articles.csv     same briefs, 2023 `article text` header
  lab_report/index.html         generated HTML notebook
  run_lab.py                    CLI wrapper
```

## Commands

Run from the repository root. CPython 3.11+ is enough.

```bash
python3 -m silverlab list
python3 -m silverlab baselines --id lab-01
python3 -m silverlab metrics --against abstractive
python3 -m silverlab metrics --against extractive --detail
python3 -m silverlab catalog
python3 -m silverlab rubric
python3 -m silverlab validate
python3 -m silverlab report --out examples/lab_report/index.html
```

`python3 examples/run_lab.py` is the same CLI if you prefer not to use `-m`.

## What the numbers are (and are not)

The ROUGE table is computed on **these sixteen fictional briefs**. It is not a
reconstruction of the 2023 mT5 run. That printout was never committed, and this
lab will not invent one.

Gold **extractive** lines are substrings of the article. Gold **abstractive**
lines are hand-written rewrites. Score both; they answer different questions.

## Why these stories

Other personal-docs branches on this repo use municipal-news fiction. This
corpus is observatories, sourdough, jazz, moth counts, and a radio birthday —
still Danish, still news-shaped, but a different shelf.
