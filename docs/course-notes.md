# Course-project notes (ITU 2023)

**Course:** Advanced Natural Language Processing and Deep Learning,
IT University of Copenhagen, 2023.

**Repo:** personal course deliverable. Later notes and examples in
`docs/` and `examples/` are not part of the original hand-in.

## Problem as framed then

Danish abstractive summarization had less ready-made supervision than
English. Nordjylland / TV2 Nord style data existed or was arriving, but
the project wanted to try a *generated*-label route:

- start from a pile of Danish news text
- borrow a strong English news summarizer
- move across the language barrier with OPUS-MT
- fine-tune a multilingual T5 so inference can stay in Danish

That is silver-label transfer, not “we annotated 10k summaries by hand”.

## Why mT5 and not a Danish-only encoder-decoder

mT5 already saw Danish in pretraining, so the fine-tune could be
relatively short (20 epochs on a constructed set) without training a
tokenizer from scratch. `mt5-large` is the train-time model;
`mt5-small` appears only in the eval scripts. Whether a small model was
trained as a runtime alternative or whether those scripts were written
first and never renamed is not recorded in git.

## Why the English hop

In 2023 the convenient open news summarizer the scripts call is
English-only (`mrm8488/t5-base-finetuned-summarize-news`). Direct Danish
T5 checkpoints were fewer and less news-specific. The hop accepts
translation noise in exchange for a summarizer that already knows
headline style.

A modern remake would at least *compare* against:

- fine-tuning mT5 / Scandinavian T5 directly on Nordjylland
- a Danish instruction model with a short prompt
- the extractive baseline in `examples/extractive_summary.py`

The extractive script is here so that comparison has a floor that runs
offline.

## What I would change if I were handing it in again

1. Delete `[:10]` and take paths from `argparse`.
2. Convert **both** OPUS directions in the same converter file.
3. Share one `split_into_sentences` module (now sketched in
   `examples/text_chunking.py`) instead of pasting it three times.
4. Fix the comma-flush bug or document it as intentional.
5. Write the train/val/test split with a seeded script.
6. Evaluate the silver validation set *and* Nordjylland, and say so.
7. Pin `requirements.txt` and record GPU model + wall time.
8. Stop loading `small_model` after training `large_model` unless that
   is a deliberate second run.

None of those edits are applied to the original `*.py` files in this
change set. The point of the personal docs is to remember the project
clearly, not to pretend the 2023 hand-in was a library.
