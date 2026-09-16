# Models and conversion

Four public checkpoints appear in the 2023 scripts. Only one of them is the
model this project actually trains.

## Helsinki-NLP OPUS-MT

| Direction | Hub id | CTranslate2 directory |
| --- | --- | --- |
| Danish → English | `Helsinki-NLP/opus-mt-da-en` | `models/opus-mt-da-en_ct2` |
| English → Danish | `Helsinki-NLP/opus-mt-en-da` | `models/opus-mt-en-da_ct2` |

These are Marian-style bilingual models. They are small enough to convert on a
CPU and fast enough under CTranslate2 to label thousands of articles.

`Ctranslate_converter.py` also contains commented converters for
`facebook/nllb-200-3.3B` and `facebook/nllb-200-distilled-600m`. That was an
abandoned alternative: NLLB is multilingual and would have used the
`eng_Latn` / `dan_Latn` prefixes that are still hard-coded in
`translate.py` and `translate_back.py`. The committed pipeline uses OPUS-MT.

Conversion is a one-off:

```bash
python Ctranslate_converter.py
```

The converter writes a CTranslate2 model directory next to a copy of the
tokenizer files. `ctranslate2.Translator(model_path, device=...)` then loads
that directory. The Hugging Face tokenizer is still used to turn text into
the token strings CTranslate2 expects
(`convert_ids_to_tokens(tokenizer.encode(...))`).

If conversion fails, the usual causes are:

- `transformers` and `ctranslate2` versions that no longer agree on Marian
  layer names. Pin the pair you used in 2023, or convert on the same machine
  you will run translation on.
- Disk. A converted OPUS-MT model is small; a converted NLLB-3.3B is not.
- The output directory already exists. `TransformersConverter.convert` will
  refuse to overwrite unless you pass the matching force flag.

## English news T5

`summary.py` uses `mrm8488/t5-base-finetuned-summarize-news`. It is a T5-base
checkpoint fine-tuned on English news, not a Danish model. That is why the
pipeline translates first.

The 512-token encoder limit is why articles are packed into windows. A
Danish feature piece that becomes three English windows produces three
English mini-summaries that are then concatenated. The silver target can
therefore be a *list* of ledes rather than a single abstract. Fine-tuning
inherits that style.

## mT5

`finetune.py` trains `google/mt5-large`. `eval.py` and `use_model.py` load
`google/mt5-small` as the *tokenizer* name and then load weights from
`small_model`. The split is historical: large was the training run, small
was the laptop-friendly checkpoint used to print examples.

mT5 is SentencePiece and multilingual. It can read Danish bodies without
the OPUS-MT hop, which is the entire reason to fine-tune it. Generation
settings baked into `AutoConfig` in `finetune.py`:

| Key | Value |
| --- | --- |
| `min_length` | 9 |
| `max_length` | 128 |
| `length_penalty` | 0.8 |
| `no_repeat_ngram_size` | 3 |
| `num_beams` | 4 |
| `dropout_rate` | 0.1 |

`length_penalty < 1` slightly prefers shorter outputs, which matches the
80-token English teacher.

## What is *not* trained

OPUS-MT and the English T5 are frozen teachers. Errors they make become
part of the silver target. Typical failure modes that then leak into mT5:

- Named entities that OPUS-MT transliterates or drops (Danish compounds,
  street names, party abbreviations).
- T5 summaries that invent a number that was only implied.
- Back-translation that restores a grammatical Danish sentence with a
  milder or stronger stance than the English lede.

`docs/limitations.md` lists the ones that showed up while reading outputs.
