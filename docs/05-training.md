# Fine-tuning mT5

**Script:** `finetune.py`  
**Base model:** `google/mt5-large`  
**Data:** `datasets/train_dataset.csv`, `datasets/validation_dataset.csv`, `datasets/test_dataset.csv`  
**Saves:** `mt5-summarize-large/` (Trainer checkpoints) and `./large_model` (final `save_pretrained`)

mT5 is T5 trained on mC4, so the encoder already has Danish subwords. Fine-tuning here is "learn this project's silver-summary style," not "learn Danish from scratch."

## Data load

```python
train_dataset = load_dataset("csv", data_files="datasets/train_dataset.csv")["train"]
validation_dataset = load_dataset("csv", data_files="datasets/validation_dataset.csv")["train"]
test_dataset = load_dataset("csv", data_files="datasets/test_dataset.csv")["train"]
```

Hub `load_dataset("csv")` always names the split `"train"`. The script then wraps the three Arrow tables in a `DatasetDict` with keys `train`, `validation`, `test`. The `test` split is **tokenized but never passed to `Seq2SeqTrainer`**. Only `train` and `validation` are used. The test CSV is loaded so you can score it later with a copy of the eval loop if you want a teacher-fidelity number.

## Tokenization

```python
def tokenize_data(data):
    input_feature = mt5_tokenizer(data["body"], truncation=True, max_length=1024)
    label = mt5_tokenizer(data["summary"], truncation=True, max_length=128)
    return {
        "input_ids": input_feature["input_ids"],
        "attention_mask": input_feature["attention_mask"],
        "labels": label["input_ids"],
    }
```

- Source: Danish article, 1024 tokens. Longer bodies lose the tail.
- Target: Danish silver summary, 128 tokens. Longer teacher strings (multi-chunk T5 joins) lose the tail.
- Columns `id`, `body`, `summary` are removed after `map`.
- `batch_size=128` for the map only — not the train batch size.

mT5's tokenizer is SentencePiece. Spaces and Danish letters (æ ø å) are fine. You do **not** add a `summarize:` prefix in this script. The model sees raw article text.

`DataCollatorForSeq2Seq` pads batches and replaces label pad tokens with `-100` so they are ignored by the loss.

## Generation config baked into `AutoConfig`

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

These become the model's default generate settings (and affect eval generate when `predict_with_generate=True`). `length_penalty=0.8` slightly prefers shorter beams. Trigram blocking is on. `min_length=9` avoids one-word collapses.

`use_model.py` does **not** reuse this config. It generates with `num_beams=2` and `no_repeat_ngram_size=1`. Do not compare those prints to trainer metrics as if they used the same decoder.

## Trainer arguments

See [07-hyperparameters.md](07-hyperparameters.md) for the full table. The important ones:

| Arg | Value | Why it is there |
| --- | --- | --- |
| `num_train_epochs` | 20 | Small silver set; long schedule with Adafactor |
| `learning_rate` | `3e-4` | Typical Adafactor + mT5 starting point |
| `lr_scheduler_type` | `polynomial` | Decays to ~0 by the end of training |
| `warmup_steps` | 1000 | Protects the pretrained multilingual features |
| `optim` | `adafactor` | Memory-friendly; standard for T5 |
| `per_device_train_batch_size` | 8 | mT5-large + 1024 source is VRAM-heavy |
| `fp16` | True | Assumes a CUDA GPU that likes fp16 (Ampere+ is happier with bf16; this script does not set bf16) |
| `evaluation_strategy` / `save_strategy` | `epoch` | One val pass and one checkpoint per epoch |
| `load_best_model_at_end` | True | Restores best `rouge_1_mid_fmeasure` |
| `save_total_limit` | 1 | Disk saver; you only keep the latest / best rotation |
| `predict_with_generate` | True | Needed so `compute_metrics` sees decoded strings, not logits |
| `generation_max_length` | 128 | Matches target truncation |
| `push_to_hub` | False | Local-only course run |

`save_steps = 100` is ignored when `save_strategy="epoch"`.

## Metrics during training

`compute_metrics`:

1. Decode predictions and labels (`-100` → pad).
2. `nltk.sent_tokenize` each string and join sentences with newlines (the ROUGE-Lsum convention).
3. `datasets.load_metric("rouge")` with `use_aggregator=True`.
4. Log `rouge_1_mid_fmeasure`, `rouge_2_mid_fmeasure`, `rouge_l_mid_fmeasure`.

`datasets.load_metric` is the **legacy** API (the `datasets` metrics hub). Current Transformers examples prefer `evaluate.load("rouge")`. Both can work; the legacy path needs the `rouge` extra / `rouge-score` package.

These ROUGE numbers are against **silver** validation labels, not journalist abstracts. They measure "how close is mT5 to the teacher pipeline," not "how good is Danish news summarization."

BERTScore is **not** computed in `finetune.py`. It only appears in `eval.py`.

## Saving

After `trainer.train()`:

```python
os.makedirs("./large_model", exist_ok=True)
(trainer.model.module if hasattr(trainer.model, "module") else trainer.model
 ).save_pretrained("./large_model")
```

The `module` branch covers `DataParallel`. The tokenizer is **not** saved beside `./large_model` in this snippet. When you reload, `use_model.py` / `eval.py` load the tokenizer from `google/mt5-small` or `google/mt5-large` on the Hub. That is fine as long as you did not add tokens. If you did, save the tokenizer too:

```python
mt5_tokenizer.save_pretrained("./large_model")
```

## `small_model` vs `large_model`

| Path | Produced by | Consumed by |
| --- | --- | --- |
| `./large_model` | `finetune.py` (`mt5-large`) | nothing in the repo unless you change paths |
| `small_model` | not produced by any checked-in script | `use_model.py`, `eval.py` |
| `mt5-summarize-large/` | Trainer `output_dir` | checkpoints / logs |

If you want the eval scripts to score the model you just trained, either:

- change `from_pretrained("small_model")` to `from_pretrained("./large_model")` and load `google/mt5-large` as the tokenizer name, or
- run a second fine-tune with `model_name = "google/mt5-small"` and `save_pretrained("small_model")`.

`examples/configs/finetune_mt5_large.yaml` and `finetune_mt5_small.yaml` list both recipes in one place. The Python scripts do not read those YAML files; they are documentation you can copy from.

## Hardware sketch

mT5-large (1.2B) + 1024 source + 128 target + beam-4 generate at eval-epoch is the heavy step. The 2023 run assumed a CUDA GPU with fp16. If you only have a small GPU, use the small YAML as a guide: `google/mt5-small`, shorter source length, smaller beams.

Do not try to run `finetune.py` as-is on CPU. The examples never call it.
