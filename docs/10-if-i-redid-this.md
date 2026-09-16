# If I reran this as a personal project

These are notes to myself, not a patch series against the 2023 scripts.

## Keep

- Silver labelling as a way to bootstrap a language with little
  supervised summarization data.
- Writing every hop to CSV. Debugging a cascade without artifacts is
  guesswork.
- A public Danish news test set (Nordjylland-style) that is *not* the
  silver-label train distribution.

## Change first

1. **One packer, one unit.** Count the same tokenizer ids for the long
   saw and for the window accumulator. Persist `pane_id` in the CSV.
2. **Do not concatenate pane summaries into a training target.** Either
   summarize the article once at 1024+ tokens, or train on pane-level
   pairs and decode with a separate fusion step. The 128-token label cap
   makes multi-pane concatenation busywork.
3. **Danish sentence segmentation** before packing. Clocks, ordinal
   dates, and `mio. kr.` are packing bugs when they become sentence
   boundaries.
4. **Export both OPUS directions** in the converter, or switch the pair
   to a single multilingual model whose language prefixes are real.
5. **Align train and eval checkpoints.** The file that writes
   `./large_model` should be the file that eval loads.
6. **Drop `no_repeat_ngram_size=1`** from any Danish decoder demo.
7. **Stop slicing `[:10]`** in committed labelling code. Put smoke-run
   flags in argparse.

## Change when there is time

- Replace English-news T5 with a Danish or multilingual summarizer so
  hop 2 is not a domain-and-language jump.
- Log figure-survival (amounts, dates, ordinance numbers) as a first-
  class metric beside ROUGE. Danish compounds make ROUGE pessimistic;
  figure survival is closer to what a local reader notices.
- Decode mT5 in bf16. Treat fp16 NaNs as a setup failure, not as a
  random seed issue.
- Keep a ten-article fictional kit like Toftevig in git so the packing
  house can be tested without the 10k dump or a GPU.

## Do not bother

- Re-tuning `repetition_penalty=5.0` in isolation. It is compensating
  for a model that is allowed to see the source and likes to copy. A
  better hop-2 model, or constrained decoding for names and amounts,
  is the actual lever.
- Building a shared library *inside* the 2023 files. They are an exam
  snapshot. New work belongs next to them, which is what `pakhus/` is.
