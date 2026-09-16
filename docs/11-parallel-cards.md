# Parallel hops and article cards

Each Sejerø body was written as **matched Danish / English sentences**.
`translate.py` does not give you that alignment; it emits one English
string. The desk pairs sentences by index so a compound in sentence 0
can be compared with its English gloss in sentence 0.

The quote is almost always sentence index 3 (0-based). That is also the
sentence `summary.py` is most likely to drop under `max_length=80`.

```bash
PYTHONPATH=. python3 examples/align_parallel.py --id SEJ-001
PYTHONPATH=. python3 examples/write_cards.py
```

Cards land in [`generated/cards/`](generated/cards/README.md). Each card
repeats the slot card, the quote, the hops, the extractive comparison,
the stylebook, and the aligned sentences. They are the workbook pages
you can read without running Python.

If DA and EN sentence counts ever disagree, `python3 -m sejeroe validate`
fails. That is intentional: the closed world is supposed to stay
parallel.
