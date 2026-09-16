# Reproduction notes

A clean re-run of the 2023 GPU pipeline needs weights, the original article dump, and a CUDA machine. The checked-in `examples/` path needs none of those.

## Two reproduction targets

### A. Documentation / schema (this PR)

```bash
python examples/run_all.py
```

Or the individual steps:

```bash
python -m pip install pandas pyyaml   # or: pip install -r requirements.txt
python examples/chunking/demo_chunking.py
python examples/validation/validate_samples.py
python examples/inspection/inspect_dataset.py
python examples/inspection/print_pipeline_io.py
```

Expected: `run_all.py` (and each step) exits 0. `validate_samples.py` prints one `OK` line per sample CSV.

### B. Full silver-label + mT5 run (original course path)

1. GPU with enough VRAM for mT5-large fp16 at 1024 / 128 (or switch the script to `mt5-small`).
2. `pip install -r requirements.txt` with a CUDA wheel for `torch` and a matching `ctranslate2`.
3. `nltk.download("punkt")` (already invoked in several scripts).
4. Place `10000_articles_without_linebreaks.csv` next to `translate.py`.
5. Uncomment da-en conversion in `Ctranslate_converter.py` and run it.
6. Remove `[:10]` in `summary.py`.
7. Run `translate.py` → `summary.py` → `translate_back.py`.
8. Split into `datasets/*.csv` ([02-datasets.md](02-datasets.md)).
9. Run `finetune.py`.
10. Point `use_model.py` / `eval.py` at the directory you actually saved, or fine-tune a small model into `small_model`.

## Environment drift since 2023

| Then | Now (typical) |
| --- | --- |
| `transformers` 4.3x, `use_auth_token=False` | `token=None`; `use_auth_token` warns or errors |
| `evaluation_strategy=` | `eval_strategy=` in recent TrainingArguments |
| `datasets.load_metric` | `evaluate.load` |
| `from_pretrained(..., src_lang=...)` on Marian | unused kwargs may error on strict versions |
| fp16 on older GPUs | prefer `bf16=True` on Ampere / Hopper |

If a script fails on an argument name, change the *script*, not the YAML notes, and mention the Transformers version in your commit.

## Caches

Default Hub cache is `~/.cache/huggingface/`. CTranslate2 conversion writes under `models/`. Trainer writes `mt5-summarize-large/`. All of these are gitignored.

Set `HF_HOME` / `TRANSFORMERS_CACHE` if the home volume is small.

## Determinism

None of the root scripts seed `random`, `numpy`, or `torch`. CTranslate2 and T5 generate will drift across hardware. For a paper-style rerun you would add:

```python
import random, numpy as np, torch
random.seed(2023)
np.random.seed(2023)
torch.manual_seed(2023)
```

and still not get bit-identical Marian output.

## Checklist before claiming a rerun

- [ ] Both CTranslate2 model dirs exist
- [ ] `translated_articles.csv` row count equals the input dump
- [ ] `summary.py` was not left on `[:10]`
- [ ] Labeled row count equals translated row count (minus intentional filters)
- [ ] Train/val/test ids are disjoint
- [ ] `./large_model/config.json` `architectures` matches the tokenizer you load at eval
- [ ] Nordjylland metrics and silver-val metrics are stored as separate JSON files
- [ ] No copyrighted full-text CSV was committed

## What this repo will never reproduce for you

- The original 10k dump
- The 2023 wandb / TensorBoard curves (not checked in)
- Bit-identical silver summaries
- A Hub model card — nothing is pushed (`push_to_hub = False`)
