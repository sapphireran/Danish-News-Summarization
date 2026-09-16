# Reproducing a personal rerun

This is a checklist, not a promise that 2023 numbers will come back.
The original lab image, dump, and random seeds were not frozen.

## GPU path

1. Create a virtualenv and install [`../requirements.txt`](../requirements.txt)
   against a CUDA `torch` wheel that matches the machine.
2. `python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"`
3. Uncomment both OPUS-MT directions in `Ctranslate_converter.py`.
4. Convert: `python Ctranslate_converter.py`.
5. Place the Danish dump at `10000_articles_without_linebreaks.csv`.
6. Run `translate.py`.
7. Edit `summary.py` to drop `[:10]`. Run it.
8. Run `translate_back.py`.
9. Split with `examples/scripts/split_labeled_dataset.py` into `datasets/`.
10. Decide `google/mt5-large` vs `mt5-small` from VRAM, then run
    `finetune.py` (set `fp16=False` on CPU — and do not expect a large
    run to finish on CPU).
11. Point `eval.py` / `use_model.py` at the directory you actually saved
    (`large_model` vs `small_model`) and at one Nordjylland dump, not two.
12. Record package versions and the number of scored examples next to
    the metrics.

## CPU path (contracts only)

```bash
python3 -m unittest discover -s examples/tests -t examples
python3 examples/scripts/validate_pipeline_config.py --all
python3 examples/scripts/dry_run_pipeline.py \
  --input examples/data/sample_articles.csv \
  --output-dir /tmp/danish-news-dry-run \
  --split
```

That path never touches Hugging Face. It is the one this repository
can still run on a laptop or a cloud agent without weights.

## What "done" looked like in the course

A written report plus:

- a trained mT5 checkpoint
- qualitative prints from `use_model.py`
- ROUGE / BERTScore from `eval.py`
- a short discussion of pivot-language noise

The report itself is not in this git history. These notes are the
personal reconstruction of the engineering half.
