# Script reference

All paths are relative to the repository root. Values below are the
hardcoded defaults in the 2023 files, not recommended production
settings.

## `Ctranslate_converter.py`

Converts a Transformers Marian checkpoint to CTranslate2.

| | |
| --- | --- |
| Reads | `Helsinki-NLP/opus-mt-en-da` from the Hub |
| Writes | `models/opus-mt-en-da_ct2` |
| Commented | NLLB 3.3B, NLLB 600M, `opus-mt-da-en` |
| CLI | none; edit the file |

## `translate.py`

Danish article → English article.

| | |
| --- | --- |
| Reads | `10000_articles_without_linebreaks.csv` (`id`, `article text`) |
| Model | `models/opus-mt-da-en_ct2` + tokenizer `Helsinki-NLP/opus-mt-da-en` |
| Writes | `translated_articles.csv` (`id`, `body`, `translated`) |
| Window | 512 Marian tokens, pack at 90% |
| Extra | downloads NLTK `punkt` on first run |

## `summary.py`

English article → English summary.

| | |
| --- | --- |
| Reads | `translated_articles.csv` |
| Model | `mrm8488/t5-base-finetuned-summarize-news` |
| Writes | `summarized_file_ml80_rp5.0.csv` |
| Slice | **first 10 rows only** (`df[:10]`) |
| Generate | beams 2, max length 80, repetition penalty 5.0 |

## `translate_back.py`

English summary → Danish silver summary.

| | |
| --- | --- |
| Reads | `summarized_file_ml80_rp5.0.csv` |
| Model | `models/opus-mt-en-da_ct2` + tokenizer `Helsinki-NLP/opus-mt-en-da` |
| Writes | `labeled_dataset_ml80_rp5.0.csv` (`id`, `body`, `summary`) |
| Note | passes NLLB language prefixes into an OPUS decoder |

## `finetune.py`

Supervised mT5 fine-tune on the silver labels.

| | |
| --- | --- |
| Reads | `datasets/{train,validation,test}_dataset.csv` (`id`, `body`, `summary`) |
| Model | `google/mt5-large` |
| Writes | trainer dir `mt5-summarize-large`, final copy `./large_model` |
| Train | 20 epochs, Adafactor, lr `3e-4`, fp16, batch 8 |
| Select | best `rouge_1_mid_fmeasure`, `save_total_limit=1` |

The test split is loaded into the `DatasetDict` but never passed to
`Seq2SeqTrainer`. Only `train` and `validation` are used.

## `use_model.py`

Qualitative generations on the ScandEval mini set.

| | |
| --- | --- |
| Reads | `ScandEval/nordjylland-news-summarization-mini` test split |
| Model | tokenizer `google/mt5-small`, weights `small_model` |
| Writes | stdout (5 batches of size 2 by default) |
| Generate | beams 2, `no_repeat_ngram_size=1`, max length 128 |

The printed “input text” uses `split_dataset["test"]["input_text"][i]`,
i.e. dataset row `i`, while predictions come from dataloader batch `i`.
Those line up only while `batch_size=2` *and* you remember that each
loop step shows **the first sequence in the batch** next to
**dataset row i**, not dataset row `2*i`. Treat the printout as a
smoke test, not a aligned error analysis.

## `eval.py`

Corpus-level ROUGE and BERTScore.

| | |
| --- | --- |
| Reads | `alexandrainst/nordjylland-news-summarization` test split |
| Model | tokenizer `google/mt5-small`, weights `small_model` |
| Writes | stdout metrics dict |
| Batch | eval batch 64, `dataloader_drop_last=True` |
| Metrics | ROUGE mid F1 + BERTScore P/R/F1 (`xlm-roberta-large`, `lang='da'`) |

`training_args.output_dir` is `mt5-summarize-large` even though the
loaded weights are `small_model`. That directory is unused during
`trainer.evaluate()` except as a Trainer placeholder.

## Dependency graph

```
Ctranslate_converter.py
        │
        ├──► translate.py ──► summary.py ──► translate_back.py
        │                                              │
        │                                              ▼
        │                                        (manual split)
        │                                              │
        │                                              ▼
        │                                         finetune.py
        │                                              │
        │                         ┌────────────────────┴─────────┐
        │                         ▼                              ▼
        │                    large_model                    (not loaded
        │                                                    by eval)
        └──► (da→en convert is commented)

Hub: nordjylland-news-* ──► use_model.py
                         └──► eval.py  (expects small_model)
```
