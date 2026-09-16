# Pipeline

This page is the contract between the six course scripts: filenames, columns, chunking rules, and the places the committed code does something surprising.

## End-to-end file flow

```
10000_articles_without_linebreaks.csv
        │  columns: id, article text
        ▼
   translate.py
        │
        ▼
translated_articles.csv
        │  columns: id, body, translated
        ▼
   summary.py          ⚠ processes only df[:10] as committed
        │
        ▼
summarized_file_ml80_rp5.0.csv
        │  columns: id, body, translated, summary   (summary is still English)
        ▼
   translate_back.py
        │
        ▼
labeled_dataset_ml80_rp5.0.csv
        │  columns: id, body, summary               (summary is Danish)
        ▼
   manual split into datasets/{train,validation,test}_dataset.csv
        │  columns: id, body, summary
        ▼
   finetune.py  →  ./large_model
        │
        ▼
   copy / rename to small_model   (not automated)
        ▼
   use_model.py / eval.py
```

The example tree mirrors every one of those schemas under `examples/data/` so you can validate the contracts without the 10k dump.

## Stage 1 — CTranslate2 conversion

`Ctranslate_converter.py` wraps `ctranslate2.converters.TransformersConverter`.

As committed it only converts:

- `Helsinki-NLP/opus-mt-en-da` → `models/opus-mt-en-da_ct2`

The Danish → English direction that `translate.py` loads (`models/opus-mt-da-en_ct2`) is present only as a comment. Convert it yourself before step 2. A copy-paste snippet is in [models.md](models.md).

NLLB 3.3B and 600M converters are also commented out. The later translation functions still use NLLB-style language tags (`dan_Latn`, `eng_Latn`) as `target_prefix`. Helsinki OPUS-MT does **not** use those tags the way NLLB does. See [troubleshooting.md](troubleshooting.md).

## Stage 2 — `translate.py` (Danish → English)

Hard-coded constants:

- `input_file_path = '10000_articles_without_linebreaks.csv'`
- `model_path = "models/opus-mt-da-en_ct2"`
- `max_length = 512`
- `text_max_length = int(max_length * 0.9)` → 460
- `output_file_path = 'translated_articles.csv'`

### Input columns

| Column | Meaning |
| --- | --- |
| `id` | Stable article id, passed through every later file |
| `article text` | Full Danish body, line breaks already removed in the course dump |

### Output columns

| Column | Meaning |
| --- | --- |
| `id` | Same id |
| `body` | Original Danish text (renamed from `article text`) |
| `translated` | English rendering, sentence packs joined with spaces |

### Chunking

1. `nltk.sent_tokenize` on the Danish article.
2. Each sentence is measured with the OPUS-MT tokenizer.
3. Sentences longer than `text_max_length` are split on words, preferring `,`, `;`, `:` as cut points (`split_long_sentence`).
4. Sentences are packed into lists whose token lengths sum to ≤ `text_max_length`.
5. Each pack is translated as a batch (`translate_batch`).
6. Packs are concatenated with a trailing space.

This is the same algorithm the example helper `examples/lib/text_chunking.py` re-implements so you can print packs without CTranslate2.

### Translation call

`translate()` encodes each sentence, converts ids to tokens, and (historically) attaches a target prefix `[tgt_lang]`. The decode step drops the first generated token (`hypotheses[0][1:]`), which only makes sense if a language-code prefix was actually consumed. With a plain OPUS-MT model that prefix is optional/wrong; inspect a few rows of `translated_articles.csv` before you burn a night of GPU time.

## Stage 3 — `summary.py` (English → English summary)

Hard-coded constants:

- `input_file_path = "translated_articles.csv"`
- `model_name = "mrm8488/t5-base-finetuned-summarize-news"`
- `text_max_length = 512`
- `output_file_path = 'summarized_file_ml80_rp5.0.csv'`
- `max_length=80` on `model.generate`
- `repetition_penalty=5.0`, `length_penalty=1.0`, `num_beams=2`, `early_stopping=True`

### The `[:10]` slice

```python
df = pd.read_csv(input_file_path)[:10]
```

This is a leftover debug limit. A full labeling run must delete `[:10]`. The output filename (`ml80_rp5.0`) encodes the generation knobs, not the number of rows.

### Long-article strategy

English T5-base is a 512-token encoder. A translated news feature can be longer. The script:

1. splits the English article into sentence packs that fit 512 tokens (same family of helpers as translation),
2. summarizes **each pack** independently to ≤ 80 tokens,
3. joins the pack summaries with a space.

So a 2,000-token article does not get one 80-token summary. It gets *N* short summaries concatenated. That is closer to “section-wise abstractive notes” than to a single well-formed lede. Fine-tuning later has `max_length=128` on the target side, so very long joined summaries get truncated there.

### Output columns

| Column | Meaning |
| --- | --- |
| `id` | Same id |
| `body` | Original Danish |
| `translated` | English article |
| `summary` | **English** summary (name is easy to misread) |

## Stage 4 — `translate_back.py` (English summary → Danish summary)

Hard-coded constants:

- `input_file_path = 'summarized_file_ml80_rp5.0.csv'`
- `output_file_path = 'labeled_dataset_ml80_rp5.0.csv'`
- `model_path = "models/opus-mt-en-da_ct2"`
- `max_length = 512`

Only the `summary` column is translated. `body` stays the original Danish. The English `translated` column is dropped.

### Output columns

| Column | Meaning |
| --- | --- |
| `id` | Same id |
| `body` | Original Danish article |
| `summary` | Danish silver label |

This is the format `finetune.py` wants, after you split it.

## Stage 5 — Split (manual)

There is no `split.py` in the repo. For the course run the labeled CSV was shuffled and cut into:

- `datasets/train_dataset.csv`
- `datasets/validation_dataset.csv`
- `datasets/test_dataset.csv`

`examples/toy_labeling_pipeline.py` does this split for the tiny example set so you can see the expected layout. A real split should be by article id (no leakage) and should probably be stratified by length. The course scripts do not enforce that.

## Stage 6 — `finetune.py`

Loads the three CSVs, tokenizes `body` → encoder (1024) and `summary` → labels (128), builds `google/mt5-large` with a custom `AutoConfig` (beam 4, no-repeat trigram, length penalty 0.8), and runs `Seq2SeqTrainer` for 20 epochs. Full hyperparameter sheet: [training.md](training.md).

The script saves `./large_model` at the end. It does **not** write `small_model`.

## Stage 7 — Inspection and scoring

`use_model.py` and `eval.py` both `from_pretrained("small_model")`. They evaluate on Nordjylland, whose column names are `input_text` / `target_text`, not `body` / `summary`. That is intentional: the held-out benchmark is a different schema and a different source.

## Intermediate data you should spot-check

After each GPU stage, open five random rows and ask:

1. **Translation:** is the English actually English, or did the target prefix eat the first word?
2. **Summary:** does the English summary mention entities from *that* article, or did chunk-joining drift?
3. **Back-translation:** is the Danish grammatical, or did OPUS-MT produce case/gender artifacts?
4. **Length:** did joined chunk summaries blow past 128 tokens (they will be truncated in training)?

`examples/length_stats.py` computes the easy numeric half of that checklist on the example CSVs.
