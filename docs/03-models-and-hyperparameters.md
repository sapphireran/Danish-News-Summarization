# Models and hyperparameters

A catalog of every pretrained checkpoint the 2023 scripts touch, why it was chosen, and the knobs that actually affect quality.

## Translation: Helsinki-NLP OPUS-MT

| Direction | Hugging Face id | CTranslate2 directory |
| --- | --- | --- |
| Danish → English | `Helsinki-NLP/opus-mt-da-en` | `models/opus-mt-da-en_ct2` |
| English → Danish | `Helsinki-NLP/opus-mt-en-da` | `models/opus-mt-en-da_ct2` |

OPUS-MT models are relatively small Marian checkpoints trained on OPUS bitext. For news-like sentences they are a good speed/quality compromise. They are weaker on:

- Quoted speech with ellipses
- Municipal abbreviations and party letter codes
- Proper names that look like common nouns (`Bakken`, `Sund`)
- Code-switched English loanwords already present in Danish news

NLLB-200 (600M and 3.3B) conversions are commented in `Ctranslate_converter.py`. They were considered as a quality upgrade and dropped for runtime. If you revive the factory and have the VRAM, NLLB is the first A/B test to run — but you must then use real language-code prefixes, which the current decode path already half-implements.

## English summarizer: T5 news fine-tune

```
mrm8488/t5-base-finetuned-summarize-news
```

A community T5-base fine-tune aimed at English news. It produces short, lead-like abstracts. That matches Danish newsroom style better than a long-form CNN/DailyMail model, at the cost of dropping nuance.

Committed generation hyperparameters:

```
num_beams=2
max_length=80
repetition_penalty=5.0
length_penalty=1.0
early_stopping=True
```

`repetition_penalty=5.0` is high. It was a reaction to degenerate loops on concatenated packs. It also suppresses legitimate repetition (a name that *should* appear twice). If you retune, sweep `{1.2, 2.0, 3.0, 5.0}` on 50 articles and read the outputs; do not trust ROUGE alone.

`summary.py` hardcodes `[:10]`. That is not a hyperparameter; it is a leftover debug slice.

## Target model: mT5

| Script | Checkpoint | Role |
| --- | --- | --- |
| `finetune.py` | `google/mt5-large` | Train the Danish summarizer |
| `use_model.py` | `google/mt5-small` tokenizer + `small_model` weights | Qualitative generations |
| `eval.py` | `google/mt5-small` tokenizer + `small_model` weights | Official scores |

The mismatch is historical. The course trained a large model and later checked a small student checkpoint in the eval scripts. When you reproduce, pick **one** size and use it in all three files, or you will tokenize with the wrong vocabulary.

### Fine-tune config (`AutoConfig`)

```
min_length=9
max_length=128
length_penalty=0.8
no_repeat_ngram_size=3
num_beams=4
dropout_rate=0.1
```

`min_length=9` avoids empty or two-word dumps. `length_penalty=0.8` slightly prefers shorter outputs, which is appropriate for news leads. `no_repeat_ngram_size=3` is a second anti-loop device on top of the English-stage repetition penalty.

### Training arguments

| Argument | Value | Comment |
| --- | --- | --- |
| `num_train_epochs` | 20 | High for mT5-large; watch val ROUGE for overfit to translationese |
| `learning_rate` | 3e-4 | Typical Adafactor range for T5-family |
| `lr_scheduler_type` | `polynomial` | Decays toward the end of 20 epochs |
| `warmup_steps` | 1000 | Meaningful only if total steps ≫ 1000 |
| `optim` | `adafactor` | Memory-friendly; standard for T5 |
| `weight_decay` | 0.01 | |
| `per_device_train_batch_size` | 8 | |
| `gradient_accumulation_steps` | 1 | Effective batch = 8 |
| `fp16` | True | mT5 + fp16 can be numerically spicy; if loss spikes, try bf16 |
| `predict_with_generate` | True | Needed for ROUGE during eval |
| `generation_max_length` | 128 | |
| `load_best_model_at_end` | True | |
| `metric_for_best_model` | `rouge_1_mid_fmeasure` | Unigram overlap; can reward extractive copying |
| `save_total_limit` | 1 | Only the latest/best-ish checkpoint is kept |

`evaluation_strategy` / `save_strategy` are `"epoch"`. On a 10k-pair set that is a reasonable cadence. On a 200-pair toy split it over-evaluates.

## Evaluation models

BERTScore in `eval.py` uses:

```
lang='da'
model_type="xlm-roberta-large"
```

XLM-R large is a reasonable Danish-capable scorer. It is slow. On the full Nordjylland test split, budget time accordingly. `use_model.py` does not compute BERTScore; it only prints text.

## Tokenization lengths

| Field | Train / eval max length |
| --- | --- |
| Article body (`body` or `input_text`) | 1024 |
| Summary (`summary` or `target_text`) | 128 (180 in `use_model.py` labels) |

`use_model.py` tokenizes labels to 180 but generates with `max_length=128`. The extra 52 tokens exist only so the printed reference is less often truncated than the generation.

## What was *not* used (and why that is documented)

- **PEGASUS / BART large** — English-only, heavier; T5-base already filled the role.
- **Decoder-only LLMs** — not part of the 2023 course toolkit we standardized on.
- **Danish-specific tokenizers** — mT5's SentencePiece already covers Danish; a dedicated tokenizer would have required pretraining we could not afford.
- **Reinforcement learning / factuality rewards** — out of scope; silver labels already drift, and RL would amplify that without a fact checker.

## Suggested sweeps if you continue the work

Keep the architecture, change one axis at a time:

1. Translation model: OPUS-MT vs NLLB-600M on 200 articles, judged by named-entity preservation.
2. English summarizer: current T5 vs a newer multilingual summarizer that might skip the English hop entirely.
3. mT5 size: small vs base vs large on the same silver set.
4. Pack policy: independent pack summaries vs hierarchical second-pass.
5. Best-model metric: ROUGE-1 vs ROUGE-L vs BERTScore-F1.

Record those sweeps outside this historical script set so the 2023 command sequence stays reproducible.
