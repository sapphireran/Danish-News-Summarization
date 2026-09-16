# Project overview

This repository is a personal final project from ITU's *Advanced Natural
Language Processing and Deep Learning* course (2023). The goal was a Danish
news summariser at a time when high-quality Danish abstractive labels were
scarce and a full mT5 training run still fitted on a single university GPU.

The bet was simple: English summarisation checkpoints were already decent, and
Helsinki-NLP OPUS-MT already covered Danish↔English. If those two systems were
chained, a large dump of unlabelled Danish articles could be turned into
*silver* Danish summaries. A multilingual seq2seq model could then be
fine-tuned to map Danish body → Danish summary directly, so inference would not
need the translation hop.

```
Danish article
    │
    ▼
OPUS-MT da→en   (CTranslate2)
    │
    ▼
English T5 news summariser
    │
    ▼
OPUS-MT en→da   (CTranslate2)
    │
    ▼
silver (body, summary) pairs
    │
    ▼
fine-tune google/mt5-large
    │
    ▼
evaluate on Nordjylland News (human labels)
```

Held-out evaluation does **not** use the silver labels. `eval.py` and
`use_model.py` read
[`alexandrainst/nordjylland-news-summarization`](https://huggingface.co/datasets/alexandrainst/nordjylland-news-summarization)
and the smaller ScandEval mini split. That keeps the automatic labels in the
training loop and the human labels in the score loop.

## Repository map

| Path | Role |
| --- | --- |
| `Ctranslate_converter.py` | Convert Helsinki OPUS-MT weights to CTranslate2 |
| `translate.py` | Danish bodies → English |
| `summary.py` | English bodies → English summaries |
| `translate_back.py` | English summaries → Danish summaries |
| `finetune.py` | Fine-tune mT5 on the silver CSV splits |
| `use_model.py` | Print a few generations from a local checkpoint |
| `eval.py` | ROUGE + Danish BERTScore on Nordjylland News |
| `danish_news_sum/` | Offline helpers used by docs and examples |
| `examples/` | Invented fixtures and walkthrough scripts |
| `docs/` | This note series |

The 2023 scripts are still the source of truth for a full run. The package
under `danish_news_sum/` extracts the packing algorithm, the CSV checks, and a
lexical stand-in for ROUGE so the documentation can be executed without a GPU.

## Design choices that are easy to miss

1. **Summarise in English, not Danish.** The project did not start from a
   Danish abstractive model. It borrowed an English news T5
   (`mrm8488/t5-base-finetuned-summarize-news`) and paid the translation tax
   twice.
2. **Keep the original Danish body.** Only the *summary* is back-translated.
   Fine-tuning therefore sees real Danish source text paired with a noisy
   Danish target, which is closer to inference than training on translated
   bodies.
3. **Evaluate on a different dataset.** Nordjylland News is regional journalism
   with human summaries. Domain shift is expected and is part of the point:
   if the silver pipeline only memorised its own translationese, the
   Nordjylland numbers would collapse.
4. **CTranslate2 for the hops, Transformers for mT5.** Translation is a
   throughput problem (thousands of articles, 512-token windows). Fine-tuning
   is a modelling problem (Adafactor, beam search, ROUGE as the selection
   metric).

## What "done" looked like in 2023

A finished personal run produced:

- `models/opus-mt-da-en_ct2` and `models/opus-mt-en-da_ct2`
- `translated_articles.csv`
- `summarized_file_ml80_rp5.0.csv`
- `labeled_dataset_ml80_rp5.0.csv`
- `datasets/{train,validation,test}_dataset.csv`
- `./large_model` or `./small_model`
- a printed dict from `eval.py` with `rouge_*_mid_fmeasure` and
  `bertscore_{precision,recall,f1}`

Those artifacts are intentionally gitignored. The committed
`examples/data/*.csv` files are tiny, hand-written stand-ins for the same
schemas.
