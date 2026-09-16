# Overview

## Course context

This repository is a **personal** final project for ITU's *Advanced Natural Language Processing and Deep Learning* course (2023). The assignment was to build a non-trivial sequence-to-sequence system, justify the data story, and evaluate it. The project chose **Danish news summarization** because:

- Danish news text is easy to collect and legally discuss in a classroom setting.
- Abstractive summarization is a clean seq2seq task (long document in, short document out).
- Off-the-shelf Danish summarizers were weak compared with English ones.
- A public evaluation set existed: Nordjylland news summarization (used here via Hugging Face).

The committed Python files are the original course scripts, lightly bug-fixed in late 2023. They were written to run on a single GPU machine, with hard-coded filenames and a few leftovers from earlier NLLB experiments. This documentation does not rewrite those scripts. It explains them, and the `examples/` tree lets you walk the *data contracts* on a CPU.

## Problem statement

**Input:** a Danish news article (a few hundred to a few thousand tokens).

**Output:** a short Danish abstract, on the order of one to three sentences, that a reader could use as a stand-in for the lede.

**Constraint:** no large human-written Danish summary corpus was used for training. Labels were manufactured by a translate → summarize → translate-back loop.

That constraint is the whole project. The modeling piece (fine-tune `mT5`) is standard Hugging Face `Seq2SeqTrainer` code. The interesting engineering is everything that happens *before* `trainer.train()`:

- sentence-aware chunking so OPUS-MT and T5 never see 2k-token walls of text,
- CTranslate2 so translation is fast enough to label thousands of articles,
- a deliberate English pivot because English news summarizers were stronger,
- a later evaluation on *human* Danish summaries so the silver-label noise is visible.

## Design in one paragraph

Helsinki-NLP OPUS-MT (`da-en`, `en-da`) is converted with CTranslate2. Danish articles are split into sentence packs that fit a 512-token translator, rendered into English, then packed again for `mrm8488/t5-base-finetuned-summarize-news` (max 512 input, ~80-token summaries, repetition penalty 5.0). Those English summaries are translated back to Danish and treated as targets. `google/mt5-large` is fine-tuned for 20 epochs with Adafactor, polynomial decay, and ROUGE-1 as the checkpoint metric. Inspection and scoring happen on Nordjylland news, not on the silver labels, so you can see whether the model learned Danish news style or only translationese.

```
Danish article
    │
    ▼
OPUS-MT da→en  (CTranslate2, sentence packs)
    │
    ▼
English T5 news summarizer  (chunk long articles, join chunk summaries)
    │
    ▼
OPUS-MT en→da  (CTranslate2)
    │
    ▼
Silver pair (Danish body, Danish summary)
    │
    ▼
mT5 fine-tune  →  local checkpoint
    │
    ▼
Nordjylland eval  (ROUGE + BERTScore, lang=da)
```

## What this repo is not

- It is not a hosted API or a packaged library.
- It is not a reproduction of a published paper. The method is a well-known low-resource pattern (translate-train / pivot-language labeling), implemented as course code.
- It is not multi-document or query-focused summarization.
- It does not include the original 10k-article dump. That file was local to the course machine (`10000_articles_without_linebreaks.csv`).

## How to use the two “modes”

| Mode | When | What you run |
| --- | --- | --- |
| **Examples / docs** | You want to understand schemas, chunking, and label quality without downloading 1B+ parameters | `examples/*.py` plus this folder |
| **Full pipeline** | You have CUDA, disk, and a Danish article CSV | the six root scripts, in the order in the root README |

If you only have an afternoon, run the example mode. If you want to recreate the 2023 numbers, start at [reproducing-course-run.md](reproducing-course-run.md) and budget for model downloads plus a long `mT5-large` train.
