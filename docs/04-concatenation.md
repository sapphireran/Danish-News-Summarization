# Concatenation, then truncation

`summary.py` generates with `max_length=80` **per English pane**, then
joins pane summaries with a space. Silver-label length therefore scales
with the number of panes, not with a target brief length.

## Worked numbers

Take the course constants literally.

| Article length (T5 tokens, English) | Panes at 512 | Concatenated silver (≤80 each) | mT5 label budget in `finetune.py` | What training actually sees |
| --- | --- | --- | --- | --- |
| 400 | 1 | ≤80 | 128 | the whole silver brief |
| 900 | 2 | ≤160 | 128 | first ~128 tokens; pane 1's tail dropped |
| 1800 | 4 | ≤320 | 128 | first pane's brief plus a stub of pane 1 |

Two failure modes stack:

1. **Echoes.** Each pane is summarized as if it were a whole news story.
   Pane 0 writes a lede. Pane 1, which may be background, still tries to
   open like a lede and repeats the municipality name.
2. **Silent tail drop.** `finetune.py` tokenizes `summary` with
   `max_length=128`. Extra pane summaries produced at labelling time are
   not a richer target; they are extra bytes that get chopped.

Meanwhile the *body* is truncated to 1024 mT5 tokens of **Danish**, which
is a different tokenizer and a different language than the T5 panes that
created the label. The training pair is not "full article → full silver
label". It is "prefix of Danish article → prefix of concatenated pane
briefs".

## The leftover pane

The packer described in [02-packing-algorithm.md](02-packing-algorithm.md)
puts leftover sentences in a final short window. On Toftevig fixtures
that last pane is often 15–30% of the budget. The lab's extractive
stand-in still emits a "brief" for it (first sentence plus any figure
sentence). After concatenation, that leftover brief is the most likely
piece to fall past token 128.

So the part of the article that packing already treated as remainder is
also the part fine-tuning never asks the model to predict. Long-range
Danish news structure (decision at the top, economics in the middle,
reactions at the end) is trained as if only the decision existed.

## What the lab measures

`pakhus.concat` scores a silver-sim label against the oracle brief for:

- token length vs the 128 cap (how much would be truncated)
- repeated proper names across pane briefs (echo)
- figure survival (DKK, dates, `mio. kr.`, percentages)
- share of silver tokens that come from pane 0 vs later panes

Those numbers are for the fictional Toftevig set. They are a method
check, not a claim about the 2023 Nordjylland run.
