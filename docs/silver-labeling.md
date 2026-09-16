# Silver-labeling method

The training signal in this project is **not** journalist-written Danish. It is a three-hop projection through English. This page is the method note I wish I had written in December 2023.

## The claim

Given unlabeled Danish news `x_da`:

1. Translate: `x_en = MT_da→en(x_da)`
2. Summarize in the resource-rich language: `s_en = Summ_en(x_en)`
3. Translate back: `s_da = MT_en→da(s_en)`
4. Train: `mT5(x_da) → s_da`

At test time there is no pivot. The student model must summarize Danish directly.

That is attractive for a course project because it separates *data creation* from *model training*, and because each hop is a downloadable checkpoint. It is also a stacked approximation to a task that Nordjylland already provides gold for. The scientific value is therefore not “we beat Alexandra Institute on TV2 Nord.” The value is “how much quality survives the pivot, and what does ROUGE on gold say about a model that never saw gold?”

## Why English, not a Danish summarizer

I considered training or prompting directly in Danish. In 2023 the obvious alternatives were:

| Alternative | Why I did not start there |
| --- | --- |
| Fine-tune mT5 on Nordjylland gold | That is the strong baseline. It answers a different question (supervised Danish summarization) and uses the same distribution I wanted as a *test* set. |
| Fine-tune on DaNewsroom | Also supervised, noisier, mixed extractive/abstractive. DanSumT5 already existed as a published line of work. |
| Zero-shot mT5 or GPT-style APIs | Course constraint plus I wanted a fully offline, reproducible (in theory) stack. |
| Danish extractive (LexRank / TextRank) | Different task; I wanted abstractive labels. |

English was the pivot because the news T5 I used (`mrm8488/t5-base-finetuned-summarize-news`) is a narrow, cheap specialist. I trusted it more on CNN/DailyMail-like English than I trusted a zero-shot multilingual model on Danish municipal news.

## What the pivot actually transfers

A silver summary is a composition of three behaviors:

1. **OPUS-MT da-en** prefers short, slightly normalized English. Named entities in Jutland place names and Danish compounds get flattened or mistranslated. Definite-article suffixes (`-en`, `-et`) disappear into English articles and may not come back cleanly.
2. **English news T5** was trained on a different journalism culture: inversion-heavy leads, US/UK entity style, 80-token budget, high repetition penalty. It is not trying to write a TV2 Nord “here is the news in one sentence” blurb.
3. **OPUS-MT en-da** re-Danish-izes whatever T5 emitted, including English hallucinations. Fluency can look high while facts are already wrong.

So `s_da` is “what an English news summarizer thought the English translation was about, said in Marian Danish.” That is a style, and it is not Nordjylland’s style.

## Error compounding

Write the gold Danish summary as `s*`. The student is trained toward `s_da`. The gaps:

```text
x_da  --MT-->  x_en     [omission, entity errors, register shift]
x_en  --T5-->  s_en     [hallucination, lead bias, length cap]
s_en  --MT-->  s_da     [further entity and morphology errors]
s_da  vs  s*            [domain and style mismatch at test]
```

ROUGE against `s*` therefore mixes *task difficulty* with *label shift*. A model can learn the silver style well (high silver-test ROUGE) and still score poorly on Nordjylland. The reverse is also possible: a conservative extractive-looking student might overlap Nordjylland’s often near-extractive blurbs more than a chatty T5 pivot does.

I did not run the diagnostic that would separate those effects: evaluate the silver labels themselves against Nordjylland on the subset of articles that appear in both corpora (if any). The 10k dump is not identified in git, so I cannot even say whether it *is* TV2 Nord text.

## Length and map-reduce

`summary.py` summarizes each 512-token pack and concatenates. Training then truncates labels at 128 SentencePiece tokens. Consequences:

- Long articles get multi-sentence silver labels that are stitched highlights, not a single abstract.
- `finetune.py` cuts those stitches at 128 tokens, so the student never sees the tail of a long silver label.
- Nordjylland summaries are short (card: 12–499 characters). The student may learn to be more verbose than the test references, which hurts ROUGE-L and can look like “the model rambles” in `use_model.py`.

If I reran the method I would add a second T5 pass over the concatenated sub-summaries, or sample only articles whose English side fits in 512 tokens, and I would set the student `max_length` from a percentile of *silver* label lengths, not from a copied 128.

## Why mT5 and not a Danish decoder-only model

Course default was encoder–decoder. mT5-large is the “we have one GPU and a weekend” multilingual summarizer. Decoder-only LLMs with Danish instruction following were less of a course-supported path in that offering. mT5 also makes ROUGE-in-the-Trainer straightforward: `predict_with_generate=True` and a `compute_metrics` hook.

The cost is that mT5-large plus `fp16` plus batch 8 plus 20 epochs is easy to overfit on a small silver set, and Adafactor at `3e-4` is a borrowed T5 recipe, not a sweep winner I can defend.

## Leakage and contamination

Two contamination questions I did not close:

1. **Train/eval article overlap.** If the 10k dump includes TV2 Nord pieces that sit in Nordjylland test, the student has seen the article (with a different summary). That is document-level leakage even if the labels differ.
2. **mT5 pretraining.** mT5 has seen Common Crawl-scale web text. A test article could in principle have been in pretraining. For a 2023 course project I accepted that; I would not use this setup to claim a new SOTA.

## Relation to published Danish summarization

Work I would cite if this were a paper, and that I used only as context, not as code:

- **DaNewsroom** (Varab & Schluter, LREC 2020): large Danish summarization set, mixed quality.
- **DanSumT5** (Kolding et al.): mT5 fine-tuned on a cleaned abstractive DaNewsroom slice; they report ROUGE and BERTScore plus human ranks, and they warn that automatic metrics still miss factual errors.
- **Nordjylland News** (Alexandra Institute): the gold set I pointed `eval.py` at.
- Later **ScandEval / EuroEval** summarization tasks moved the headline metric toward chrF-style scores with language penalties. My 2023 scripts do not implement that.

I am not claiming this student repo matches DanSum numbers. I never logged comparable intervals.

## What would falsify the method

I would call the pivot a failure if, after a clean rerun:

- silver labels are frequently not Danish (wrong-language outputs from the back-translation hop)
- BERTScore on Nordjylland is indistinguishable from an unfinetuned mT5-large baseline
- human spot-checks show systematic entity inversion (wrong town, wrong person) at a rate higher than “annoying but usable”

I would call it a *limited success* if the student is fluent and on-topic but more verbose and more English-news-shaped than TV2 Nord references. That is the outcome I subjectively remember from `use_model.py` printouts. Memory is not a result. The printouts were not committed.
