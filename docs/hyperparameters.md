# Hyperparameters

Numbers below are copied from the 2023 scripts. They are not a recommended search space. If you change a decode setting that is baked into an output filename, rename the file.

## Translation packing

Shared idea: never send more than ~90% of the Marian 512-token window in one batch.

| Name | Script | Value |
| --- | --- | --- |
| `max_length` | `translate.py`, `translate_back.py` | 512 |
| `text_max_length` | both | `int(512 * 0.9)` → 460 |
| Long-sentence split | `translate.py` | word tokens; flush on `,` / `;` / `:` or when length overflows |
| Sentence tokenizer | all text scripts | NLTK `punkt` |

`summary.py` uses `text_max_length = 512` (no 0.9 margin) because that value is the T5 input cap, not a Marian safety margin.

## English summarizer decode

From `summary.py`:

| Name | Value |
| --- | --- |
| `model_name` | `mrm8488/t5-base-finetuned-summarize-news` |
| `num_beams` | 2 |
| `max_length` | 80 |
| `repetition_penalty` | 5.0 |
| `length_penalty` | 1.0 |
| `early_stopping` | True |
| Row cap | `[:10]` |

Output path: `summarized_file_ml80_rp5.0.csv`.

## mT5 generation config (training)

From `finetune.py` `AutoConfig.from_pretrained(...)`:

| Name | Value |
| --- | --- |
| `min_length` | 9 |
| `max_length` | 128 |
| `length_penalty` | 0.8 |
| `no_repeat_ngram_size` | 3 |
| `num_beams` | 4 |
| `dropout_rate` | 0.1 |

Trainer generation:

| Name | Value |
| --- | --- |
| `predict_with_generate` | True |
| `generation_max_length` | 128 |

## mT5 training

From `Seq2SeqTrainingArguments` in `finetune.py`:

| Name | Value | Notes |
| --- | --- | --- |
| `output_dir` | `mt5-summarize-large` | Checkpoint root |
| `num_train_epochs` | 20 | Long for silver labels; early-stop via best ROUGE-1 |
| `learning_rate` | `3e-4` | High vs typical AdamW 1e-4; Adafactor-friendly |
| `lr_scheduler_type` | `polynomial` | Comment lists the other HF scheduler names |
| `warmup_steps` | 1000 | Fixed step count, not a ratio |
| `optim` | `adafactor` | Common for T5-family |
| `weight_decay` | 0.01 | |
| `per_device_train_batch_size` | 8 | |
| `per_device_eval_batch_size` | 8 | |
| `gradient_accumulation_steps` | 1 | Effective batch = 8 per device |
| `evaluation_strategy` | `epoch` | |
| `save_strategy` | `epoch` | |
| `save_steps` | 100 | Redundant with epoch saves; still set |
| `logging_steps` | 250 | |
| `fp16` | True | Needs CUDA |
| `load_best_model_at_end` | True | |
| `metric_for_best_model` | `rouge_1_mid_fmeasure` | |
| `save_total_limit` | 1 | Only one checkpoint kept |
| `push_to_hub` | False | |
| `log_level` | `error` | Quiet logs |

Tokenizer caps:

| Field | `max_length` |
| --- | --- |
| `body` | 1024 |
| `summary` | 128 |

Tokenize `batch_size` is 128 rows per map batch (preprocessing, not training).

## Inspection decode (`use_model.py`)

| Name | Value |
| --- | --- |
| Base tokenizer name | `google/mt5-small` |
| Weights | `small_model` |
| `num_beams` | 2 |
| `num_return_sequences` | 1 |
| `no_repeat_ngram_size` | 1 | Forbids any repeated unigram |
| `remove_invalid_values` | True |
| `max_length` | 128 |
| Label tokenize length | 180 |
| Dataloader batch | 2 |
| Printed batches | 5 |

`no_repeat_ngram_size=1` is harsher than training (`3`). Names that appear twice in a good summary will be blocked.

## Evaluation trainer (`eval.py`)

| Name | Value |
| --- | --- |
| Tokenizer | `google/mt5-small` |
| Weights | `small_model` |
| `output_dir` | `mt5-summarize-large` | Reuses the train folder name |
| `per_device_eval_batch_size` | 64 |
| `evaluation_strategy` | `epoch` |
| `predict_with_generate` | True |
| `dataloader_drop_last` | True | Drops a leftover partial batch |
| Source tokenize | 1024 |
| Target tokenize | 128 |

BERTScore:

| Name | Value |
| --- | --- |
| `lang` | `da` |
| `model_type` | `xlm-roberta-large` |

## Filename encoding

When a decode knob is part of a CSV name, treat the name as a cache key:

```text
summarized_file_ml{max_length}_rp{repetition_penalty}.csv
labeled_dataset_ml{max_length}_rp{repetition_penalty}.csv
```

The 2023 tree only has `ml80_rp5.0`. If you sweep those two knobs, do not reuse the same path.

## What is not specified

The scripts do not set:

- a global random seed
- gradient checkpointing
- label smoothing
- a max source length other than tokenizer truncation
- temperature / top-p (beam search only)

Re-training will not be bit-identical to a 2023 run.
