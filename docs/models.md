# Models and hyperparameters

Three model families appear in the 2023 scripts. They are not interchangeable: each stage owns one.

## 1. OPUS-MT (labeling translation)

| Direction | Hugging Face id | CTranslate2 directory |
| --- | --- | --- |
| Danish → English | `Helsinki-NLP/opus-mt-da-en` | `models/opus-mt-da-en_ct2` |
| English → Danish | `Helsinki-NLP/opus-mt-en-da` | `models/opus-mt-en-da_ct2` |

These are MarianMT bilingual models, not NLLB. Typical properties:

- Sentencepiece tokenizer with a practical limit around 512 tokens.
- Fast after CTranslate2 conversion, which is why labeling uses `ctranslate2.Translator`.
- Quality is solid on clean news prose and weaker on slang, code-switching, and very long compounds.

`Ctranslate_converter.py` also contains commented converters for `facebook/nllb-200-3.3B` and `facebook/nllb-200-distilled-600m`. The labeling scripts still pass Flores-style `dan_Latn` / `eng_Latn` prefixes, which is an NLLB habit. If you revive NLLB, those prefixes become meaningful. On OPUS-MT they are an experiment leftover.

### Conversion

```python
from ctranslate2.converters import TransformersConverter
TransformersConverter("Helsinki-NLP/opus-mt-en-da").convert("models/opus-mt-en-da_ct2")
```

Convert both directions before a full labeling run. See [known-issues.md](known-issues.md).

## 2. English news T5 (silver summaries)

| Field | Value |
| --- | --- |
| id | `mrm8488/t5-base-finetuned-summarize-news` |
| Task | English abstractive news summarization |
| Encoder window in `summary.py` | 512 |
| `max_length` | 80 |
| `num_beams` | 2 |
| `repetition_penalty` | 5.0 |
| `length_penalty` | 1.0 |
| `early_stopping` | True |

`repetition_penalty=5.0` is aggressive. It reduces loops (“the mayor said the mayor said”) and can also delete repeated but legitimate named entities. If silver summaries look oddly entity-poor, try 1.5–2.5 before changing anything else.

Chunk-then-summarize means the model never sees the full English article when the story is long. Discourse-level compression (drop the whole second half) cannot happen inside one generate call.

## 3. mT5 (the model you actually train)

| Script | Base checkpoint | Local weights |
| --- | --- | --- |
| `finetune.py` | `google/mt5-large` | writes `./large_model` |
| `use_model.py` | `google/mt5-small` tokenizer + `small_model` weights | reads `small_model` |
| `eval.py` | `google/mt5-small` tokenizer + `small_model` weights | reads `small_model` |

The 2023 training run used large. The checked-in eval/inspect scripts assume a later or alternate small checkpoint named `small_model`. Point those scripts at `large_model` if that is what you trained.

### Fine-tune `Seq2SeqTrainingArguments`

Values from `finetune.py`:

| Argument | Value |
| --- | --- |
| `num_train_epochs` | 20 |
| `learning_rate` | `3e-4` |
| `lr_scheduler_type` | `polynomial` |
| `warmup_steps` | 1000 |
| `optim` | `adafactor` |
| `weight_decay` | 0.01 |
| `per_device_train_batch_size` | 8 |
| `per_device_eval_batch_size` | 8 |
| `gradient_accumulation_steps` | 1 |
| `evaluation_strategy` | `epoch` |
| `save_strategy` | `epoch` |
| `predict_with_generate` | True |
| `generation_max_length` | 128 |
| `fp16` | True |
| `load_best_model_at_end` | True |
| `metric_for_best_model` | `rouge_1_mid_fmeasure` |
| `save_total_limit` | 1 |
| `push_to_hub` | False |

Adafactor + a relatively high `3e-4` is a common T5 recipe. Twenty epochs on a large silver set can overfit fluency of the pivot summaries (the model learns “how OPUS-MT + T5 phrase Danish”) rather than how journalists write ledes. Early stopping on validation ROUGE-1 is the guardrail.

### Generation config baked into `AutoConfig`

`finetune.py` writes these onto the config object before `from_pretrained`:

| Key | Value |
| --- | --- |
| `min_length` | 9 |
| `max_length` | 128 |
| `length_penalty` | 0.8 |
| `no_repeat_ngram_size` | 3 |
| `num_beams` | 4 |
| `dropout_rate` | 0.1 |

`length_penalty=0.8` slightly prefers shorter outputs. Combined with `min_length=9` you should not get empty decodes, but you can get single-sentence stubs.

`use_model.py` does **not** reuse that config. It generates with `num_beams=2`, `no_repeat_ngram_size=1`, `max_length=128`. Qualitative prints are therefore not the same as the training-time generate settings.

## Tokenization limits

| Text | Tokenizer | Max length |
| --- | --- | --- |
| Danish / English article at labeling | OPUS-MT or news T5 | 512, packed in chunks of 460 |
| Danish article at train/eval | mT5 | 1024 |
| Danish summary at train | mT5 | 128 |
| Danish summary at `use_model.py` tokenize | mT5 | 180 (labels only) |
| Decode at train | mT5 generate | 128 |

The 180 vs 128 mismatch in `use_model.py` only affects how gold labels are tokenized for display, not the generate cap.

## Device

Every root script picks `cuda` if `torch.cuda.is_available()` else `cpu`. CTranslate2 gets the same string. Fine-tuning `mt5-large` with `fp16=True` and batch size 8 needs a roomy GPU (course machines were in that class). The example scripts never import `torch`.

## What to download vs what to train

You download:

- OPUS-MT da↔en (then convert)
- `mrm8488/t5-base-finetuned-summarize-news`
- `google/mt5-large` or `google/mt5-small`
- At eval time, `xlm-roberta-large` via BERTScore (`lang='da'`)

You train:

- The mT5 summarizer on silver pairs

You do not train OPUS-MT or the English T5 in this repo.
