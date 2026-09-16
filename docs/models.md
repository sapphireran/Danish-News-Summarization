# Models

Every checkpoint the scripts touch is a public Hugging Face model. This
page lists what each one is for and which local directory the code
expects after conversion or fine-tuning.

## Translation — Helsinki-NLP OPUS-MT + CTranslate2

| Direction | Transformers id | CTranslate2 directory |
| --- | --- | --- |
| Danish → English | `Helsinki-NLP/opus-mt-da-en` | `models/opus-mt-da-en_ct2` |
| English → Danish | `Helsinki-NLP/opus-mt-en-da` | `models/opus-mt-en-da_ct2` |

OPUS-MT models are bilingual MarianMT checkpoints. They do **not** take
NLLB language-code prefixes such as `dan_Latn` or `eng_Latn`. The 2023
scripts still pass those strings as `src_lang` / `tgt_lang` and as
`target_prefix` tokens. For a Marian OPUS model the prefix is typically
ignored or becomes a junk first token that `translate_back.py` then
strips with `hypotheses[0][1:]`. See [limitations.md](limitations.md).

Conversion:

```bash
python Ctranslate_converter.py
```

Enable the commented `opus-mt-da-en` block before the forward
translation step. Output directories are created by the converter; they
are gitignored.

## English summarizer

| Script | id |
| --- | --- |
| `summary.py` | `mrm8488/t5-base-finetuned-summarize-news` |

This is a T5-base checkpoint fine-tuned on English news summarization.
Max input length in the script is 512. It is only used to label the
English pivot; it is not the model students were asked to submit.

## Danish / multilingual summarizer (the actual project model)

| Script | Hugging Face id | Local directory |
| --- | --- | --- |
| `finetune.py` | `google/mt5-large` | `./large_model` |
| `eval.py` | `google/mt5-small` (tokenizer) + `small_model` (weights) | `small_model` |
| `use_model.py` | same as `eval.py` | `small_model` |

[mT5](https://arxiv.org/abs/2010.11934) is the multilingual T5 trained
on mC4, including Danish. Fine-tuning it on silver Danish pairs is the
whole learning problem in this repo. Generation config applied in
`finetune.py`:

```
min_length = 9
max_length = 128
length_penalty = 0.8
no_repeat_ngram_size = 3
num_beams = 4
dropout_rate = 0.1
```

`use_model.py` decodes with a different policy (`num_beams=2`,
`no_repeat_ngram_size=1`, no length penalty). Scores from `eval.py`
and the printed samples from `use_model.py` are therefore not
guaranteed to describe the same decoding distribution.

## Evaluation-only models

`eval.py` loads BERTScore with `lang='da'` and
`model_type="xlm-roberta-large"`. That download is separate from mT5
and is used only as a metric, not as a generator.

## Disk and GPU rough sizes

These are order-of-magnitude figures for planning a local run, not
benchmarks.

| Artifact | Parameters (approx.) | Notes |
| --- | --- | --- |
| OPUS-MT da↔en | ~75M each | Comfortable on CPU after CTranslate2 convert |
| T5-base news | 220M | English labeling; 512-token windows |
| mT5-small | 300M | `eval.py` / `use_model.py` |
| mT5-large | 1.2B | `finetune.py`; wants a 16 GB+ GPU at batch 8 / 1024 |
| XLM-R large | 550M | BERTScore only |

The examples under `examples/` never load these checkpoints.
