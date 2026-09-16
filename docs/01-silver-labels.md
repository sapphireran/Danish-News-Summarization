# Silver labels as a method

The 2023 project did not start from a large Danish summarization corpus.
It started from unlabeled Danish news text and a bet: if you can
translate, you can borrow an English teacher.

The borrowed teacher was `mrm8488/t5-base-finetuned-summarize-news`. The
bridge was Helsinki-NLP OPUS-MT in both directions, converted with
CTranslate2. The student was `google/mt5-large` (trained) and, in the
eval scripts as committed, `google/mt5-small` loaded from `./small_model`.

```
Danish article
    │  opus-mt-da-en  (CTranslate2)
    ▼
English article
    │  English news T5
    ▼
English summary
    │  opus-mt-en-da  (CTranslate2)
    ▼
Danish silver summary
    │  mT5 fine-tune
    ▼
Danish student model
    │  scored on Nordjylland-News
    ▼
ROUGE + BERTScore  (never committed)
```

That diagram is the whole method. Everything else in the repo is
plumbing: sentence windows so 512-token models do not overflow, CSV
filenames hardcoded in each script, and a Hub eval set that does *not*
use the silver labels.

## What silver labels are not

They are not gold. A gold Danish summary would have been written by a
person looking at the Danish article. A silver summary is a Danish
sentence that has been through two translation models and one English
summarizer. Each hop can drop a number, flatten a name, invent a
specificity, or replace a compound with a generic.

They are also not the evaluation target. `eval.py` and `use_model.py`
read `input_text` / `target_text` from Nordjylland-News. Training on
silver and testing on human (or at least independently collected)
summaries is the honest setup. It is also why a high training ROUGE on
the silver validation split would not have answered the course question.

## Why the English pivot was tempting

In 2023 the English news-summarization stack was deep and cheap to
reuse. Danish abstractive models were thinner. Pivot translation is the
standard low-resource move: do the hard generation in a high-resource
language, then come home. The cost is translationese plus compounded
error. This branch exists to make that cost visible on a laptop, without
pretending the original 10k dump is available.

## What this branch does not do

It does not invent a 2023 scoreboard. The metric printout was never in
git. It does not patch `summary.py`'s `[:10]` slice, the converter that
only emits `opus-mt-en-da`, or the `large_model` / `small_model` mismatch.
Those scars are documented in [script archaeology](04-script-archaeology.md)
and left in the root scripts on purpose.
