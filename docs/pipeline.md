# Labeling pipeline

The four root scripts that build silver labels are `Ctranslate_converter.py`, `translate.py`, `summary.py`, and `translate_back.py`. This page is the narrative; [script-reference.md](script-reference.md) is the I/O cheat sheet.

## Stages

### 0. Convert OPUS-MT to CTranslate2

`TransformersConverter` from CTranslate2 reads a Hugging Face seq2seq checkpoint and writes a fast inference directory.

The checked-in converter only runs `Helsinki-NLP/opus-mt-en-da` → `models/opus-mt-en-da_ct2`. The `opus-mt-da-en` block is commented out. `translate.py` still points at `models/opus-mt-da-en_ct2`, so a first-time reproduction must uncomment that conversion (or convert it in a one-off shell command).

CTranslate2 is used because the labeling pass walks thousands of articles, and the Python Transformers generate loop was too slow on the course GPUs.

### 1. Danish → English (`translate.py`)

**Read:** `10000_articles_without_linebreaks.csv`  
**Columns in:** `id`, `article text`  
**Write:** `translated_articles.csv`  
**Columns out:** `id`, `body`, `translated`

For each article:

1. Sentence-split with NLTK `punkt`.
2. Measure each sentence in OPUS-MT tokens.
3. If a sentence is longer than `0.9 * 512` tokens, split it on words / commas (see below).
4. Greedy-pack sentences into batches that stay under that token budget.
5. `translator.translate_batch` on each batch.
6. Join batch translations with spaces.

The tokenizer is `Helsinki-NLP/opus-mt-da-en`. The CTranslate2 call also sends a `target_prefix` of `eng_Latn`. That prefix style belongs to NLLB-style models (the converter file still has commented `facebook/nllb-200-*` experiments). OPUS-MT does not use Flores codes the same way. Treat the prefix as leftover from the NLLB prototype unless you re-measure quality with and without it.

### 2. English → English summary (`summary.py`)

**Read:** `translated_articles.csv`  
**Write:** `summarized_file_ml80_rp5.0.csv`  
**Columns out:** `id`, `body`, `translated`, `summary`

Model: `mrm8488/t5-base-finetuned-summarize-news`.

Generation defaults in the script:

| Setting | Value |
| --- | --- |
| `num_beams` | 2 |
| `max_length` | 80 |
| `repetition_penalty` | 5.0 |
| `length_penalty` | 1.0 |
| `early_stopping` | True |
| encoder window | 512 tokens |

Long English articles are split with the same sentence-pack algorithm, each chunk is summarized independently, and the chunk summaries are concatenated. That is why a long piece can produce a multi-sentence “summary” that is really a stitch of local abstracts. Compression is uneven: the lead may be over-compressed and the tail under-compressed.

**Smoke-test slice:** `pd.read_csv(...)[:10]` only labels the first ten rows. Remove that slice for a full run.

### 3. English summary → Danish summary (`translate_back.py`)

**Read:** `summarized_file_ml80_rp5.0.csv`  
**Write:** `labeled_dataset_ml80_rp5.0.csv`  
**Columns out:** `id`, `body`, `summary`

Same CTranslate2 pattern as step 1, opposite direction: `models/opus-mt-en-da_ct2` and `Helsinki-NLP/opus-mt-en-da`. Only the *summary* column is translated. The Danish `body` is the original article, not a round-trip.

After this stage you have silver pairs ready to split into `datasets/train_dataset.csv`, `datasets/validation_dataset.csv`, and `datasets/test_dataset.csv` for `finetune.py`.

### 4. Fine-tune and evaluate

Documented in [models.md](models.md) and [evaluation.md](evaluation.md). Fine-tuning is not part of label generation; it consumes the CSVs from step 3.

## Chunking algorithm

Both translation and summarization need a context window. The implementation is copy-pasted across `translate.py` and `summary.py` (and a slimmer variant in `translate_back.py`).

### Sentence packing

```
budget = int(512 * 0.9)   # 460 tokens
batches = []
current, current_len = [], 0
for sentence in sentences:
    n = token_len(sentence)
    if current_len + n > budget and current:
        flush current
    append sentence to current
```

A leftover batch is flushed at the end. Empty leading batches should not occur if the input has sentences.

### Long-sentence splitter

When a single sentence exceeds the token budget, `split_long_sentence` walks **words**, not tokens:

- Accumulate `len(word) + 1` (character count, including a space).
- If the current word is `,`, `;`, or `:` **and** the running character count is still below the budget, cut there.
- If the running character count reaches the budget, push the previous words as a chunk and start a new chunk with the overflowing word.

NLTK `word_tokenize` yields punctuation as its own token, so the comma rule can fire. The budget number (`460`) is a *token* threshold reused as a *character* threshold. That mismatch is real; it is conservative (460 characters is usually fewer tokens than 460), so it rarely overflows the encoder, but it can over-split.

`examples/text_chunking.py` reimplements this behavior with a tiny regex tokenizer so you can print batches without downloading `punkt`.

## Column rename at the first hop

| Stage | Article column |
| --- | --- |
| Raw dump | `article text` |
| After `translate.py` | `body` (copy of the Danish article) |
| Fine-tune CSVs | `body` |

`id` is the join key for the whole pipeline. The toy corpus in `examples/corpus.py` uses stable ids `dn-001` … `dn-010`.

## Failure modes you will see in silver labels

- **Hallucinated English facts** from the T5 news model, then fluently translated into Danish.
- **Stitched chunk summaries** that repeat the same entity with different wording.
- **Dropped Danish specifics** (street names, municipal abbreviations) that OPUS-MT paraphrased in English and never recovered.
- **Length blow-ups** when a short article still gets an 80-token English summary and a slightly longer Danish rendering.

None of these are crashes. They are why the Nordjylland human test set matters.

## Dry-run without models

```bash
python examples/toy_pipeline.py
```

That script does not call OPUS-MT or T5. It validates schemas, aligns ids across the committed snapshots, and shows how `dn-006` (the long harbor article) packs under a small word budget.
