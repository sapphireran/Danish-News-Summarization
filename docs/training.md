# Training

All numbers on this page are taken from `finetune.py` as committed. They are not suggested defaults for a new project; they are the course run’s knobs, written down so you can see what a 20-epoch `mT5-large` job was actually doing.

## Data into the trainer

```python
model_name = "google/mt5-large"

train_dataset = load_dataset('csv', data_files='datasets/train_dataset.csv')['train']
validation_dataset = load_dataset('csv', data_files='datasets/validation_dataset.csv')['train']
test_dataset = load_dataset('csv', data_files='datasets/test_dataset.csv')['train']
```

`test_dataset` is loaded and tokenized, then **never passed** to `Seq2SeqTrainer`. Only `train` and `validation` are used. The test CSV is dead weight unless you add an evaluate call yourself.

Tokenization:

```python
input_feature = mt5_tokenizer(data["body"], truncation=True, max_length=1024)
label = mt5_tokenizer(data["summary"], truncation=True, max_length=128)
```

- Long Danish articles lose their tail at 1024 SentencePiece tokens.
- Silver summaries longer than 128 tokens (joined chunk summaries) lose *their* tail — often the most specific nouns sit at the end of a joined summary.

`remove_columns=["id", "body", "summary"]` runs on every split. Keep those three names stable.

## Model config vs trainer generate

Two different “how to decode” stories exist:

1. **`AutoConfig.from_pretrained(..., min_length=9, max_length=128, length_penalty=0.8, no_repeat_ngram_size=3, num_beams=4, dropout_rate=0.1)`**  
   Attached to the model object. Used when something calls `model.generate()` without overriding.
2. **`Seq2SeqTrainingArguments(..., predict_with_generate=True, generation_max_length=128)`**  
   Used by the trainer during `evaluate()` / `predict()`. Beams and n-gram blocking then come from the model config unless you also set `generation_num_beams` (this script does not).

In practice epoch metrics are “ROUGE of 128-token beam-4 generations on the validation silver labels.”

## `Seq2SeqTrainingArguments` sheet

| Argument | Value | Reading |
| --- | --- | --- |
| `output_dir` | `mt5-summarize-large` | checkpoints + trainer state |
| `log_level` | `error` | almost silent logs |
| `num_train_epochs` | `20` | long for a silver-label set; overfitting is likely |
| `learning_rate` | `0.0003` | 3e-4, typical Adafactor / T5 range |
| `lr_scheduler_type` | `polynomial` | comment lists the other HF names |
| `warmup_steps` | `1000` | ~1000 optimizer steps, not epochs |
| `optim` | `adafactor` | T5-paper optimizer; less VRAM than AdamW |
| `weight_decay` | `0.01` | |
| `per_device_train_batch_size` | `8` | |
| `per_device_eval_batch_size` | `8` | |
| `gradient_accumulation_steps` | `1` | effective batch = 8 per GPU |
| `evaluation_strategy` | `epoch` | one generate-pass per epoch |
| `save_strategy` | `epoch` | |
| `predict_with_generate` | `True` | required for ROUGE |
| `generation_max_length` | `128` | |
| `save_steps` | `100` | ignored when `save_strategy="epoch"` |
| `logging_steps` | `250` | mostly hidden by `log_level="error"` |
| `push_to_hub` | `False` | |
| `fp16` | `True` | CUDA only |
| `load_best_model_at_end` | `True` | |
| `metric_for_best_model` | `rouge_1_mid_fmeasure` | higher is better (default) |
| `save_total_limit` | `1` | only one checkpoint kept |

`eval_steps = 100` is commented out, which is correct when evaluation is per epoch.

## Metric used to pick the best checkpoint

`compute_metrics` loads `datasets.load_metric("rouge")` **inside** the function (once per eval). It decodes predictions and labels, restores pad ids from `-100`, sentence-tokenizes with NLTK, joins sentences with `\n` (the ROUGE-Lsum convention), and returns:

- `rouge_1_mid_fmeasure`
- `rouge_2_mid_fmeasure`
- `rouge_l_mid_fmeasure`

`mid` is the bootstrap midpoint from the legacy `rouge` metric object (`value.mid.fmeasure`). Modern `evaluate.load("rouge")` returns plain floats instead. If you upgrade the metric API, also change `metric_for_best_model`.

BERTScore is **not** computed during training.

## Saving

After `trainer.train()`:

```python
os.makedirs("./large_model", exist_ok=True)
if hasattr(trainer.model, "module"):
    trainer.model.module.save_pretrained("./large_model")
else:
    trainer.model.save_pretrained("./large_model")
```

Because `load_best_model_at_end=True`, this should be the best ROUGE-1 checkpoint, not necessarily the last epoch. The tokenizer is **not** saved next to the model. `use_model.py` / `eval.py` reload a tokenizer from `google/mt5-small` or `google/mt5-large` on the hub. That is fine as long as the hub id matches the trained size.

The `module` branch is for `DataParallel`. `Seq2SeqTrainer` on one GPU usually hits the `else`.

## What 20 epochs implies

Silver labels are peaked: many targets share T5-news phrasing (“The storm left thousands without power…”) even when the Danish bodies differ. A 20-epoch run with batch 8 can memorize that phrasing. Signs you went too far:

- validation ROUGE-1 still rises while Nordjylland ROUGE falls,
- outputs start with the same English-calque openers,
- rare proper nouns from the train dump appear on unrelated eval articles.

If you retrain, try 3–5 epochs first, or early-stop on a *Nordjylland* validation slice rather than on silver ROUGE.

## Memory knobs if the large model does not fit

Change only these, in order:

1. `per_device_train_batch_size` 8 → 2 or 1
2. `gradient_accumulation_steps` 1 → 4 or 8 (keep effective batch near 8)
3. `fp16` stay True on CUDA; do not switch to bf16 unless you have Ampere+ and have tested
4. encoder `max_length` 1024 → 512 (quality drop on long features)
5. `google/mt5-large` → `google/mt5-small` (then fix eval tokenizer)

Adafactor is already the low-VRAM optimizer choice. Do not add a second full AdamW state “to be safer.”

## Reproducibility gaps

`finetune.py` does not set:

- `seed` / `data_seed` on `TrainingArguments`
- `torch.manual_seed`
- a frozen Hugging Face `datasets` fingerprint
- `save_pretrained` for the tokenizer
- logging of the git commit or the silver-label filename

A second run will not match the first bit-for-bit. For a personal course project that is acceptable; record the hub revision and the labeled CSV hash if you care later.

## Training on the example CSVs (smoke only)

The files under `examples/data/finetune/` have the right columns but only a handful of rows. They are useful to test that `load_dataset` + `tokenize_data` still run, not to train a real model. A one-batch overfitting test would need you to point `data_files=` at those paths and drop `num_train_epochs` to 1, `fp16` to False on CPU, and `warmup_steps` to 0. That experiment is intentionally *not* wired into the course script.
