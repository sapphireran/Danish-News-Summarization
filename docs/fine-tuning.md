# Fine-tuning notes (`finetune.py`)

This file is the only training entry point. It assumes you already have silver labels split into three CSVs under `datasets/`.

## Inputs

```python
train_dataset      = load_dataset('csv', data_files='datasets/train_dataset.csv')['train']
validation_dataset = load_dataset('csv', data_files='datasets/validation_dataset.csv')['train']
test_dataset       = load_dataset('csv', data_files='datasets/test_dataset.csv')['train']
```

Hugging Face still names the loaded split `'train'` when you pass a single CSV. The code then wraps them in a `DatasetDict` with keys `train`, `validation`, and `test`. Only `train` and `validation` are given to `Seq2SeqTrainer`.

## Tokenization

```python
input_feature = mt5_tokenizer(data["body"], truncation=True, max_length=1024)
label         = mt5_tokenizer(data["summary"], truncation=True, max_length=128)
```

Returned fields: `input_ids`, `attention_mask`, `labels`.

Original columns `id`, `body`, `summary` are removed. After `map`, you cannot print a Danish article from the tokenized dataset without joining back to the CSV on row order. Row order is preserved by `map` with `batched=True`, but do not shuffle the tokenized set independently of the CSV if you still want that join.

mT5 tokenizers expect a `</s>` / padding setup that `DataCollatorForSeq2Seq` handles. Padding is not done in `tokenize_data`; the collator pads each batch.

### Prefix

Some T5 summarizers want a task prefix such as `summarize: `. `finetune.py` does **not** add one. mT5 was pretrained with a different span-corruption format, and the 2023 run treated “body in, summary out” as enough of a fine-tune signal. If you add a prefix later, add it on both train and inference.

## Model init

```python
model_name = "google/mt5-large"
mt5_config = AutoConfig.from_pretrained(model_name, min_length=9, max_length=128, ...)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name, config=mt5_config).to(device)
```

Passing a modified config into `from_pretrained` overlays generation defaults on the pretrained weights. Dropout `0.1` is also set here.

## Trainer arguments (as written)

| Argument | Value | Comment |
| --- | --- | --- |
| `output_dir` | `mt5-summarize-large` | Epoch checkpoints |
| `num_train_epochs` | 20 | Long; silver data overfits |
| `learning_rate` | `3e-4` | Typical Adafactor-scale LR, high for AdamW |
| `lr_scheduler_type` | `polynomial` | |
| `warmup_steps` | 1000 | Independent of dataset size |
| `optim` | `adafactor` | Memory-friendly for mT5-large |
| `weight_decay` | 0.01 | |
| `per_device_train_batch_size` | 8 | |
| `per_device_eval_batch_size` | 8 | |
| `gradient_accumulation_steps` | 1 | Effective batch = 8 per GPU |
| `evaluation_strategy` | `epoch` | |
| `save_strategy` | `epoch` | |
| `predict_with_generate` | `True` | Needed for ROUGE during eval |
| `generation_max_length` | 128 | |
| `logging_steps` | 250 | |
| `fp16` | `True` | Needs a CUDA GPU |
| `load_best_model_at_end` | `True` | |
| `metric_for_best_model` | `rouge_1_mid_fmeasure` | |
| `save_total_limit` | 1 | Plus the best, depending on Transformers version |
| `push_to_hub` | `False` | |

`save_steps = 100` is ignored when `save_strategy="epoch"`.

`log_level = "error"` hides most trainer logs. Raise it if a rerun dies silently.

## Metrics during training

`compute_metrics`:

1. Batch-decodes predictions and labels.
2. Replaces label `-100` with `pad_token_id`.
3. Sentence-tokenizes with NLTK and joins sentences with `\n` (the ROUGE package’s expected “sentence” delimiter).
4. Calls `datasets.load_metric("rouge")` with `use_aggregator=True`.
5. Returns mid F for ROUGE-1/2/L.

`datasets.load_metric` is the old API. On current `datasets` it warns or fails; `evaluate.load("rouge")` is the replacement. `eval.py` already imports `evaluate` but still calls `datasets.load_metric` inside `compute_metrics`.

Only ROUGE-1 mid F is used for checkpoint selection. ROUGE-2 and ROUGE-L are logged and then ignored for `load_best_model_at_end`.

## Saving

After `trainer.train()` the script writes `./large_model` via `save_pretrained`, unwrapping `model.module` if the trainer used `DataParallel`.

It does **not** save the tokenizer next to the weights. `use_model.py` and `eval.py` therefore load a tokenizer from `google/mt5-small` / `google/mt5-large` on the Hub instead of from `./large_model`. When you rerun, also call `mt5_tokenizer.save_pretrained("./large_model")`.

## Memory

mT5-large + 1024 source tokens + 128 decoder tokens + `fp16` + `predict_with_generate` (beam 4) is the VRAM-heavy path. If a rerun OOMs:

1. Drop `per_device_train_batch_size` to 2 and raise `gradient_accumulation_steps` to 4.
2. Fine-tune `google/mt5-small` or `google/mt5-base` instead, and keep the tokenizer/weights names consistent in `eval.py` / `use_model.py`.
3. Turn off `predict_with_generate` during training and compute ROUGE only at the end.

## Things this script does not do

- No early stopping callback beyond “keep the best of 20 epochs.”
- No seed is set. Runs are not bit-identical.
- No max-grad-norm override (Transformers default applies).
- No filtering of empty silver summaries.
- No length-ratio filter (summary should be shorter than body). A translation glitch can produce a “summary” longer than the article.

The offline example `examples/demo_finetune_preview.py` prints token-length histograms on the synthetic CSVs so you can see how much 1024 / 128 truncation would bite, without loading mT5.
