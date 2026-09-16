# Pipeline

The project builds a Danish news summarizer in two stages:

1. **Silver-label generation.** Unlabeled Danish articles are translated
   to English, summarized with an English news T5, then translated back
   to Danish. The result is a weakly supervised `body` / `summary` pair.
2. **Fine-tuning and evaluation.** Those pairs fine-tune multilingual T5
   (`google/mt5-large` in `finetune.py`). Held-out Nordjylland-News
   examples are used to inspect generations and compute ROUGE / BERTScore.

```
Danish article
    │
    ▼
translate.py          OPUS-MT da→en  (CTranslate2)
    │
    ▼
English article
    │
    ▼
summary.py            English T5 news summarizer
    │                 (long articles are packed into 512-token windows)
    ▼
English summary
    │
    ▼
translate_back.py     OPUS-MT en→da  (CTranslate2)
    │
    ▼
Danish silver summary  ──►  finetune.py  (mT5)
                              │
                              ▼
                         local checkpoint
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
              use_model.py           eval.py
              (qualitative)     (ROUGE + BERTScore)
```

## Stage 0 — Convert translation models

`Ctranslate_converter.py` wraps Hugging Face Transformers checkpoints in
[CTranslate2](https://github.com/OpenNMT/CTranslate2) so batch
translation is faster and uses less memory than a raw `generate()` loop.

The script on `main` only converts `Helsinki-NLP/opus-mt-en-da` into
`models/opus-mt-en-da_ct2`. `translate.py` also expects
`models/opus-mt-da-en_ct2`. Uncomment the da→en converter lines, or add
a second `TransformersConverter` call, before running the forward
translation step. See [limitations.md](limitations.md).

## Stage 1 — Danish → English

`translate.py` reads a CSV of raw articles (default
`10000_articles_without_linebreaks.csv` with columns `id` and
`article text`) and writes `translated_articles.csv` with:

| column | meaning |
| --- | --- |
| `id` | article identifier, copied through |
| `body` | original Danish text |
| `translated` | English pivot text |

Long articles are sentence-split with NLTK, then packed into windows of
about `0.9 * 512` tokenizer tokens so OPUS-MT is not fed truncated
mid-sentence blobs. Sentences that still exceed the window are broken on
commas, semicolons, or word boundaries (`split_long_sentence`).

## Stage 2 — English summarization

`summary.py` loads `mrm8488/t5-base-finetuned-summarize-news` and
summarizes the `translated` column. The same packing logic is reused
because the English T5 is capped at 512 tokens.

Generation settings in the script:

- `num_beams=2`
- `max_length=80` (filename also encodes this as `ml80`)
- `repetition_penalty=5.0` (`rp5.0`)
- `length_penalty=1.0`
- `early_stopping=True`

The checked-in script slices the frame to the first 10 rows
(`df[:10]`). Remove that slice for a full run. Output:

`summarized_file_ml80_rp5.0.csv` with `id`, `body`, `translated`, `summary`.

## Stage 3 — English → Danish

`translate_back.py` translates only the English `summary` column back to
Danish and drops the English columns. Output
`labeled_dataset_ml80_rp5.0.csv`:

| column | meaning |
| --- | --- |
| `id` | article identifier |
| `body` | original Danish article |
| `summary` | Danish silver summary |

`finetune.py` expects this schema, split into
`datasets/train_dataset.csv`, `datasets/validation_dataset.csv`, and
`datasets/test_dataset.csv`. The original scripts do not perform the
split; do that offline (for example a 90/5/5 shuffle with a fixed seed).

## Stage 4 — Fine-tune mT5

`finetune.py` tokenizes `body` → encoder (max 1024) and `summary` →
decoder labels (max 128), then trains `google/mt5-large` with Adafactor
for 20 epochs. The best checkpoint by ROUGE-1 mid F-measure is saved
under `./large_model`. Full hyper-parameters are in
[training.md](training.md).

`eval.py` and `use_model.py` load `small_model` and `google/mt5-small`.
If you only trained the large model, either point those scripts at
`./large_model` or run a second fine-tune with `google/mt5-small`.

## Stage 5 — Inspect and score

- `use_model.py` prints a handful of Nordjylland-News mini-set
  generations next to the reference summary.
- `eval.py` runs `Seq2SeqTrainer.evaluate()` with ROUGE and Danish
  BERTScore (`xlm-roberta-large`).

Neither script consumes the silver-label CSVs. They evaluate the
fine-tuned weights on a public Danish news benchmark, which is the
intended external check.

## What this pipeline is not

It is not a production training job. Paths, model names, batch sizes,
and even which model size is trained versus evaluated are hardcoded.
The [`examples/`](../examples/README.md) folder walks the *data*
transformations on a tiny fictional corpus so the method is visible
without a GPU.
