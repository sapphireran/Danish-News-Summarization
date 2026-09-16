# The four hops

```
Danish article
    │  hop 1   Helsinki-NLP/opus-mt-da-en  (CTranslate2)
    ▼
English article
    │  hop 2   mrm8488/t5-base-finetuned-summarize-news
    ▼
English summary          (one generate() per packed window, then join)
    │  hop 3   Helsinki-NLP/opus-mt-en-da  (CTranslate2)
    ▼
Danish silver summary    →  fine-tune google/mt5-large
```

Each hop can drop a fact. Names get transliterated. Numbers change
grouping (`1,2` / `1.2`). A "four metre wave" can become a "four-meter
wave" and then a "fire meter bølge" that no longer matches a ROUGE
reference written as `4 meter`.

## Why English in the middle

In 2023 the strongest cheap news summariser the scripts reach for is
English. Danish T5-class checkpoints were thinner. The bet: an English
summariser plus two OPUS hops beats training a Danish summariser from
scratch on a few hundred gold pairs.

The bet has a cost. The student model never sees a human Danish
summary during training. It sees whatever survived the triangle.

## Two bounds in the study kit

The kit cannot load OPUS-MT. It offers two stand-ins:

| bound | translator | summariser | meaning |
| --- | --- | --- | --- |
| **oracle** | gold parallel sentences | lead sentences + one per window | upper bound if translation were perfect |
| **gloss** | closed-world word list | same extractive rule on glossed English | lower bound / degraded hop |

A real OPUS+T5 run should land *between* these bounds on entity
retention. If a neural run drops more names than the gloss hop, the
pipeline is losing information that even a clumsy word list kept.

## What `summary.py` actually did

It did **not** summarise the whole article in one generate call.
It packed the English article into ≤512-piece windows (90 % guard),
called T5 on each window with `max_length=80` and
`repetition_penalty=5.0`, and concatenated the window summaries.

That is closer to "map a summariser over chunks" than to
"document-level abstractive summary". The kit's extractive hop copies
the chunk-then-join shape.
