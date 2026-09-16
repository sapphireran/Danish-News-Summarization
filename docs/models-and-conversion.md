# Models and conversion

Three model families appear in this project. They do different jobs and are not interchangeable.

## 1. Helsinki-NLP OPUS-MT (round-trip translation)

| Direction | Hugging Face id | CTranslate2 directory expected by scripts |
| --- | --- | --- |
| Danish → English | `Helsinki-NLP/opus-mt-da-en` | `models/opus-mt-da-en_ct2` |
| English → Danish | `Helsinki-NLP/opus-mt-en-da` | `models/opus-mt-en-da_ct2` |

These are MarianMT models trained on OPUS bitext. They are small enough to convert with CTranslate2 and fast enough to push ~10k news articles through on one GPU.

### Why CTranslate2

The 2023 labeling run translated every sentence pack of every article twice (out and back). Hugging Face `generate` on MarianMT is correct but slow. CTranslate2 rewrites the weights into a runtime that batches well and uses fewer dependencies at inference time.

`Ctranslate_converter.py` is a thin wrapper:

```python
from ctranslate2.converters import TransformersConverter
converter = TransformersConverter("Helsinki-NLP/opus-mt-en-da")
converter.convert("models/opus-mt-en-da_ct2")
```

Conversion downloads the Transformers checkpoint, then writes a directory with `model.bin` (or a quantized variant) plus CTranslate2 config files. The tokenizer is **not** stored in a form the rest of the scripts use. Both `translate.py` and `translate_back.py` still load the tokenizer from Hugging Face (`AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-...")`).

You therefore need network access (or a populated Hugging Face cache) even after conversion.

### Quantization

The converter is called with defaults. If disk or VRAM is tight, reconvert with an explicit quantization (for example `int8` or `float16`) via the CTranslate2 CLI. The Python scripts do not pass a compute type into `ctranslate2.Translator(...)` beyond `device="cuda"|"cpu"`.

### Language-prefix leftover

`translate.py` and `translate_back.py` build `target_prefixes = [[tgt_lang] ...]` with `eng_Latn` / `dan_Latn`. Those strings are NLLB language codes. OPUS-MT decoders do not expect them. On a rerun, drop `target_prefix` entirely for OPUS-MT, or switch the converter *and* the tokenizers to an NLLB checkpoint.

## 2. English news T5 (silver summarizer)

**id:** `mrm8488/t5-base-finetuned-summarize-news`

This is a T5-base checkpoint fine-tuned on English news summarization. It is used only in `summary.py` and only on the **translated** English text.

It is not multilingual. Feeding it Danish `body` text produces garbage. That is why the pipeline is pivot-through-English rather than “just run T5 on Danish.”

Generation settings used in the script:

| Argument | Value | Why it is there |
| --- | --- | --- |
| `num_beams` | 2 | Cheap beam search |
| `max_length` | 80 | Short news lede; encoded in the output filename |
| `repetition_penalty` | 5.0 | Aggressive; T5 news models loop on names otherwise |
| `length_penalty` | 1.0 | Neutral |
| `early_stopping` | True | Stop when all beams hit EOS |

`max_length=80` is tokens, not words. A long article that was split into four 512-token English chunks can still produce ~320 tokens of English summary before back-translation.

## 3. mT5 (the model you actually keep)

| Script | Hugging Face id | Local weights |
| --- | --- | --- |
| `finetune.py` | `google/mt5-large` | writes `./large_model` |
| `use_model.py` | tokenizer from `google/mt5-small` | reads `./small_model` |
| `eval.py` | tokenizer from `google/mt5-small` | reads `./small_model` |

mT5 is multilingual T5. Danish is in the pretrain mix, so the fine-tune can stay in Danish on both the encoder and the decoder.

The **size mismatch** between training (`large`) and the eval/demo scripts (`small` tokenizer + `small_model` directory) is real. Possible 2023 interpretations:

- A cheaper `mt5-small` run was used for inspection, and `mt5-large` was the long job.
- Directory names were never updated after a size experiment.

Tokenizers for `mt5-small` and `mt5-large` share the SentencePiece vocabulary in practice, but do not rely on that. Load the tokenizer from the same directory you load the weights from.

### Generation config baked into training

`finetune.py` builds an `AutoConfig` with:

| Field | Value |
| --- | --- |
| `min_length` | 9 |
| `max_length` | 128 |
| `length_penalty` | 0.8 |
| `no_repeat_ngram_size` | 3 |
| `num_beams` | 4 |
| `dropout_rate` | 0.1 |

`use_model.py` ignores that config and generates with `num_beams=2`, `no_repeat_ngram_size=1`, `max_length=128`. Qualitative prints are therefore not the same decode the trainer used at eval time.

## 4. BERTScore encoder (eval only)

`eval.py` asks BERTScore for `lang='da'` and `model_type="xlm-roberta-large"`. That downloads a separate model the first time you evaluate. It is not used for generation.

## Models that were tried and left commented

In `Ctranslate_converter.py`:

- `facebook/nllb-200-3.3B`
- `facebook/nllb-200-distilled-600m`

NLLB would have justified the `dan_Latn` / `eng_Latn` prefixes. It was heavier than OPUS-MT and was not wired through `summary.py` / `finetune.py`.

## Disk sketch (order of magnitude)

These are not measured on this machine; they are the sizes you should plan for before downloading.

| Artifact | Rough size |
| --- | --- |
| Each OPUS-MT Transformers checkpoint | ~300 MB |
| Each OPUS-MT CTranslate2 directory (fp32) | similar, smaller if quantized |
| `mrm8488/t5-base-finetuned-summarize-news` | ~900 MB |
| `google/mt5-small` | ~1.2 GB |
| `google/mt5-large` | ~5 GB |
| Fine-tuned `./large_model` | same order as mT5-large |
| `xlm-roberta-large` for BERTScore | ~2 GB |
| 10k-article CSV + intermediates | tens to hundreds of MB |

## Offline examples

The scripts in [`../examples`](../examples) do **not** load any of these checkpoints. They reimplement the sentence-packing logic and a stub pivot so the CSV schemas can be exercised without a GPU or a Hugging Face login.
