# Models

Four model families appear in the scripts. Only two of them are trained here (mT5 small/large). The translation and English summarization models are used off the shelf.

## Helsinki-NLP OPUS-MT

| Direction | Hugging Face id | Used by | CTranslate2 folder |
| --- | --- | --- | --- |
| Danish → English | `Helsinki-NLP/opus-mt-da-en` | `translate.py` | `models/opus-mt-da-en_ct2` |
| English → Danish | `Helsinki-NLP/opus-mt-en-da` | `translate_back.py`, `Ctranslate_converter.py` | `models/opus-mt-en-da_ct2` |

These are bilingual Marian checkpoints. They expect SentencePiece-like tokens from their own tokenizer. They are not NLLB and do not need a language-pair code in the same way `facebook/nllb-200-*` does.

The converter file still has NLLB 3.3B and distilled 600M lines commented out. An earlier experiment likely tried a single many-to-many model for both directions. The submitted pipeline settled on the smaller OPUS-MT pair.

### Why CTranslate2

`ctranslate2.Translator` is a C++ runtime with faster batch decoding than a naive `model.generate` loop over 10k articles. Conversion is:

```python
from ctranslate2.converters import TransformersConverter

TransformersConverter("Helsinki-NLP/opus-mt-da-en").convert("models/opus-mt-da-en_ct2")
TransformersConverter("Helsinki-NLP/opus-mt-en-da").convert("models/opus-mt-en-da_ct2")
```

The checked-in `Ctranslate_converter.py` only runs the second line. Enable the first before `translate.py`.

Device selection in the translation scripts:

```python
ctranslate2.Translator(model_path, device="cuda" if torch.cuda.is_available() else "cpu")
```

Tokenizer loading still goes through Transformers so encoding stays compatible with the converted graph.

### Language-token leftovers

Both `translate.py` and `translate_back.py` build `target_prefixes = [[tgt_lang], ...]` with NLLB-style tags (`eng_Latn`, `dan_Latn`) and then drop the first hypothesis token. On OPUS-MT this is defensive, not required. If a future change switches back to NLLB, those prefixes become meaningful and the `[1:]` slice should be revisited.

## English news T5

| Field | Value |
| --- | --- |
| id | `mrm8488/t5-base-finetuned-summarize-news` |
| Script | `summary.py` |
| Role | English abstractive summarizer |
| Local training | none |

This is an English T5-base checkpoint fine-tuned on news. It is the reason the pipeline pivots through English: in 2023 a competent English news summarizer was easy to download, while a strong Danish one was not.

Generation settings in the script:

| Knob | Value | Intent |
| --- | --- | --- |
| `num_beams` | 2 | Cheap beam search |
| `max_length` | 80 | Short news lede / blurb |
| `repetition_penalty` | 5.0 | Aggressive anti-loop (very high) |
| `length_penalty` | 1.0 | Neutral length |
| `early_stopping` | True | Stop when beams finish |

`repetition_penalty=5.0` is unusually strong. It was likely a reaction to T5 repeating n-grams on long concatenated chunks. It can also clip useful repeated entities (place names, party names). If you re-run the labeler, try 1.5–2.5 and keep the `rp*` filename suffix honest.

The model is applied **per chunk**, then strings are concatenated. A 1,800-token English article might become three 80-token summaries glued together. Downstream mT5 therefore sometimes sees multi-sentence silver targets that read like a sequence of local blurbs rather than one edited abstract.

## mT5

| Size | Hugging Face id | Script | Local folder |
| --- | --- | --- | --- |
| Large (train) | `google/mt5-large` | `finetune.py` | `./large_model` |
| Small (eval/inspect) | `google/mt5-small` | `eval.py`, `use_model.py` | `small_model` |

mT5 is multilingual T5. Danish is in its pretraining mixture, so the fine-tune does not have to teach the model the language from scratch. The hope is that silver Danish targets are enough to specialize it for news compression.

`finetune.py` also builds an `AutoConfig` with generation defaults that the trainer uses when `predict_with_generate=True`:

| Config key | Value |
| --- | --- |
| `min_length` | 9 |
| `max_length` | 128 |
| `length_penalty` | 0.8 |
| `no_repeat_ngram_size` | 3 |
| `num_beams` | 4 |
| `dropout_rate` | 0.1 |

`use_model.py` does **not** reuse that config. It generates with `num_beams=2`, `no_repeat_ngram_size=1`, `max_length=128`. Qualitative prints and training-time ROUGE are therefore not the same decode.

### small vs large mismatch

The training script saves `large_model`. The eval scripts load `small_model`. That is a leftover from running a cheaper inspection model. To evaluate the model you actually trained, point `local_model_path` / `from_pretrained("small_model")` at `large_model`, or copy the folder.

## BERTScore backbone (eval only)

`eval.py` computes BERTScore with:

```python
model_type="xlm-roberta-large"
lang="da"
```

`xlm-roberta-large` is downloaded at eval time. It is not trained in this repo. It is the contextual encoder for token-similarity F1 between prediction and reference.

## Disk layout after a full setup

```text
models/
  opus-mt-da-en_ct2/     # required by translate.py
  opus-mt-en-da_ct2/     # required by translate_back.py
small_model/             # required by use_model.py and eval.py
large_model/             # written by finetune.py
mt5-summarize-large/     # Hugging Face Trainer output_dir (checkpoints)
```

`models/`, `*_model/`, and `mt5-summarize-*/` are gitignored.

## What was considered and left commented

`Ctranslate_converter.py` still names:

- `facebook/nllb-200-3.3B`
- `facebook/nllb-200-distilled-600m`

NLLB would have given one runtime for many directions, at a much higher VRAM cost for the 3.3B model. Distilled 600M is closer to OPUS-MT in size but was not the submitted path.

Do not uncomment those lines unless you also change `translate.py` / `translate_back.py` to NLLB tokenization (source language token, target prefix, no naive `[1:]` unless it still matches NLLB's first token).
