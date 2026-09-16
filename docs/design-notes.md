# Design notes

These are the “why” notes for the personal 2023 project. They are not a paper.

## The actual research question

Danish abstractive summarization was (and still is) data-poor compared with English. Human summary annotation for 10k local-news articles was out of scope for a course final. The bet:

> If we manufacture Danish summaries by pivoting through a strong English news summarizer, is the resulting signal clean enough to fine-tune mT5 so that it does something reasonable on a *human* Danish test set?

“Reasonable” was measured with ROUGE and BERTScore on Nordjylland news, plus reading a few outputs.

## Why not train a Danish summarizer from scratch?

- No large public Danish article–summary pair set of the size we wanted to train on.
- Encoder-decoders without pretraining would not converge on a course budget.
- mT5 already sees Danish in pretraining; the missing piece is the *summarization* mapping, not the language.

Silver labels are a way to teach that mapping without a newsroom annotation team.

## Why English as the pivot, not a multilingual summarizer directly?

In 2023 the best easily available news summarizer we could call in a loop was English T5 fine-tuned on news (`mrm8488/t5-base-finetuned-summarize-news`). Multilingual summarizers existed but were weaker on “write a lede” style, or heavier than the labeling budget allowed.

The cost is structural: the English model compresses *English news conventions* (inverted pyramid, AP-ish attribution). Danish local news (municipal quotes, sports clubs, ferry cancellations) gets forced through that style, then back.

## Where label noise enters

```
Danish syntax
    → OPUS-MT da-en   (translation noise)
    → English T5      (hallucination, lead bias, chunk seams)
    → OPUS-MT en-da   (back-translation noise, lost names)
    → mT5 target
```

Typical artifacts:

1. **Named-entity drift.** A street or a committee acronym becomes a generic “the municipality.”
2. **Number drift.** `klokken 21` survives or becomes `9 pm` and then `kl. 9` on the way back.
3. **Chunk seams.** Two half-summaries contradict or repeat.
4. **Over-fluency.** The Danish target is grammatical but journalistically bland.

mT5 will imitate this distribution. If 40% of silver targets drop the number, the model learns that dropping numbers is fine. That is why Nordjylland (human targets) is the judge, not a silver-held-out split.

## Why CTranslate2

Labeling is inference-heavy and training-light. Converting OPUS-MT once, then `translate_batch` over sentence packs, was the difference between overnight and “still running on Monday.” The converter file’s commented NLLB 3.3B line is the fossil of a “maybe a larger translator helps” experiment that did not become the default.

## Why mT5-large for training and mT5-small in eval scripts

`finetune.py` uses large because capacity helps when the targets are noisy: the model can fit the mapping without collapsing to copy-the-first-sentence as quickly. The eval scripts pointing at `small_model` are almost certainly from a later “can we ship a smaller checkpoint” attempt. Documented in [known-issues.md](known-issues.md); not resolved here.

## Why ROUGE-1 for model selection

It is cheap enough to run every epoch with generate. BERTScore-every-epoch on large would have dominated the GPU time. The downside: the trainer prefers models that overlap silver unigrams, i.e. models that sound like the pivot. A student rerun could select on validation BERTScore or on a small human-labeled slice instead.

## Chunking vs truncation

Two ways to handle long news:

| Strategy | Used where | Effect |
| --- | --- | --- |
| Truncate to 1024 | mT5 train/eval | Tail of the article never seen |
| Sentence-pack to 512 and summarize each pack | English T5 labeling | Tail is seen, but only locally |

The trained model therefore learns from *stitched local abstracts* but at inference is asked to summarize a *truncated full article* in one shot. That train/serve mismatch is worth remembering when outputs ignore the end of a story: the fine-tune targets may have described the end, while the encoder never received it at eval.

## What I would change in a personal rerun

These are notes, not a roadmap, and they stay in docs (no silent rewrite of the course scripts):

- Convert and test both OPUS-MT directions; drop NLLB prefixes unless NLLB is actually used.
- Remove the `[:10]` slice; keep a `--limit` flag instead.
- Deduplicate the chunker into one module (the examples tree already has a stdlib port).
- Train and eval the same size; log generate kwargs next to metrics.
- Keep a 100-article human-spotcheck set even if the rest is silver.
- Set seeds.

## What the example corpus is for

The ten fiction articles exist so this repository can explain itself without the original dump or GPU weights. They are not a training set. If they ever look too clean compared with real North Jutland news, that is because they were written to be readable documentation, not a benchmark.
