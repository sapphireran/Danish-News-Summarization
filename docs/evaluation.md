# Evaluation

Two scripts look at the fine-tuned model. They use **different** public
datasets, **different** decoding settings, and (as checked in) expect
`small_model` even though `finetune.py` writes `large_model`.

## Qualitative — `use_model.py`

```bash
python use_model.py
```

Loads `ScandEval/nordjylland-news-summarization-mini` test, tokenizes
`input_text` / `target_text`, and prints up to five batches:

```
***** Input's Text *****
...Danish article...
***** Summary Text (True Value) *****
...reference...
***** Summary Text (Generated Text) *****
...model...
```

Decoding: `num_beams=2`, `no_repeat_ngram_size=1`, `max_length=128`.
`no_repeat_ngram_size=1` forbids repeating any unigram, which is an
aggressive constraint for Danish (articles and prepositions will
collide). If generations look oddly telegraphic, this is the first
knob to revert to `3` (the value used at train time).

Alignment caveat: the printed source article is `dataset[i]` while the
batch contains two examples. See [script_reference.md](script_reference.md).

## Quantitative — `eval.py`

```bash
python eval.py
```

Loads `alexandrainst/nordjylland-news-summarization` test (or fails if
column names are `text` / `summary` rather than `input_text` /
`target_text`; rename as described in [datasets.md](datasets.md)).

`compute_metrics`:

1. Decode predictions and labels (`-100` → pad, then skip specials).
2. `nltk.sent_tokenize` each string and join sentences with `\n`
   (the ROUGE-Lsum convention).
3. `datasets.load_metric("rouge")` with `use_aggregator=True`.
4. Report `rouge_{1,2,l,lsum}_mid_fmeasure` from the rouge-score
   `AggregateScore.mid.fmeasure` fields (exact key set depends on the
   metric version; the script iterates `rouge.items()`).
5. `datasets.load_metric("bertscore")` with `lang='da'` and
   `model_type="xlm-roberta-large"`.
6. Mean precision / recall / F1 over the eval set.

`dataloader_drop_last=True` with batch 64 silently drops a remainder
of up to 63 test articles. On a 4,178-row test set that is one batch
worth of rows. Set it to `False` for a complete score.

## What the numbers mean here

| Metric | Sensitive to | Weak at |
| --- | --- | --- |
| ROUGE-1 | unigram overlap with the TV2 Nord lede | paraphrase, synonym |
| ROUGE-2 | bigram fluency / extractive copying | short abstractive rewrites |
| ROUGE-L | longest common subsequence | word order that is valid but different |
| BERTScore (XLM-R) | token embedding similarity in Danish | factual hallucinations that are on-topic |

Silver-label training can inflate ROUGE against a style that does not
match TV2 Nord ledes. A model that copies the first sentence of the
body will often look decent on ROUGE-1 and weak on a human factuality
pass. BERTScore is not a factuality metric; it rewards semantic
nearness.

The English T5 stage is never scored. If you want to debug the
pipeline, score:

1. English T5 summaries against a small hand-written English reference
   set (not provided).
2. Back-translated Danish silver labels against Nordjylland-News
   references on the same article ids, if any overlap exists.
3. The fine-tuned mT5 against Nordjylland-News (what `eval.py` does).

A drop from (2) to (3) is underfitting; a high (2) and low (3) means
the silver style does not match the benchmark style.

## Lightweight stand-in

[`examples/rouge_lite.py`](../examples/rouge_lite.py) implements
ROUGE-1/2/L in the standard library so you can score the fictional
sample predictions without downloading `rouge-score` or XLM-R. It is
for teaching the metric, not for replacing `eval.py`.
