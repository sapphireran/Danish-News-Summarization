# Evaluation

There are three different "how good is it?" paths in this repo. They
do not measure the same thing.

| Path | Script | Data | Metrics | Use it for |
| --- | --- | --- | --- | --- |
| Train-time | `finetune.py` `compute_metrics` | silver `validation_dataset.csv` | ROUGE-1/2/L mid F | checkpoint selection |
| Qualitative | `use_model.py` | Nordjylland **mini** | eyeball | "does it even look Danish?" |
| Reported | `eval.py` | Nordjylland **full test** | ROUGE + BERTScore | the number you write down |

Mixing those three into one table without labels is how a project
report becomes impossible to reproduce.

## ROUGE

Both `finetune.py` and `eval.py` decode, restore pad ids, run
`nltk.sent_tokenize`, join sentences with `\n` (the rouge-score
package's sentence convention), and ask for the **mid** F-measure.

ROUGE-1/2 are overlap of unigrams / bigrams. ROUGE-L is longest common
subsequence. For Danish they are noisy:

- Compounds (`folkebiblioteker` vs `biblioteker`) miss a unigram match
  even when a reader would accept the shorter word.
- Silver labels that already came through English T5 tend to share
  function words with mT5's output, which inflates ROUGE-1 without
  proving factual fidelity.

Treat ROUGE-1 as a *training* signal (it is what
`metric_for_best_model` uses) and not as a claim about usefulness.

## BERTScore

`eval.py` additionally loads BERTScore with:

```python
lang="da"
model_type="xlm-roberta-large"
```

and reports mean precision, recall, and F1.

BERTScore is kinder to paraphrases than ROUGE, which is what you want
for abstractive news. It is also slow and will download
`xlm-roberta-large` the first time. The language code `'da'` matters;
leaving it at the English default silently scores Danish with the
wrong fallback.

## Qualitative checklist (`use_model.py`)

The script prints five batches of:

1. input article (`input_text` from the Hub set)
2. reference (`target_text`)
3. generation (`model.generate`, 2 beams, `no_repeat_ngram_size=1`)

Read them with three questions, in order:

1. **Language.** Is the output Danish, or did mT5 fall back to English
   or a mixed token salad? (Common if the tokenizer/model sizes differ.)
2. **Entities.** Do municipality names, kroner amounts, and dates match
   the input? Silver-label models often drop or round numbers.
3. **Coverage vs. fidelity.** A dek that only restates the lede is
   boring but honest. A dek that adds a cause the article never stated
   is a problem even if ROUGE likes the shared words.

`no_repeat_ngram_size=1` forbids repeating any token. That is harsher
than the training config (`no_repeat_ngram_size=3`) and will mutilate
legitimate pairs like `kommune` … `kommune`. Do not quote those strings
as the model's real style.

## Numbers this repository does **not** claim

The 2023 course report is not checked in. This tree therefore does
**not** invent a ROUGE table. If you reproduce the run, record:

```text
split:                 nordjylland test | silver validation | silver test
checkpoint:            large_model | small_model | hub id
generate kwargs:       beams / max_length / no_repeat
rouge_1_mid_fmeasure:
rouge_2_mid_fmeasure:
rouge_L_mid_fmeasure:
bertscore_f1:
date / commit / GPU:
```

Put the block next to the checkpoint, not only in a slide.

## Dry-run "metrics"

`examples/dry_run_pipeline.py` writes `compression_stats.json` with
word counts and summary/body ratios for the fictional sample set.
Those are **not** quality metrics. They exist to calibrate how
aggressive a silver-label summary looks (see the note printed at the
end of that script). A real eval still needs `eval.py` and a GPU.
