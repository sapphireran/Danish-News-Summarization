# Design notes

This is a retrospective on the 2023 course code, not a rewrite of it.
The root scripts stay as they were handed in. The notes below are the
reasons the pipeline looks the way it does, plus the sharp edges that
showed up while documenting it.

## Why pivot through English?

Danish abstractive summarization in 2023 had fewer ready news-domain
checkpoints than English. The project had:

* a large pile of unlabeled Danish news
* a usable DA↔EN MarianMT pair (OPUS-MT)
* an English T5 already fine-tuned on news summaries
* mT5 as a multilingual student that can be trained on the resulting
  silver pairs

The bet is that **translation error + English news style** is still a
better supervision signal than unsupervised Danish objectives alone.
The cost is well known: names, syntax, and information can drift twice
(DA→EN, then EN→DA), and the English T5 is biased toward English
journalistic compression (lead-like summaries, 80-token cap per window).

Concatenating per-window T5 outputs makes the silver label **coverage-heavy**:
it tries to summarize each slice rather than drop tail paragraphs. That
is closer to multi-document stitching than to a single headline. Fine-tuning
mT5 on those labels teaches that style. Nordjylland gold, by contrast, is
often a short news abstract. A length gap between silver labels and gold
targets is expected.

## Silver labels are not gold

Nothing in `labeled_dataset_ml80_rp5.0.csv` was written by a journalist
for this project. Downstream ROUGE on Nordjylland is therefore a transfer
number. A high ROUGE against the silver file would only show that mT5
copied the noisy teacher.

The fixture pair `sample_labeled.csv` vs `sample_references.csv` exists to
make that distinction visible on eight rows: the scorer is allowed to
be mediocre when the two human strings disagree in wording.

## Windowing vs. 512 tokens

MarianMT and T5-base were trained around 512 subword tokens. A Danish
broadsheet article is longer. The course scripts:

1. sentence-split
2. break leftover long sentences on `,` / `;` / `:` then on words
3. greedy-pack until the running length exceeds a 90% budget

A quirk: `split_long_sentence` increments `len(word) + 1` (characters)
and compares that to `text_max_length` derived from the **token** limit.
On Danish, characters and SentencePiece tokens are not the same scale, so
the original splitter is neither a pure char cap nor a true token cap.
`danish_news.chunking` keeps `unit="chars"` to reproduce that mix and
`unit="words"` as the default for examples.

NLTK `punkt` is also English-centric. Danish `f.eks.` / `mio. kr.` will
over-segment unless abbreviations are protected. The CPU splitter
maintains an explicit abbreviation list for that reason.

## CTranslate2 converter vs. translate.py

`Ctranslate_converter.py` as committed converts `opus-mt-en-da` only.
`translate.py` loads `models/opus-mt-da-en_ct2`. The README still says
both models are produced in step 1. Anyone reproducing from the scripts
needs to uncomment the `opus-mt-da-en` block (the lines are already
there).

The converter also has NLLB experiments commented out. Mixing NLLB
language prefixes with OPUS-MT tokenizers (as `translate.py` still does)
is leftover from those experiments.

## `summary.py` only processes ten rows

```python
df = pd.read_csv(input_file_path)[:10]
```

That slice is fine for a smoke test and wrong for a 10k silver set.
Remove it for a full run. The output name `summarized_file_ml80_rp5.0.csv`
does not record the row count, so a ten-row file and a 10k-row file look
the same on disk.

## Fine-tune script vs. eval script

* `finetune.py` trains `google/mt5-large` into `./large_model`.
* `use_model.py` and `eval.py` load `small_model` with tokenizer
  `google/mt5-small`.

Those are two different student models. Align the paths before comparing
a training log with an `eval.py` dict.

Other API drift since 2023:

* `use_auth_token=False` → `token=None` (or omit)
* `evaluation_strategy` → `eval_strategy`
* `datasets.load_metric` → `evaluate.load`
* `Seq2SeqTrainer(..., tokenizer=...)` → `processing_class=`

The course scripts were not updated for those renames. They may still
run on the Transformers version used in the course environment and warn
or fail on current releases.

## What this documentation pass does not change

* No GPU training code was rewritten in place.
* No company or third-party news text was added.
* The glossary backend is deliberately dumb; improving it is not a
  substitute for OPUS-MT.

The useful remaining work, if the GPU path is revived, is: convert both
OPUS directions, drop NLLB prefixes, remove the `[:10]` slice, and point
eval at the checkpoint you actually trained.
