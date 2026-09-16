# Labeling pipeline

The course project does not start from human-written Danish summaries.
It *constructs* silver labels with a round-trip through English, then
fine-tunes `google/mt5-large` on the resulting Danish `(article, summary)`
pairs.

```
Danish article
      │
      ▼
opus-mt-da-en  (CTranslate2)     translate.py
      │
      ▼
English article
      │
      ▼
T5 news summarizer               summary.py
      │
      ▼
English summary  (max 80 tokens, repetition_penalty=5.0)
      │
      ▼
opus-mt-en-da  (CTranslate2)     translate_back.py
      │
      ▼
Danish silver summary
      │
      ▼
manual CSV split                 datasets/{train,validation,test}_dataset.csv
      │
      ▼
mT5-large fine-tune              finetune.py
```

That design is a reaction to the data situation in 2023: large Danish
news corpora existed, but clean abstractive summaries in Danish were
scarce compared with English. English had a ready news T5
(`mrm8488/t5-base-finetuned-summarize-news`). The cheap way to reuse it
was to translate, summarize, and translate back.

## Why CTranslate2

`Ctranslate_converter.py` wraps Hugging Face OPUS-MT checkpoints as
CTranslate2 models. The converter in the repo currently **only exports
`Helsinki-NLP/opus-mt-en-da`**. The DA→EN conversion is present but
commented out. `translate.py` still expects `models/opus-mt-da-en_ct2`,
so a first-time run needs that block turned back on (or a second
converter invocation). Commented NLLB converters are leftovers from an
earlier comparison and are not part of the final workflow.

## Article chunking

OPUS-MT was trained with a 512-token ceiling. A Danish news article is
often longer than that, so every translation script cuts the input
before calling `translate_batch`.

The control flow, shared by `translate.py` and `summary.py`:

1. Sentence-split the article (`nltk.sent_tokenize`).
2. Measure each sentence with the model tokenizer.
3. If a sentence itself is over `text_max_length` (90% of 512 in the
   translation scripts, 512 flat in `summary.py`), run
   `split_long_sentence`.
4. Pack the resulting units into lists whose token lengths sum to at
   most `text_max_length`.
5. Translate or summarize each list, then concatenate.

`split_long_sentence` walks `nltk.word_tokenize` output and accumulates
`len(word) + 1`. That is a **character** budget, not a token budget.
After the split, the script re-encodes each chunk with the real
tokenizer. The two measures can disagree on space-heavy Danish
compounds.

There is a second quirk: in the committed code, a comma, semicolon or
colon **always** flushes the current chunk while the running character
count is still under the limit. The comments talk about splitting long
sentences; the `if` as written splits on every list comma. The offline
reconstruction in `examples/text_chunking.py` exposes that behaviour as
`mode="historical"` and a tighter `mode="near_limit"` that only uses
those marks once the chunk is close to the budget.

`translate_back.py` is simpler. Summaries are short, so it only packs
sentences and never calls `split_long_sentence`.

## What each script writes

| Step | Script | Default input | Default output |
| --- | --- | --- | --- |
| Convert | `Ctranslate_converter.py` | Hugging Face model id | `models/opus-mt-*-ct2` |
| DA→EN | `translate.py` | `10000_articles_without_linebreaks.csv` | `translated_articles.csv` |
| Summarize | `summary.py` | `translated_articles.csv` | `summarized_file_ml80_rp5.0.csv` |
| EN→DA | `translate_back.py` | the summarized file | `labeled_dataset_ml80_rp5.0.csv` |

Column-level contracts are in [dataset-schema.md](dataset-schema.md).
The same names are encoded in `examples/schema.py` so the sample CSVs
can be checked mechanically.

## Debug leftover in `summary.py`

```python
df = pd.read_csv(input_file_path)[:10]
```

A full labeling run over ~10k articles will silently summarize the first
ten rows unless that slice is removed. The filename
`summarized_file_ml80_rp5.0.csv` records the generation knobs
(`max_length=80`, `repetition_penalty=5.0`), not the row count.

## Offline stand-in

`examples/toy_pipeline.py` walks the same stage filenames and schemas
without downloading models. It packs sentences with a word-count budget
and writes extractive Danish summaries. That is **not** a substitute for
the silver-label quality of T5 + OPUS-MT; it exists so the control flow
and CSV contracts can be exercised on a laptop. See
[examples/README.md](../examples/README.md).
