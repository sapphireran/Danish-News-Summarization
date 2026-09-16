# Overview and design rationale

This note is the map of the 2023 ITU project: what problem it tried to solve, which constraints shaped the architecture, and how the rest of `docs/` and `examples/` fit together.

## Problem

Abstractive summarization for Danish news is a low-resource problem relative to English:

- High-quality Danish article–summary pairs were scarce in public datasets.
- English news summarizers (T5, BART, PEGASUS, and their fine-tunes) were already strong.
- Multilingual encoder–decoders such as mT5 can *represent* Danish, but they still need in-language supervision to produce fluent Danish leads rather than English or code-switched output.

The course project therefore asked a practical question:

> If we can automatically manufacture Danish summaries, can we fine-tune a multilingual model that then summarizes Danish news *directly*, without a translate–summarize–translate loop at inference time?

That last clause matters. The silver-label pipeline is a **training-data factory**. Once mT5 is fine-tuned, inference is a single Danish→Danish generation step.

## Constraints that drove the design

| Constraint | Consequence |
| --- | --- |
| Course compute budget (a single GPU, not a cluster) | OPUS-MT + CTranslate2 for translation; T5-base for English summaries; mT5-large for the final model rather than a 13B decoder |
| No licensed Danish annotators | Labels are model-generated, not journalist-written |
| News articles longer than 512 SentencePiece tokens | Custom sentence packing before every seq2seq call |
| Need a number that can be compared to other student projects | ROUGE-1/2/L plus Danish BERTScore on Nordjylland News |

## High-level architecture

```
Danish article
    │
    ▼
OPUS-MT da→en  (CTranslate2)     ── training-time only
    │
    ▼
English T5 news summarizer       ── training-time only
    │
    ▼
OPUS-MT en→da  (CTranslate2)     ── training-time only
    │
    ▼
Silver pair (Danish body, Danish summary)
    │
    ▼
Fine-tune mT5
    │
    ▼
Danish→Danish summarizer         ── what you deploy / evaluate
```

At evaluation time the model is scored against **human or editorially curated** Danish summaries from the Nordjylland News summarization set, not against its own silver labels. That is the only way the automatic labels can be stress-tested.

## What this repository is (and is not)

**Is**

- A personal academic record of the 2023 pipeline.
- A place to document the design so a later self can rerun or critique it.
- A small library of GPU-free examples that demonstrate chunking, silver-label bookkeeping, and toy ROUGE/overlap metrics.

**Is not**

- A production news product.
- A claim that silver labels match journalist quality.
- Employer or company intellectual property. The work predates any industry affiliation and stays on this personal GitHub account.

## How to read the rest of the docs

If you want the *story* of a single article moving through the factory, start with [01-pipeline.md](01-pipeline.md) and then walk [examples/silver_label_walkthrough.md](../examples/silver_label_walkthrough.md).

If you want to know why sentences are packed the way they are, read [02-chunking-and-length.md](02-chunking-and-length.md) and run `examples/run_chunking_demo.py`.

If you want to reproduce training, jump to [03-models-and-hyperparameters.md](03-models-and-hyperparameters.md) and [07-reproduction.md](07-reproduction.md).

If you want to decide whether the method is ethically or scientifically sound enough to reuse, read [06-limitations-and-ethics.md](06-limitations-and-ethics.md) first.

## Design bets, stated plainly

1. **Translation quality is "good enough" for news prose.** OPUS-MT da↔en is strong on straightforward journalistic sentences and weaker on idioms, quotes, and named entities with Danish morphology.
2. **An English news T5 transfers the *task*, not the language.** The hope is that "what is a news lead" is more language-agnostic than the surface form.
3. **mT5 can unlearn English-centric phrasing** if it sees enough Danish bodies paired with Danish (translated) leads.
4. **Automatic metrics still say something useful** on a real Danish test set, even if they do not measure factuality.

Each of those bets can fail independently. The evaluation protocol in [05-evaluation.md](05-evaluation.md) only tests the composition of all four.

## Original scripts versus documentation

Root-level `*.py` files are the course submission. They contain hardcoded filenames, a 10-row debug slice in `summary.py`, deprecated `datasets.load_metric` calls, and OPUS-MT tokenizers constructed with NLLB-style language codes (`dan_Latn`, `eng_Latn`). Those details are documented rather than silently "fixed," because changing them would rewrite the historical experiment.

The example code under `examples/` is new, self-contained, and covered by `tests/`.
