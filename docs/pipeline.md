# Pipeline

The labeling pipeline is four batch jobs plus a later fine-tune. Each job is a standalone script with hard-coded paths. Nothing in the original tree wires them together with a CLI or config file.

This page walks the data as it moves across disk.

## Stage 0 — Convert translation models

**Script:** `Ctranslate_converter.py`

CTranslate2 reads a Hugging Face Transformers encoder-decoder and writes a directory of quantized/optimized runtime files.

| Setting in the file | Value |
| --- | --- |
| Active converter | `Helsinki-NLP/opus-mt-en-da` |
| Active output | `models/opus-mt-en-da_ct2` |
| Commented converters | NLLB 3.3B, NLLB 600M, `opus-mt-da-en` |

`translate.py` does **not** use the active output. It loads `models/opus-mt-da-en_ct2`. Convert that checkpoint before Danish→English translation, either by uncommenting the `opus_da_en_model` lines or by running an equivalent `TransformersConverter("Helsinki-NLP/opus-mt-da-en").convert(...)`.

CTranslate2 conversion is one-time work. The resulting folders are large and are gitignored.

## Stage 1 — Danish articles to English

**Script:** `translate.py`

### Inputs

- CSV: `10000_articles_without_linebreaks.csv`
- Columns: `id`, `article text`
- Runtime: `models/opus-mt-da-en_ct2`
- Tokenizer: `Helsinki-NLP/opus-mt-da-en` (`src_lang="dan_Latn"`)

The filename is historical. The script does not enforce a 10,000-row limit; it translates every row.

### Processing

1. Read all article bodies into memory.
2. For each article, split into sentences with NLTK `punkt`.
3. If a sentence encodes longer than `text_max_length` (`int(512 * 0.9) = 460` tokens), split it on words and on `,`, `;`, `:`.
4. Pack sentences into lists whose encoded length stays under that window.
5. Translate each list with `ctranslate2.Translator.translate_batch`.
6. Join translated sentences with spaces.

The tokenizer is also given `tgt_lang='eng_Latn'` style prefixes in `translate()`. OPUS-MT da-en is a bilingual model, not NLLB. The extra language-token prefix is leftover from earlier NLLB experiments (the converter still has those models commented out). On a bilingual OPUS-MT model the prefix can emit a stray token at the start of a hypothesis. `translate()` strips the first generated token with `result.hypotheses[0][1:]`.

### Output

CSV: `translated_articles.csv`

| Column | Meaning |
| --- | --- |
| `id` | Copied from the source row |
| `body` | Original Danish article (`article text`) |
| `translated` | English article |

## Stage 2 — English summaries

**Script:** `summary.py`

### Inputs

- CSV: `translated_articles.csv`
- Columns used: `id`, `body`, `translated`
- Model: `mrm8488/t5-base-finetuned-summarize-news`
- Device: CUDA if available, otherwise CPU

### Processing

1. **Debug cap:** `pd.read_csv(...)[:10]` keeps only the first ten rows.
2. Each English `translated` field is packed with the same sentence-then-word splitter, now with `text_max_length = 512` to match T5's typical window.
3. Each packed chunk is summarized independently:
   - `num_beams=2`
   - `max_length=80`
   - `repetition_penalty=5.0`
   - `length_penalty=1.0`
   - `early_stopping=True`
4. Chunk summaries are joined with a space to form one article-level summary.

A long article therefore becomes a concatenation of local summaries, not a single global abstract. That is a deliberate trade-off: T5-base cannot see 2–3k tokens at once, and the project preferred coverage over a tightly compressed lede.

### Output

CSV: `summarized_file_ml80_rp5.0.csv`

The filename records two decode knobs:

- `ml80` → `max_length=80`
- `rp5.0` → `repetition_penalty=5.0`

| Column | Meaning |
| --- | --- |
| `id` | Copied |
| `body` | Original Danish article |
| `translated` | English article |
| `summary` | English summary |

## Stage 3 — English summaries to Danish

**Script:** `translate_back.py`

### Inputs

- CSV: `summarized_file_ml80_rp5.0.csv`
- Runtime: `models/opus-mt-en-da_ct2`
- Tokenizer: `Helsinki-NLP/opus-mt-en-da` (`src_lang="eng_Latn"`)

Only the `summary` column is translated. The Danish `body` is passed through unchanged so the fine-tune sees a real Danish article paired with a silver Danish summary.

### Processing

Same sentence packing as stage 1, with `max_length = 512` and `text_max_length = 460`. Summaries are usually short enough to be a single batch.

The same NLLB-style target prefix (`dan_Latn`) is applied, and the first generated token is dropped.

### Output

CSV: `labeled_dataset_ml80_rp5.0.csv`

| Column | Meaning |
| --- | --- |
| `id` | Copied |
| `body` | Original Danish article |
| `summary` | Danish silver summary |

This is the labeled dataset. It is **not** yet split for `finetune.py`.

## Stage 4 — Split for training (manual)

There is no script in the original tree that writes `datasets/*.csv`. The expected layout is documented in [datasets.md](datasets.md).

A typical split for a ~10k-article dump:

| Split | Rough share | File |
| --- | --- | --- |
| Train | 80% | `datasets/train_dataset.csv` |
| Validation | 10% | `datasets/validation_dataset.csv` |
| Test | 10% | `datasets/test_dataset.csv` |

Shuffle on `id` before slicing so related local-news days do not all land in train. The example splitter in `examples/demo_pipeline.py` uses a stable hash of `id` so the same rows stay in the same split if you rerun it.

## Stage 5 — Fine-tune mT5

**Script:** `finetune.py`

1. Load the three CSVs with `datasets.load_dataset('csv', ...)`.
2. Tokenize `body` to 1024 tokens and `summary` to 128 tokens using the `google/mt5-large` tokenizer.
3. Build an `AutoConfig` with generation defaults (`min_length=9`, `max_length=128`, `num_beams=4`, `no_repeat_ngram_size=3`, `length_penalty=0.8`).
4. Train 20 epochs with Adafactor, polynomial decay, `fp16`, and `load_best_model_at_end` on `rouge_1_mid_fmeasure`.
5. Save the trainer's best model to `./large_model`.

The training metric uses `datasets.load_metric("rouge")`, which downloads the classic `rouge-score` wrapper. Mid F-measure for ROUGE-1/2/L is what the trainer reports.

## Stage 6 — Inspect and evaluate

Two separate scripts, two slightly different defaults.

| Script | Local weights | Hugging Face eval set | Batch |
| --- | --- | --- | --- |
| `use_model.py` | `small_model` | `ScandEval/nordjylland-news-summarization-mini` test | 2 |
| `eval.py` | `small_model` | `alexandrainst/nordjylland-news-summarization` test | 64 |

Neither script loads `./large_model` unless you change the path. If you only ran `finetune.py`, copy or point those scripts at `large_model`.

`use_model.py` prints:

- the raw Danish input
- the reference summary
- the generated summary

for the first few dataloader batches.

`eval.py` returns a dict of ROUGE mid F-measures plus mean BERTScore precision/recall/F1 with `lang='da'` and `model_type="xlm-roberta-large"`.

## Memory and runtime shape

These are order-of-magnitude notes from the script settings, not measured benchmarks.

| Stage | Dominant cost | Why |
| --- | --- | --- |
| Conversion | Disk + RAM | Each OPUS-MT export is hundreds of MB |
| `translate.py` | GPU or many CPU threads | 10k articles, sentence batches of size ~few |
| `summary.py` | GPU | T5-base beam-2 per chunk; long articles → many chunks |
| `translate_back.py` | GPU or CPU | Summaries are short; this is the cheap translation pass |
| `finetune.py` | GPU VRAM | `mt5-large`, batch 8, 1024 source tokens, fp16 |
| `eval.py` | GPU + download | BERTScore pulls `xlm-roberta-large` |

## Failure isolation

Because every stage writes a CSV, you can restart from the last good file:

1. If translation dies at row 4,000, keep `translated_articles.csv` only if the script finished. The original loop does not checkpoint. For a long run, consider writing incrementally (not implemented in the 2023 script).
2. If summarization was capped at 10 rows, the labeled file will also have 10 rows. That is enough to smoke-test fine-tuning, not enough to train.
3. If back-translation fails, you still have English summaries and can retry without re-summarizing.

The example demo (`examples/demo_pipeline.py`) walks the same CSV contracts on five fictional articles so you can see the column flow without GPUs.
