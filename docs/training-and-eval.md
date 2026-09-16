# Training and evaluation

This page records the fine-tuning and evaluation setup that is actually in
`finetune.py`, `use_model.py`, and `eval.py`. It is a personal lab notebook
for the 2023 run, not a claim that these knobs are optimal.

## Data into the trainer

`finetune.py` tokenizes `body` → encoder and `summary` → labels.

```text
body     → input_ids, attention_mask     (truncate 1024)
summary  → labels                        (truncate 128)
```

`id`, `body`, and `summary` are removed after the map. The collator is
`DataCollatorForSeq2Seq`, which pads dynamically and replaces label pad ids
with `-100` so they are ignored by the loss.

If a silver summary is longer than 128 tokens — easy when `summary.py`
concatenates several 80-token chunk summaries — the tail is silently dropped.

## Optimization

`Seq2SeqTrainingArguments` as committed:

| Argument | Value | Why it is there |
| --- | --- | --- |
| `output_dir` | `mt5-summarize-large` | Checkpoint root |
| `num_train_epochs` | 20 | Long course-project run |
| `learning_rate` | `3e-4` | Relatively high; paired with Adafactor |
| `lr_scheduler_type` | `polynomial` | Decay after warmup |
| `warmup_steps` | 1000 | Stabilize the first updates |
| `optim` | `adafactor` | Memory-friendly for mT5-large |
| `weight_decay` | 0.01 | |
| `per_device_train_batch_size` | 8 | |
| `per_device_eval_batch_size` | 8 | |
| `gradient_accumulation_steps` | 1 | Effective batch = 8 per GPU |
| `evaluation_strategy` | `epoch` | Deprecated name in current Transformers |
| `save_strategy` | `epoch` | |
| `predict_with_generate` | `True` | Needed for ROUGE during eval |
| `generation_max_length` | 128 | |
| `logging_steps` | 250 | |
| `fp16` | `True` | Assumes a CUDA GPU |
| `load_best_model_at_end` | `True` | Reload best ROUGE-1 mid F |
| `metric_for_best_model` | `rouge_1_mid_fmeasure` | See below |
| `save_total_limit` | 1 | Disk saver on a student machine |
| `push_to_hub` | `False` | Local only |

`save_steps = 100` is present but unused while `save_strategy` is `epoch`.

`fp16=True` will fail on a CPU-only machine. For a smoke test, set `fp16` to
`False` and drop the model size.

## Metrics during training

`compute_metrics` decodes predictions and labels, sentence-splits them with
NLTK so ROUGE-Lsum-style newlines exist, then calls
`datasets.load_metric("rouge")` with `use_aggregator=True`.

Reported keys:

- `rouge_1_mid_fmeasure`
- `rouge_2_mid_fmeasure`
- `rouge_l_mid_fmeasure`

The trainer treats ROUGE-1 mid F as the best-model metric. Mid is the
bootstrap center of the official `rouge-score` aggregator, not a single
corpus-level F.

`datasets.load_metric` is deprecated. A current rewrite would use the
`evaluate` package (`evaluate.load("rouge")`). `eval.py` already imports
`evaluate` but still calls `datasets.load_metric` for the actual numbers.

## Saving weights

After `trainer.train()` the script writes `./large_model` via
`save_pretrained`, unwrapping `trainer.model.module` if the model was
DataParallel. Tokenizer files are not explicitly saved there. When you later
load `large_model`, keep using `AutoTokenizer.from_pretrained("google/mt5-large")`
or save the tokenizer next to the weights yourself.

## Qualitative inspection (`use_model.py`)

The script loads `small_model`, tokenizes the Nordjylland News mini test set,
and prints five batches of:

1. source `input_text`
2. reference `target_text`
3. generated text

Generation settings (`num_beams=2`, `no_repeat_ngram_size=1`) are stricter
about repetition than the training config (`no_repeat_ngram_size=3`). Very
short or slightly awkward outputs in the printout can come from that
`no_repeat_ngram_size=1` choice, not only from the checkpoint.

The printed "input" line uses `split_dataset["test"]["input_text"][i]`, which
is the *dataset row* index, while generations come from a DataLoader of batch
size 2. Row `i` and batch `i` are not the same article after the first batch.
Read the printed source as illustrative, not as a guaranteed alignment with
the generation sitting under it.

## Held-out evaluation (`eval.py`)

`eval.py` builds a trainer with no train set and calls `trainer.evaluate()`
on the Alexandra Institute Nordjylland News test split.

Extra metric on top of ROUGE: BERTScore with `lang='da'` and
`model_type="xlm-roberta-large"`. That second model is large; the first eval
pass will download it.

Eval trainer knobs:

| Argument | Value |
| --- | --- |
| `per_device_eval_batch_size` | 64 |
| `predict_with_generate` | `True` |
| `dataloader_drop_last` | `True` |

`dataloader_drop_last=True` silently drops a partial final batch. For a
small test set that can hide several articles. Turn it off if you want a
score over every row.

## How to read the numbers

Silver-label ROUGE on the generated training split is optimistic: the model
is scored against labels that came from a translate-summarize-translate
pipeline, not against journalist-written Danish summaries.

Nordjylland News is the more honest number. It is still extractive-leaning
news text, so a model that copies named entities will look better on ROUGE-1
than it does to a reader.

BERTScore with XLM-R large is there to catch paraphrases that ROUGE misses
after two translation hops. If ROUGE is low but BERTScore F1 stays high, the
model may be semantically close and lexically far — common when the silver
labels still smell like translated English.
