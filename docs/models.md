# Models

Three families of checkpoints appear in the course scripts: bilingual OPUS-MT
for translation, an English news T5 for silver labels, and multilingual mT5
for the actual Danish summarizer.

## Translation — Helsinki-NLP OPUS-MT + CTranslate2

| Direction | Hugging Face id | Expected local directory |
| --- | --- | --- |
| Danish → English | `Helsinki-NLP/opus-mt-da-en` | `models/opus-mt-da-en_ct2` |
| English → Danish | `Helsinki-NLP/opus-mt-en-da` | `models/opus-mt-en-da_ct2` |

`Ctranslate_converter.py` converts a Transformers checkpoint to CTranslate2
with `TransformersConverter(...).convert(output_dir)`. CTranslate2 is used
because the 10k-article dump is long enough that a Python `generate()` loop
over vanilla Transformers is painfully slow on a single student GPU.

The converter file currently enables only the English→Danish model. Uncomment
the Danish→English block before running `translate.py`, or run a second
conversion by hand:

```python
from ctranslate2.converters import TransformersConverter

TransformersConverter("Helsinki-NLP/opus-mt-da-en").convert("models/opus-mt-da-en_ct2")
TransformersConverter("Helsinki-NLP/opus-mt-en-da").convert("models/opus-mt-en-da_ct2")
```

Tokenizers are still loaded from Hugging Face, not from the CTranslate2
directory:

| Script | `AutoTokenizer.from_pretrained(...)` |
| --- | --- |
| `translate.py` | `Helsinki-NLP/opus-mt-da-en` |
| `translate_back.py` | `Helsinki-NLP/opus-mt-en-da` |

Both scripts pass `src_lang` into `from_pretrained` and build
`target_prefix` lists such as `[["eng_Latn"]]`. Those language codes belong
to NLLB-style models. OPUS-MT does not use them the same way. The converter
file also has commented NLLB 600M / 3.3B experiments, which is likely where
the prefixes came from. If translations look like they start with a stray
language token, inspect the first decoded token before keeping a full run.

Device selection is `cuda` if `torch.cuda.is_available()` else `cpu`, passed
straight into `ctranslate2.Translator`.

## English summarizer — T5 news

| Field | Value in `summary.py` |
| --- | --- |
| Checkpoint | `mrm8488/t5-base-finetuned-summarize-news` |
| Task | English news summarization |
| Encoder budget | 512 tokens (articles are chunked first) |
| Decoder `max_length` | 80 |
| `repetition_penalty` | 5.0 |
| Beams | 2 |

This model is only used to manufacture labels. It never sees Danish text.
Chunk-then-concatenate means a long article can produce a summary that is
several 80-token pieces glued together, which is longer than the 128-token
label limit used later in `finetune.py`.

## Danish summarizer — mT5

| Script | Base checkpoint | Local weights |
| --- | --- | --- |
| `finetune.py` | `google/mt5-large` | writes `./large_model` |
| `use_model.py` | tokenizer from `google/mt5-small` | reads `small_model` |
| `eval.py` | tokenizer from `google/mt5-small` | reads `small_model` |

The course work tried more than one mT5 size. The training script is wired
for **large**. The inspection and evaluation scripts are wired for a local
directory named `small_model`. If you only train the large run, either point
those two scripts at `./large_model` or keep a separate small run.

`finetune.py` builds an `AutoConfig` overlay before `from_pretrained`:

| Config key | Value | Role |
| --- | --- | --- |
| `min_length` | 9 | Avoid near-empty summaries |
| `max_length` | 128 | Match label truncation |
| `length_penalty` | 0.8 | Mild preference for shorter outputs |
| `no_repeat_ngram_size` | 3 | Reduce copied phrases |
| `num_beams` | 4 | Train-time generation for metrics |
| `dropout_rate` | 0.1 | Regularization |

`use_model.py` does not reuse that config. It calls `model.generate` with
`num_beams=2`, `no_repeat_ngram_size=1`, and `max_length=128`. Qualitative
prints are therefore not identical to the trainer's generation settings.

## Checkpoints that should stay off git

These directories are large and local:

```text
models/opus-mt-da-en_ct2/
models/opus-mt-en-da_ct2/
mt5-summarize-large/
large_model/
small_model/
```

A `.gitignore` in the repo root keeps them from being added by accident.
