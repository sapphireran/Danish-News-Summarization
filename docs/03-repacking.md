# Repacking at every hop

The 2023 cascade looks like a pipeline of files. It is also a pipeline of
**independent packers**. No window id is written to CSV. Each script
reads a text column, splits sentences again, and builds new crates.

```
Danish article
    │  translate.py  (OPUS da-en tokenizer, budget 460, character saw)
    ▼
English article  (one string, windows forgotten)
    │  summary.py    (T5 tokenizer, budget 512, character saw)
    ▼
English summary  (pane summaries joined with spaces, windows forgotten)
    │  translate_back.py  (OPUS en-da tokenizer, budget 512, no saw)
    ▼
Danish silver label
    │  finetune.py   (mT5 tokenizer, body 1024 / label 128, no packing)
    ▼
Truncated training pair
```

## Why this is not harmless

The English string that `summary.py` sees is not aligned to the Danish
windows that `translate.py` used. OPUS may merge or split clauses.
`sent_tokenize` on the English side uses NLTK's English punkt model, not
the Danish one. A cut that fell after a Danish subordinate clause can
reappear in the middle of an English sentence, or not at all.

Then `translate_back.py` packs the *summaries*, which are short, with a
512-token budget. For a single-pane article the back-translation is
usually one window. For a four-pane article the concatenated English
summary can approach `4 * 80` T5 tokens and may need packing — or, with
no long-split, it becomes one over-long sequence.

## What Pakhuset records

The CPU hops keep a `pane_id` on every crate and write it through to a
sidecar table (`examples/data/pane_trace.csv`). That table is the thing
the 2023 CSVs are missing. It answers:

- How many Danish panes did article X produce at hop 1?
- How many English panes did the re-split produce at hop 2?
- Did hop 2 pane 0 cover the same sentences as hop 1 pane 0?
- Which silver-label sentences came from an underfilled last pane?

Without those ids, "the model dropped the kroner amount" is unanswerable.
The amount may have sat in pane 2 of the Danish packing, pane 1 of the
English packing, and then in the truncated tail of a 128-token mT5 label.

## Alignment in the lab

Toftevig fixtures are sentence-aligned by construction: each Danish
sentence has a canned English sentence with the same index. That is
cheating, on purpose. It lets `examples/walk_windows.py` show hop-2
repacking *in isolation* from translation error. Real OPUS output would
add a second misalignment on top.
