# Design notes

These notes record the method implied by the 2023 scripts. They are not
a substitute for a course report; they exist so a later reader can see
*why* the repository is shaped the way it is.

## Problem

Danish abstractive summarization had far less labeled news data than
English in 2023. Human headlines and ledes also tend to be extractive
or only loosely grounded in the body, which makes supervised training
noisy. The project therefore treats **label scarcity** as the main
constraint and spends most of the code on manufacturing Danish
article–summary pairs rather than on a custom architecture.

## Pivot through English

The silver-label path is:

```
Danish body  →  English body  →  English summary  →  Danish summary
```

The middle step uses `mrm8488/t5-base-finetuned-summarize-news`, an
English news T5 that already knows how to write short abstractive
ledes. Danish-specific summarizers existed by then (notably DanSumT5,
fine-tuned mT5 on a cleaned DaNewsroom subset; Kolding et al., NoDaLiDa
2023), but this course project instead **imports** English summarization
quality through machine translation.

That choice has a clear cost: every factual error in OPUS-MT or in the
English T5 is written into the Danish target. The fine-tune then
imitates that noisy target. The evaluation scripts therefore score
against **human** Nordjylland-News summaries, not against the silver
labels, so the reported ROUGE / BERTScore numbers measure transfer to
real Danish news writing rather than self-agreement with the pipeline.

## Why CTranslate2

OPUS-MT from Helsinki-NLP is small enough to run in Transformers, but
the dataset is “10,000 articles” in the default filename and the
forward pass is sentence-batched. CTranslate2’s `translate_batch` is
the throughput path: convert once, then reuse a quantized/optimized
runtime for both directions.

Only the en→da converter is active in `Ctranslate_converter.py`. The
da→en conversion is present but commented out. That is almost certainly
an incomplete edit rather than a design decision; both directions are
required.

## Windowing instead of truncation

News bodies in the Nordjylland-News collection routinely exceed 512
sentencepiece tokens (the public card lists bodies up to tens of
thousands of characters). Blind truncation would drop the tail of the
article, which is often where Danish local news puts quotes and
outcomes.

`translate.py` and `summary.py` therefore:

1. Sentence-split with NLTK `punkt`.
2. Break leftover long sentences on `,` / `;` / `:` or on a word
   budget.
3. Pack sentences into a running window of `0.9 * max_length` tokens.
4. Translate or summarize each window independently.
5. Concatenate the window outputs with a space.

`summary.py` can therefore emit a summary that is a **concatenation of
chunk summaries**, not a single document-level lede. That is visible in
the `ml80` filename: each chunk is capped at 80 tokens, so a long
article produces a longer, more extractive-feeling silver target.

`finetune.py` later truncates the Danish body to 1024 tokens and the
target to 128 tokens. The silver labels and the fine-tune objective are
therefore not length-aligned. A later cleanup would either summarize
chunks hierarchically (chunk summaries → one summary) or raise the
decoder `max_length` to match the concatenated silver targets.

## Model size split

| Script | Base model | Local directory |
| --- | --- | --- |
| `finetune.py` | `google/mt5-large` | `./large_model` |
| `eval.py` | `google/mt5-small` | `small_model` |
| `use_model.py` | `google/mt5-small` | `small_model` |

Training the large model and evaluating the small one is another
incomplete pairing. The intended experiment was almost certainly
“train both sizes, report both.” The scripts as checked in only train
large and only load small.

## Optimization choices

`finetune.py` uses Adafactor, a polynomial scheduler, 1000 warmup
steps, and `fp16`. That combination is the standard “fine-tune T5
without a giant Adam state” recipe from the T5 / mT5 papers. Batch size
8 with `gradient_accumulation_steps=1` is a single-GPU setting; the
effective batch is 8 sequences of 1024 encoder tokens.

`length_penalty=0.8` and `no_repeat_ngram_size=3` on the mT5 config
push generations slightly shorter and less repetitive than the English
T5’s `repetition_penalty=5.0`. The two stages are not sharing a
decoding policy.

## Evaluation design

ROUGE-1/2/L mid F-measure is the training selection metric
(`metric_for_best_model="rouge_1_mid_fmeasure"`). `eval.py` adds
BERTScore with `lang='da'` and `model_type="xlm-roberta-large"`. That
matches the DanSumT5 reporting style (ROUGE plus BERTScore) even though
this repository does not use the DanSum training set.

`datasets.load_metric("rouge")` and `datasets.load_metric("bertscore")`
were already on the deprecation path in late 2023; `evaluate.load` is
the current equivalent. The metric math is the same.

## What a follow-up would change

In decreasing order of impact on label quality:

1. Convert **both** OPUS directions and drop NLLB-style language
   prefixes (`eng_Latn` / `dan_Latn`) that OPUS-MT does not use.
2. Hierarchical English summarization so each article yields one lede,
   not a stitch of chunk summaries.
3. Filter silver labels (length ratio, source overlap, language ID,
   optional NLI consistency) before fine-tuning.
4. Train and evaluate the same mT5 size.
5. Align decoder `max_length` with the label distribution.
