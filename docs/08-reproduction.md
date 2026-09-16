# Reproduction

Two reproductions exist. They are not interchangeable.

## A. Course GPU run (historical)

This is what the README in 2023 described. It needs CUDA, CTranslate2
models, and the original 10k-article CSV (not in git).

1. Convert Marian checkpoints with `Ctranslate_converter.py`.
   **Scar:** only `opus-mt-en-da` is exported. Also convert
   `Helsinki-NLP/opus-mt-da-en` into `models/opus-mt-da-en_ct2` or hop 1
   cannot start.
2. Place the Danish CSV at `10000_articles_without_linebreaks.csv` with
   columns `id` and `article text`.
3. Run `translate.py`, then `summary.py` (remove the `[:10]` slice for a
   full pass), then `translate_back.py`.
4. Split `labeled_dataset_ml80_rp5.0.csv` into `datasets/train_dataset.csv`,
   `validation_dataset.csv`, and `test_dataset.csv` yourself. No splitter
   is committed.
5. Run `finetune.py` on a GPU that can hold mT5-large at batch 8 with
   fp16. If loss goes NaN, drop fp16.
6. To eval the checkpoint you actually trained, point `eval.py` at
   `./large_model` and keep the tokenizer name aligned, or train
   mT5-small instead.

Approximate disk: OPUS-MT CT2 exports are small; mT5-large and its
trainer output are not. The course machine had a GPU. This cloud checkout
does not attempt that path.

## B. Pakhuset CPU lab (this branch)

No weights. Fictional Toftevig articles only.

```bash
python -m pip install -e ".[dev]"
python -m pakhus scars
python -m pakhus atlas --article tof-001
python -m pakhus hops
python -m pakhus report
python -m pytest
```

Equivalent example scripts live under `examples/`. They write CSV and an
HTML atlas under `examples/report/`.

### What this does *not* reproduce

- OPUS-MT quality, T5 news style, or mT5 ROUGE on Nordjylland.
- Runtime of CTranslate2 batching.
- The exact NLTK punkt cuts (the lab uses `pakhus.sentences` plus a naive
  splitter for contrast).
- Hugging Face hub downloads. The original scripts will still try to
  download if you run them as-is.

### What it does reproduce

- Mixed character / token long-split.
- Empty-list behaviour of the course packer.
- Repacking across hops on sentence-aligned fixtures.
- Concatenated pane briefs vs a 128-token label cap.
- CSV column contracts, including `article text` with a space.
- The scar inventory of the frozen root files.

If A and B ever disagree on a *control-flow* question (how many panes,
whether an empty window appears, whether `mio. kr.` splits), B is the
one with tests. If they disagree on *string quality*, A wins — B's
English is canned.
