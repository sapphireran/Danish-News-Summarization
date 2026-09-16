# End-to-end pipeline

This document walks the silver-label pipeline in the same order the 2023 scripts were meant to run.

## Why a pivot through English

mT5 can already read Danish, but it still needs target summaries. Collecting thousands of journalist abstracts was out of scope. The project instead **manufactures** Danish targets:

```
Danish article
    --opus-mt-da-en-->  English article
    --T5 news summarizer-->  English summary
    --opus-mt-en-da-->  Danish summary  (silver label)
```

Fine-tuning then ignores the English intermediates and learns `Danish article → Danish summary` directly.

That buys scale. It also couples the teacher to two translation models and an English-only news summarizer. Errors compound; they do not average out.

## Stage 0 — Convert OPUS-MT to CTranslate2

**Script:** `Ctranslate_converter.py`

Hugging Face `Helsinki-NLP/opus-mt-*` checkpoints are converted with `ctranslate2.converters.TransformersConverter`. Runtime translation uses the CTranslate2 `Translator`, which is much faster than generating with Transformers on a single GPU.

**Checked-in behavior:** only `Helsinki-NLP/opus-mt-en-da` is converted, into `models/opus-mt-en-da_ct2`. The `opus-mt-da-en` converter is present but commented. `translate.py` still expects `models/opus-mt-da-en_ct2`. Enable both conversions before a full run. NLLB converters are also commented leftovers from earlier experiments.

See [03-translation.md](03-translation.md).

## Stage 1 — Danish → English articles

**Script:** `translate.py`

| | |
| --- | --- |
| Input | `10000_articles_without_linebreaks.csv` |
| Required columns | `id`, `article text` |
| Output | `translated_articles.csv` |
| Output columns | `id`, `body`, `translated` |
| Model | `models/opus-mt-da-en_ct2` + tokenizer `Helsinki-NLP/opus-mt-da-en` |
| Packing limit | 90% of 512 tokens (`text_max_length = 460`) |

Articles are sentence-split with NLTK `punkt`, packed into batches that stay under the encoder limit, then `translate_batch`ed. Sentences longer than the limit are broken on commas / semicolons / word boundaries.

`body` is a rename of `article text`. Downstream scripts never look at the original column name again.

## Stage 2 — English summarization

**Script:** `summary.py`

| | |
| --- | --- |
| Input | `translated_articles.csv` |
| Output | `summarized_file_ml80_rp5.0.csv` |
| Output columns | `id`, `body`, `translated`, `summary` |
| Model | `mrm8488/t5-base-finetuned-summarize-news` |
| Encoder cap | 512 tokens |
| `generate` | `num_beams=2`, `max_length=80`, `repetition_penalty=5.0`, `length_penalty=1.0`, `early_stopping=True` |

Long English articles are split into sub-articles that each fit 512 tokens. Each sub-article is summarized independently. Sub-summaries are concatenated with a space. That is extractive-adjacent at the *document* level (every chunk contributes text) even though each chunk is abstractive.

**Debug leftover:** the dataframe is sliced with `[:10]`. Delete that slice for a full corpus run.

See [04-summarization.md](04-summarization.md).

## Stage 3 — English → Danish summaries

**Script:** `translate_back.py`

| | |
| --- | --- |
| Input | `summarized_file_ml80_rp5.0.csv` |
| Output | `labeled_dataset_ml80_rp5.0.csv` |
| Output columns | `id`, `body`, `summary` |
| Model | `models/opus-mt-en-da_ct2` + tokenizer `Helsinki-NLP/opus-mt-en-da` |

Only the English `summary` column is translated. The Danish `body` is copied through unchanged. The English article (`translated`) is dropped here — training does not need it.

`translate_article()` still sentence-splits, even though summaries are short. That keeps the same safety packing as article translation.

## Stage 4 — Split into train / validation / test

There is **no** split script in the repo. After you have `labeled_dataset_ml80_rp5.0.csv`, create:

```
datasets/train_dataset.csv
datasets/validation_dataset.csv
datasets/test_dataset.csv
```

Each file must have `id`, `body`, `summary`. Recommended practice from the course write-up: shuffle with a fixed seed, hold out ~10% validation and ~10% test, and keep article `id`s unique across splits so the same story cannot leak.

Sample rows that match this schema live in `examples/data/`.

See [02-datasets.md](02-datasets.md).

## Stage 5 — Fine-tune mT5

**Script:** `finetune.py`

- Base checkpoint: `google/mt5-large`
- Source max length: 1024
- Target max length: 128
- Optimizer: Adafactor, lr `3e-4`, polynomial decay, 1000 warmup steps
- 20 epochs, batch size 8, fp16, `load_best_model_at_end` on `rouge_1_mid_fmeasure`
- Writes `mt5-summarize-large/` during training and `./large_model` at the end

See [05-training.md](05-training.md) and [07-hyperparameters.md](07-hyperparameters.md).

## Stage 6 — Qualitative check

**Script:** `use_model.py`

Loads `small_model` (not `./large_model`) and `ScandEval/nordjylland-news-summarization-mini` `test`. Prints five batches of:

- input article (`input_text`)
- gold summary (`target_text`)
- generated summary

Generation uses `num_beams=2`, `no_repeat_ngram_size=1`, `max_length=128`. `no_repeat_ngram_size=1` forbids repeating any unigram — aggressive, and it can make output read telegraphic.

## Stage 7 — Quantitative eval

**Script:** `eval.py`

Loads `small_model` and `alexandrainst/nordjylland-news-summarization` `test`. Tokenizes `input_text` / `target_text`. Reports ROUGE-1/2/L mid F-measure and BERTScore P/R/F1 with `xlm-roberta-large` and `lang='da'`.

This is a **different distribution** than the silver-label train set: Nordjylland summaries are human-oriented news abstracts, not back-translated T5 output. A drop from training ROUGE to this eval is expected.

See [06-evaluation.md](06-evaluation.md).

## Data that never enters the model

The English `translated` column is only a teacher-side intermediate. At inference, `use_model.py` / `eval.py` feed Danish `input_text` straight into mT5. You do not run OPUS-MT at test time.

## Failure points (practical)

1. Missing `models/opus-mt-da-en_ct2` because the converter left it commented.
2. `summary.py` processes 10 rows and you do not notice.
3. `finetune.py` looks in `datasets/` but the labeled file is still in the repo root.
4. `eval.py` / `use_model.py` look for `small_model` after you only saved `./large_model`.
5. NLTK `punkt` is not downloaded on a fresh machine (`nltk.download('punkt')` is already in the scripts).
6. `use_auth_token=False` is a Transformers v4-era argument; newer releases prefer `token=None`.

The examples under `examples/validation/` catch schema mistakes (1–4 are runtime / ops). They will not download weights.
