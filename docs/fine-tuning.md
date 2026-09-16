# Fine-tuning mT5

`finetune.py` is the only training script. It fine-tunes
`google/mt5-large` on the silver CSVs with Hugging Face `Seq2SeqTrainer`.

## Inputs

The script expects three files that already exist:

```
datasets/train_dataset.csv
datasets/validation_dataset.csv
datasets/test_dataset.csv
```

Each must have `id`, `body`, and `summary`. The test split is loaded into
the `DatasetDict` but never passed to `Seq2SeqTrainer`. Only `train` and
`validation` are used. The test CSV is dead weight unless you add an extra
evaluate call yourself.

## Tokenization

```
body    → encoder, truncation at 1024
summary → labels, truncation at 128
```

There is no task prefix (`summarize:` / `summariser:`) in the committed
script. mT5 is trained as a plain seq2seq map from article to summary.
That matches how `eval.py` later encodes `input_text`.

## Config baked into the model

`AutoConfig.from_pretrained` is called with generation defaults so
`predict_with_generate=True` during evaluation uses the same beam search
the 2023 run wanted:

- minimum 9 tokens, maximum 128
- length penalty 0.8
- no-repeat trigrams
- 4 beams
- dropout 0.1

Those values are duplicated in `danish_news_sum.config.MT5_LARGE` and
`examples/configs/mt5_large_train.json`.

## Trainer arguments

| Argument | 2023 value | Comment |
| --- | --- | --- |
| `num_train_epochs` | 20 | Long on purpose; `load_best_model_at_end` keeps one ckpt |
| `learning_rate` | 3e-4 | High for Adafactor, typical for T5-style runs |
| `lr_scheduler_type` | `polynomial` | Decays toward zero after warmup |
| `warmup_steps` | 1000 | First thousand steps are warmup, not a full epoch |
| `optim` | `adafactor` | Avoids Adam's extra moment buffers on mT5-large |
| `weight_decay` | 0.01 | |
| `per_device_train_batch_size` | 8 | Fits a 24 GB-class GPU with fp16 |
| `gradient_accumulation_steps` | 1 | Raise this before lowering the learning rate |
| `evaluation_strategy` / `save_strategy` | `epoch` | One eval + checkpoint per epoch |
| `predict_with_generate` | True | Needed for ROUGE |
| `generation_max_length` | 128 | Matches the config |
| `fp16` | True | |
| `load_best_model_at_end` | True | |
| `metric_for_best_model` | `rouge_1_mid_fmeasure` | Unigram overlap selected the checkpoint |
| `save_total_limit` | 1 | Disk saver; you cannot compare two epochs later |
| `push_to_hub` | False | Personal run, local checkpoint only |

`save_steps = 100` is present but unused while `save_strategy="epoch"`.

## Metrics during training

`compute_metrics` loads Hugging Face `rouge` *inside* the function, once
per evaluation. It decodes predictions and labels, restores pad ids from
`-100`, sentence-tokenizes with NLTK, then reports mid F-measure for
ROUGE-1/2/L. BERTScore is **not** computed at train time. That is
intentional: XLM-R large on every epoch would dominate the wall clock.

The same ROUGE helper is more careful in `eval.py` (it also reports
BERTScore). Do not expect the two printed dicts to share keys.

## Saving

After `trainer.train()` the script writes `./large_model` via
`save_pretrained`, unwrapping a `DataParallel` module if one exists. The
trainer output directory `mt5-summarize-large` still holds the last
checkpoint and logs. Both paths are gitignored.

`eval.py` and `use_model.py` load `small_model`, not `large_model`. If you
train large and want to inspect it, either change those paths or copy the
best checkpoint:

```bash
cp -r large_model small_model
```

A smaller personal run can start from `google/mt5-small` by editing
`model_name` or by loading `examples/configs` as a checklist. There is no
CLI flag.

## Practical notes

- Adafactor + fp16 + mT5-large is memory-sensitive. If the job OOMs, cut
  `per_device_train_batch_size` to 2 or 4 and raise
  `gradient_accumulation_steps` so the effective batch stays near 8.
- `nltk.download` is not called in `finetune.py`. Download `punkt` once
  before the first eval epoch or `sent_tokenize` will raise.
- `datasets.load_metric("rouge")` is the old API. On current `datasets` it
  still works but prints a deprecation warning. `evaluate.load("rouge")`
  is the replacement if you modernise the script later.
- Twenty epochs on a 10k-row silver set is enough to overfit translationese.
  Watch the validation ROUGE-1; if it peaks early, the best-checkpoint
  logic already keeps that epoch.
