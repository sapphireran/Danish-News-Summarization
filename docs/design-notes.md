# Design notes and caveats

Personal notes from the 2023 ITU Advanced NLP / Deep Learning final project.
The goal was a Danish news summarizer when labeled Danish data was scarce and
English news T5 models were easy to download.

## Why silver labels instead of human annotation

Hand-labeling thousands of Danish news articles was not realistic for a
course deadline. The workaround:

1. Translate Danish news to English (OPUS-MT).
2. Summarize in English (T5 news).
3. Translate the summary back to Danish (OPUS-MT).
4. Fine-tune mT5 as if those pairs were gold.

This is a cross-lingual knowledge-transfer recipe, not a claim that the
labels are journalist quality. Errors compound:

- a mistranslated entity in step 1 can become a confident wrong summary
- T5 may drop Danish-specific context that survived translation
- the back-translation can reintroduce English word order or calques
- mT5 then imitates that style

Use the public Nordjylland News numbers in `eval.py` as the external check.

## Why CTranslate2

The article dump is long-form news. A naive Transformers generate loop over
10k documents, each split into several 512-token windows, is a lot of
decoder steps. CTranslate2's `translate_batch` was the practical way to
finish the da→en and en→da passes on one GPU.

The conversion step is a one-time cost. The tokenizer still comes from
Transformers, so the installation needs both stacks.

## Why articles are sentence-packed, not naively truncated

OPUS-MT and the English T5 both sit on a 512-token encoder. Truncating a
Danish news article at 512 tokens throws away the tail, which is often where
the "what happens next" material lives.

The course scripts instead:

1. Sentence-split with NLTK.
2. Force-split oversized sentences on commas / semicolons / colons, then on
   raw word budget.
3. Pack sentences into windows of `0.9 * 512` tokens.

The 0.9 factor is a safety margin for special tokens and slight tokenizer
disagreement between length checks and the actual encoder.

`examples/chunking.py` reimplements that packing so it can be tested without
GPU weights. It is a reference, not a behavior-for-behavior copy of every
edge case in `translate.py` vs `summary.py` (those two files already differ
slightly).

## Why mT5 and not a Danish-only encoder-decoder

mT5 can read Danish `body` text directly at train time. After silver labels
exist, there is no need to keep translating articles at inference. That was
the point of the project: pay the translation cost once, then ship a
Danish-in, Danish-out model.

`mt5-large` was the ambitious training run. `use_model.py` and `eval.py`
still name `small_model` and `google/mt5-small` for the tokenizer, which
suggests a smaller run was used for quicker inspection. Document whichever
directory you actually load.

## Known issues in the committed scripts

These are recorded so a future personal rerun does not rediscover them the
hard way.

1. **`Ctranslate_converter.py` only converts en→da.** The da→en convert
   calls are commented out, but `translate.py` needs that directory.

2. **`summary.py` slices `[:10]`.** A full label run must remove that line.

3. **NLLB language prefixes on OPUS-MT.** `target_prefix=[[tgt_lang]]` with
   `eng_Latn` / `dan_Latn` is NLLB API shape. Confirm decode output before a
   10k-article job.

4. **`translate.py` tokenizer kwargs.** `src_lang="dan_Latn"` is passed to
   an OPUS-MT tokenizer. Harmless if ignored; confusing if you expect NLLB
   behavior.

5. **`use_model.py` print alignment.** Dataset row `i` is not dataloader
   batch `i` once `batch_size=2`.

6. **`eval.py` drops the last incomplete batch.** `dataloader_drop_last=True`
   can hide rows on the public test set.

7. **Deprecated Transformers / datasets APIs.** `use_auth_token`,
   `evaluation_strategy`, `datasets.load_metric`, and
   `Seq2SeqTrainer(..., tokenizer=...)` all warn or fail on current library
   versions. A rerun will need a pinned 2023-era stack or a small port.

8. **`fp16=True`.** CPU smoke tests will not start until this is flipped.

9. **No tokenizer saved with `./large_model`.** Load the matching
   `google/mt5-*` tokenizer explicitly.

10. **Silver summaries can exceed the 128-token label cap** after chunk
    concatenation in `summary.py`.

## What this archive is not

This repository is a personal course project. It is not production news
software, not a company artifact, and not a trained-model release. The
original 10k-article file is not redistributed here.
