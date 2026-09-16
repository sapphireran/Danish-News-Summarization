# Models

Four model families appear in the course scripts. They are not
interchangeable, and the tokenizer name passed to `from_pretrained` has
to match the checkpoint you actually load.

## OPUS-MT (Helsinki-NLP)

| Direction | Hugging Face id | Used in |
| --- | --- | --- |
| Danish → English | `Helsinki-NLP/opus-mt-da-en` | `translate.py` |
| English → Danish | `Helsinki-NLP/opus-mt-en-da` | `translate_back.py`, `Ctranslate_converter.py` |

These are MarianMT models trained on OPUS bitext. They use their own
sentence-piece vocabularies. They do **not** take NLLB language codes
(`dan_Latn`, `eng_Latn`). The course scripts still pass `src_lang=` into
`AutoTokenizer.from_pretrained` and `target_prefix=[tgt_lang]` into
CTranslate2. That prefix API is what you want for NLLB; for OPUS-MT the
target prefix is typically unused or harmful. If you revive the GPU path,
drop the language-code prefixes unless you switch the converter to NLLB.

Commented-out converter lines in `Ctranslate_converter.py` mention:

* `facebook/nllb-200-3.3B`
* `facebook/nllb-200-distilled-600m`

Those would need the NLLB language prefixes. They were an experiment, not
the path `translate.py` is wired to.

## CTranslate2

`TransformersConverter` rewrites a Transformers checkpoint into a CTranslate2
directory (`model.bin` + config + vocabulary). Runtime loading:

```python
translator = ctranslate2.Translator(model_path, device="cuda" or "cpu")
source_tokens = [tokenizer.convert_ids_to_tokens(tokenizer.encode(sentence))]
results = translator.translate_batch(source_tokens, target_prefix=...)
```

Reasons this project used CT2:

* faster batch translation than `model.generate` for 10k articles
* smaller memory footprint than keeping two MarianMT models in PyTorch
* the conversion is one-off (`Ctranslate_converter.py`)

## English news T5

`summary.py` uses `mrm8488/t5-base-finetuned-summarize-news`. That
checkpoint expects English. It is the reason the pipeline pivots at all:
the summarizer is not multilingual. Generation hyperparameters are stored
in the output filename (`ml80` = `max_length=80`, `rp5.0` =
`repetition_penalty=5.0`). A penalty of 5.0 is aggressive; it reduces
loops on news copy but can drop repeated proper names.

The model is still a 512-token T5. Long English articles are windowed and
the window summaries are concatenated. That can produce a silver label
that is a *list of local summaries* rather than one global abstract.

## mT5

| Script | Tokenizer / config name | Weights loaded |
| --- | --- | --- |
| `finetune.py` | `google/mt5-large` | `google/mt5-large`, then `./large_model` |
| `use_model.py` | `google/mt5-small` | `small_model` |
| `eval.py` | `google/mt5-small` | `small_model` |

mT5 is the multilingual T5 trained on mC4. Danish is in that mix, which
is why it was the fine-tune target instead of a Danish-only encoder.

The small/large split is a real inconsistency: inspection and evaluation
will not reflect the large run unless you change those paths. A local
`small_model` directory is also not in git; you have to produce it with a
separate fine-tune or a renamed checkpoint.

Relevant `finetune.py` generation config (passed through `AutoConfig`):

* `min_length=9`, `max_length=128`
* `length_penalty=0.8`
* `no_repeat_ngram_size=3`
* `num_beams=4`
* `dropout_rate=0.1`

Training: 20 epochs, learning rate `3e-4`, Adafactor, polynomial
scheduler, 1000 warmup steps, `fp16=True`, `per_device_train_batch_size=8`.
`fp16` plus Adafactor on mT5 can be numerically noisy; if loss goes to
NaN, retry in bf16 or fp32.

## What the CPU package does not load

`danish_news.glossary.GlossaryBackend` is a deterministic phrase table for
the eight fixture articles. It implements the same `translate_da_en` /
`summarize_en` / `translate_en_da` surface as the GPU scripts so
`danish_news.pipeline.run_pivot` can be demonstrated. It is not a stand-in
for OPUS-MT quality.
