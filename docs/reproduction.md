# Reproducing the project

Two tracks:

1. **Offline examples** — no model downloads, stdlib + the files in this
   repo. This is what the tests cover.
2. **Neural 2023 pipeline** — CTranslate2, Transformers, a GPU, and
   datasets that are not in git.

## Offline track (recommended first)

Python 3.11+ is enough. From the repo root:

```
python3 -m unittest discover -s tests -v
python3 examples/write_sample_csvs.py
python3 examples/schema_check.py
python3 examples/chunking_demo.py --max-length 40
python3 examples/toy_pipeline.py
python3 examples/compare_summaries.py
python3 examples/inspect_samples.py
```

`write_sample_csvs.py` regenerates `examples/data/*.csv` from
`examples/sample_catalog.py`. The committed CSVs should already match;
the command is there so a catalog edit stays consistent.

`toy_pipeline.py` writes under `examples/output/` (gitignored).

## Neural track

Approximate dependency stack from the APIs the scripts call:

```
pip install -r requirements.txt
```

Then, on a machine with CUDA and disk for model weights:

1. Uncomment the DA→EN converter in `Ctranslate_converter.py` and run it
   so both `models/opus-mt-da-en_ct2` and `models/opus-mt-en-da_ct2`
   exist.
2. Place `10000_articles_without_linebreaks.csv` next to `translate.py`
   with columns `id`, `article text`.
3. `python translate.py`
4. Remove the `[:10]` slice in `summary.py` if you want more than ten
   rows, then `python summary.py`.
5. `python translate_back.py`
6. Split `labeled_dataset_ml80_rp5.0.csv` into
   `datasets/{train,validation,test}_dataset.csv` (same columns:
   `id,body,summary`). No official ratio is recorded; a 80/10/10 split
   by `id` is a reasonable default.
7. `python finetune.py` (mT5-large, 20 epochs, Adafactor, fp16).
8. Point `use_model.py` / `eval.py` at the checkpoint you actually
   trained (`./large_model` or a copied `small_model`).
9. Confirm the Nordjylland column names before `eval.py` (see
   [evaluation.md](evaluation.md)).
10. `python use_model.py` and `python eval.py`.

Step 4 is the one people skip. Step 8 is the one that silently evaluates
the wrong model.

## Hardware sketch

These are order-of-magnitude notes, not measurements from a shared
cluster.

| Job | What dominates |
| --- | --- |
| OPUS-MT CTranslate2 over 10k articles | GPU memory ~1–2 GB; time is batching / I/O |
| T5-base news summarizer | Similar; `summary.py` does not batch across articles |
| mT5-large, batch 8, 1024 source tokens | A single consumer 24 GB GPU is tight; fp16 is assumed |
| BERTScore with `xlm-roberta-large` | Extra download + a full pass over the Nordjylland test set |

The offline examples exist specifically so none of that is required to
read the repository.

## What cannot be reproduced from git alone

- The original 10k-article dump
- The exact train/val/test partition of the silver labels
- The trained `large_model` / `small_model` weights
- The numerical ROUGE / BERTScore table from the 2023 report (not
  committed)

If those artefacts still exist on an old disk, keep them *out* of this
public repo unless the dump's license is clear. The invented samples in
`examples/data` are original text and are safe to keep.
