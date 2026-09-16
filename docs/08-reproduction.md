# Reproducing the 2023 GPU pipeline

The Sejerø desk is enough to study the hops. Rebuilding the course model
needs a machine that was not assumed when these notes were written.

## What git does not contain

- The 10 000-article Danish dump (`10000_articles_without_linebreaks.csv`)
- Converted CTranslate2 directories under `models/`
- `datasets/train_dataset.csv` and the other fine-tune splits
- `./large_model` and `small_model`
- Trainer output `mt5-summarize-large/`

`.gitignore` keeps those names out on purpose.

## Approximate environment

The 2023 scripts import:

```
nltk
numpy
pandas
torch
tqdm
transformers
ctranslate2
datasets
evaluate
```

`requirements.txt` pins a readable set. It is not a lockfile from the
course machines. `use_auth_token=False` on the OPUS tokenizers is a
deprecated Transformers flag; current releases want `token=False`.

## Order of operations

1. Uncomment the `opus-mt-da-en` convert in `Ctranslate_converter.py`
   or convert that model by hand. The committed file only writes
   `models/opus-mt-en-da_ct2`.
2. Place the raw CSV next to `translate.py`.
3. Run `translate.py` → `summary.py` → `translate_back.py`.
4. **Remove `df[:10]` in `summary.py`** before a full run.
5. Split `labeled_dataset_ml80_rp5.0.csv` into
   `datasets/train_dataset.csv`, `validation_dataset.csv`,
   `test_dataset.csv` with columns `id`, `body`, `summary`.
6. Run `finetune.py` on a GPU that can host `mt5-large` with batch 8
   and fp16. The 2023 recipe used 20 epochs and Adafactor.
7. For printed samples, prefer the training generation settings
   (`no_repeat_ngram_size=3`) over `use_model.py`'s
   `no_repeat_ngram_size=1`.
8. Evaluate on
   `alexandrainst/nordjylland-news-summarization` (`eval.py`) and
   look at the mini split only as a smoke test.

## Ethics, again

Silver labels are model outputs. They can invent numbers, flip
negation, and drop speakers. The public Nordjylland set is a better
judge of *Danish news summarization* than the silver CSV is. The Sejerø
oracle column exists to keep that distinction visible on a laptop.
