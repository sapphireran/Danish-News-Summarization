# Models

Four families appear in the root scripts. They are not interchangeable.
This page records *which checkpoint is used where* and the pitfalls that
are already visible in the checked-in code.

## 1. Helsinki-NLP OPUS-MT (translation)

| Direction | Hub id | CTranslate2 directory | Used by |
| --- | --- | --- | --- |
| Danish → English | `Helsinki-NLP/opus-mt-da-en` | `models/opus-mt-da-en_ct2` | `translate.py` |
| English → Danish | `Helsinki-NLP/opus-mt-en-da` | `models/opus-mt-en-da_ct2` | `translate_back.py` |

Convert with CTranslate2 so batch translation stays on the GPU without
paying the full Transformers generate() overhead:

```bash
python Ctranslate_converter.py
```

**The file as committed only converts en→da.** The da→en, NLLB 600M, and
NLLB 3.3B lines are commented out. For the published workflow you need
at least both OPUS directions.

`translate.py` still constructs `target_prefix=[[tgt_lang]]` with
`eng_Latn` / `dan_Latn`. Those prefixes are an NLLB convention. OPUS-MT
Marian models do **not** expect a language-token prefix the same way.
If translations look like they start with a mystery token or a repeated
language tag, strip the prefix logic when you run OPUS, or switch the
converter back to NLLB and keep the prefixes.

Tokenizer construction uses `src_lang=...` and the deprecated
`use_auth_token=False`. On current `transformers` you want
`token=False` (or nothing) and you can drop `src_lang` for OPUS-MT.

## 2. English news T5 (silver summaries)

`summary.py` loads:

```
mrm8488/t5-base-finetuned-summarize-news
```

Generation defaults copied from the script:

| kwarg | value | why it is there |
| --- | --- | --- |
| `num_beams` | 2 | cheap beam search |
| `max_length` | 80 | short news dek, matches the output filename |
| `repetition_penalty` | 5.0 | very aggressive; will also kill legitimate repetition |
| `length_penalty` | 1.0 | neutral |
| `early_stopping` | True | stop when all beams hit EOS |

A `repetition_penalty` of 5.0 is high. If summaries become telegraphic
("City opens street. Trial lasts months.") try 1.5–2.2 before you blame
the translator.

Long articles are split with the shared chunker; each window is
summarized independently and the strings are joined with a space. There
is no second-pass "summarize the summaries". For a 3–4 window feature
that produces a stitched list of dek-length sentences, not one coherent
abstract.

## 3. mT5 (the model you actually keep)

`finetune.py` fine-tunes `google/mt5-large` and writes `./large_model`.

`use_model.py` and `eval.py` load **`small_model/`** and construct a
tokenizer from `google/mt5-small`.

That split is historical (large for training, small for a laptop demo)
but it is also a footgun: evaluating a large checkpoint with a small
tokenizer, or the other way around, yields fluent garbage. Align them:

```text
finetune.py   model_name = "google/mt5-large"   →  ./large_model
eval.py       tokenizer + weights from the same size
use_model.py  same
```

mT5 generation config set in `finetune.py`:

| key | value |
| --- | --- |
| `min_length` | 9 |
| `max_length` | 128 |
| `length_penalty` | 0.8 |
| `no_repeat_ngram_size` | 3 |
| `num_beams` | 4 |
| `dropout_rate` | 0.1 |

`use_model.py` *overrides* some of that at generate() time (`num_beams=2`,
`no_repeat_ngram_size=1`, `max_length=128`). Qualitative examples from
that script are therefore not the same as `trainer.evaluate()` output.

## 4. BERTScore backbone (metrics only)

`eval.py` asks BERTScore for `lang='da'` and
`model_type="xlm-roberta-large"`. That download is separate from mT5
and is the usual reason a "quick eval" sits on `from_pretrained` for
several minutes the first time.

## Disk and GPU ballpark

These are order-of-magnitude figures for planning, not promises:

| artifact | rough disk | rough VRAM to *run* |
| --- | --- | --- |
| OPUS-MT CT2 pair | 300–600 MB | 2–4 GB |
| English T5 base | ~900 MB | 4–6 GB |
| mT5-small | ~1.2 GB | 8 GB (eval) |
| mT5-large + Adam/Adafactor | ~5–8 GB weights | 16–24 GB (train, batch 8, fp16) |
| xlm-roberta-large (BERTScore) | ~2 GB | 8 GB |

`finetune.py` sets `fp16=True`. That flag is a no-op or a crash on
CPU-only machines. Use the examples if you do not have a GPU; they
never import `torch`.

## Conversion checklist

1. Uncomment the da→en converter block.
2. Confirm the output directories match `model_path` in `translate.py`
   and `translate_back.py` (`models/opus-mt-da-en_ct2` vs
   `models/opus-mt-en-da_ct2`).
3. Run a three-sentence smoke translation in both directions before
   starting the 10k-article loop.
4. Keep the original Transformers checkpoints until you have compared
   a handful of CT2 vs. Transformers strings. CTranslate2 quantization
   is off by default in the converter call; do not add `int8` until
   that smoke test is clean.
