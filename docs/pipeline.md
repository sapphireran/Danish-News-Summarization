# Pipeline

The project builds a Danish news summarizer without a large hand-labeled Danish
training set. English summarization models were stronger in 2023 than Danish
ones, so the course project manufactured silver labels with a
**translate → summarize → translate-back** loop, then fine-tuned multilingual
mT5 on the resulting Danish `(article, summary)` pairs.

```text
Danish articles
      │
      ▼
[1] CTranslate2 conversion of Helsinki-NLP OPUS-MT
      │
      ▼
[2] translate.py          da → en   (full articles)
      │
      ▼
[3] summary.py            English T5 news summarizer
      │
      ▼
[4] translate_back.py     en → da   (summaries only)
      │
      ▼
Labeled Danish CSV
      │
      ▼
[5] finetune.py           google/mt5-large on body → summary
      │
      ├── use_model.py    qualitative generations
      └── eval.py         ROUGE + BERTScore on Nordjylland News
```

## Step 1 — Convert OPUS-MT to CTranslate2

`Ctranslate_converter.py` wraps `ctranslate2.converters.TransformersConverter`.

As committed, only `Helsinki-NLP/opus-mt-en-da` is converted, into
`models/opus-mt-en-da_ct2`. The Danish→English converter is present but
commented out. `translate.py` still expects `models/opus-mt-da-en_ct2`, so both
directions must be converted before the forward translation step. See
[models.md](models.md).

## Step 2 — Danish articles to English

`translate.py` reads `10000_articles_without_linebreaks.csv` and writes
`translated_articles.csv`.

The script does **not** send a whole article through the translator in one
call. OPUS-MT is a 512-token encoder, so each article is:

1. Split into sentences with NLTK `punkt`.
2. Re-split any sentence whose tokenized length exceeds `0.9 * 512`.
3. Packed into batches that stay under that budget.
4. Translated with CTranslate2 `translate_batch`.

Output columns: `id`, `body` (original Danish), `translated` (English).

The input column name is `article text`. After this step the Danish text is
renamed to `body`. Later scripts never look for `article text` again.

## Step 3 — English summarization

`summary.py` loads `mrm8488/t5-base-finetuned-summarize-news` and summarizes
each English article. Long articles are split the same way as in translation,
then each chunk is summarized with:

- `num_beams=2`
- `max_length=80`
- `repetition_penalty=5.0`
- `length_penalty=1.0`
- `early_stopping=True`

Chunk summaries are concatenated with a space. The output filename
`summarized_file_ml80_rp5.0.csv` encodes those two generation knobs.

**As committed, the script only keeps the first 10 rows** (`df[:10]`). That
looks like a leftover debug slice. Remove it before generating a full training
set.

## Step 4 — Summaries back to Danish

`translate_back.py` reads the English `summary` column and writes a Danish
`summary` column. The Danish `body` is copied through unchanged. The English
article is dropped.

Default paths:

| Role | Filename |
| --- | --- |
| Input | `summarized_file_ml80_rp5.0.csv` |
| Output | `labeled_dataset_ml80_rp5.0.csv` |
| Model | `models/opus-mt-en-da_ct2` |

The labeled file is the silver-standard dataset: Danish article + Danish
summary produced by the English model and a second translation hop.

## Step 5 — Fine-tune mT5

`finetune.py` expects three already-split CSVs:

- `datasets/train_dataset.csv`
- `datasets/validation_dataset.csv`
- `datasets/test_dataset.csv`

Each file needs `id`, `body`, and `summary`. The script does not create those
splits. See [datasets.md](datasets.md) and the example splitter in
`examples/split_labeled_dataset.py`.

Token limits used at train time:

| Field | Max tokens |
| --- | ---: |
| `body` | 1024 |
| `summary` | 128 |

The trainer writes checkpoints under `mt5-summarize-large/` and copies the
final weights to `./large_model`.

## Step 6 — Inspect and evaluate

`use_model.py` prints a handful of generations from a local `small_model`
checkpoint against `ScandEval/nordjylland-news-summarization-mini`.

`eval.py` runs the Hugging Face `Seq2SeqTrainer.evaluate()` loop on
`alexandrainst/nordjylland-news-summarization` and reports ROUGE plus Danish
BERTScore (`xlm-roberta-large`). That public set uses `input_text` /
`target_text`, not `body` / `summary`.

## Data that never enters the repo

The original 10k-article dump, CTranslate2 model directories, and fine-tuned
mT5 weights are local artifacts. They are not part of git history. Sample
stand-ins for every CSV stage are in `examples/sample_data/`.
