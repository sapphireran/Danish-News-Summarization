# Fine-tuning mT5

`finetune.py` trains `google/mt5-large` on the silver-label splits under
`datasets/`. It is the only script that writes a summarization
checkpoint.

## Inputs

```text
datasets/train_dataset.csv
datasets/validation_dataset.csv
datasets/test_dataset.csv
```

Columns: `id`, `body`, `summary` (both Danish). See
[datasets.md](datasets.md) for how to get there from
`labeled_dataset_ml80_rp5.0.csv`.

The test split is loaded and tokenized but **never passed to
`Seq2SeqTrainer`**. Only `train` and `validation` are used. The test
file is therefore optional for a training run, but the script will
still crash if the path is missing.

## Tokenization

```python
input_feature = mt5_tokenizer(data["body"], truncation=True, max_length=1024)
label = mt5_tokenizer(data["summary"], truncation=True, max_length=128)
```

mT5 tokenizers are SentencePiece. 1024 source tokens is enough for most
Danish news articles and will truncate long features. 128 target tokens
is short: concatenated chunk summaries from `summary.py` will often
lose their last window.

No explicit padding is done in `tokenize_data`.
`DataCollatorForSeq2Seq` pads per batch and sets label pad tokens to
`-100` so they are ignored in the loss.

## Model config overrides

```python
AutoConfig.from_pretrained(
    model_name,
    min_length=9,
    max_length=128,
    length_penalty=0.8,
    no_repeat_ngram_size=3,
    num_beams=4,
    dropout_rate=0.1,
)
```

These values are baked into the config object that is then passed to
`from_pretrained`. They affect generation during eval more than they
affect teacher-forced training.

| Field | Value | Intent |
| --- | --- | --- |
| `min_length` | 9 | Avoid empty or two-word dumps |
| `max_length` | 128 | Match label truncation |
| `length_penalty` | 0.8 | Mild pressure toward shorter beams |
| `no_repeat_ngram_size` | 3 | Block 3-gram loops |
| `num_beams` | 4 | Heavier than the English teacher's 2-beam search |
| `dropout_rate` | 0.1 | Default-ish regularization |

## Training arguments (as committed)

| Argument | Value | Comment |
| --- | --- | --- |
| `output_dir` | `mt5-summarize-large` | Intermediate Trainer checkpoints |
| `num_train_epochs` | 20 | High. Watch val ROUGE for overfitting. |
| `learning_rate` | `3e-4` | Typical Adafactor + T5 range |
| `lr_scheduler_type` | `polynomial` | Decays from 3e-4 after warmup |
| `warmup_steps` | 1000 | Long warmup; short datasets may never leave it |
| `optim` | `adafactor` | Memory-friendlier than AdamW on mT5-large |
| `weight_decay` | 0.01 | |
| `per_device_train_batch_size` | 8 | |
| `per_device_eval_batch_size` | 8 | |
| `gradient_accumulation_steps` | 1 | Effective batch = 8 per GPU |
| `evaluation_strategy` | `epoch` | |
| `save_strategy` | `epoch` | |
| `predict_with_generate` | `True` | Needed for ROUGE during eval |
| `generation_max_length` | 128 | |
| `logging_steps` | 250 | |
| `fp16` | `True` | Requires CUDA. CPU runs should set this False. |
| `load_best_model_at_end` | `True` | |
| `metric_for_best_model` | `rouge_1_mid_fmeasure` | |
| `save_total_limit` | 1 | Only the latest / best is kept |
| `push_to_hub` | `False` | |

`save_steps = 100` is ignored when `save_strategy="epoch"`.

## Metrics during training

`compute_metrics` uses `datasets.load_metric("rouge")` and reports mid
F-measure for ROUGE-1/2/L. Predictions and labels are sentence-split
with NLTK and joined on `\n` because the Hugging Face ROUGE helper
treats newlines as sentence boundaries for ROUGE-L.

`datasets.load_metric` is deprecated. A later rerun should use:

```python
import evaluate
rouge_metric = evaluate.load("rouge")
```

and then adapt the result schema. `evaluate`'s ROUGE return values are
plain floats, not the old `mid.fmeasure` objects. The trainer argument
`metric_for_best_model="rouge_1_mid_fmeasure"` would need a matching
rename.

BERTScore is **not** computed during training. That happens only in
`eval.py`. Training eval already runs generation over the validation
set; adding BERTScore with `xlm-roberta-large` would dominate step
time.

## Where weights are written

Two locations:

1. `mt5-summarize-large/` — Hugging Face Trainer checkpoints (`save_strategy`).
2. `./large_model/` — a final `save_pretrained` after `trainer.train()`.

The final save unwraps `trainer.model.module` when the model was wrapped
for multi-GPU. Eval scripts do **not** load `large_model`. They load
`small_model`. After a large run, either:

```bash
cp -r large_model small_model
```

or edit the eval scripts. Forgetting this looks exactly like "the model
never trained".

## Hardware notes

mT5-large + 1024 source + 128 target + `fp16` + batch 8 was the 2023
course-GPU setup. On a smaller card:

- drop to `google/mt5-small` or `google/mt5-base`
- cut `per_device_train_batch_size` to 2 or 4
- raise `gradient_accumulation_steps` so the effective batch stays near 8
- set `fp16=False` on CPU (and expect the run to be impractical)

Adafactor is the main reason this fit in course-lab memory. Switching to
AdamW without lowering batch size will OOM before it overfits.

## Warmup vs dataset size

1000 warmup steps at batch 8 is 8,000 examples of warmup. If the train
CSV has 9,000 rows, warmup is most of the first epoch. If you shrink the
corpus for a debug run, also shrink `warmup_steps` (for example 10% of
the first epoch) or the learning rate will barely move.

## What this script does not do

- It does not create `datasets/*.csv`.
- It does not log to Weights & Biases or TensorBoard unless you add it.
- It does not evaluate the held-out `test` split.
- It does not upload to the Hub (`push_to_hub=False`).
- It does not set a seed. Runs are not strictly reproducible.

`examples/configs/finetune.example.json` records the committed
hyperparameters as data so a later rewrite can load them instead of
leaving them scattered in Python.
