# Pipeline

The 2023 project treats Danish news summarization as a **pivot** problem.
There was no strong Danish news summarizer on the shelf, and the scraped
articles did not come with gold headlines. The workaround:

1. Translate Danish articles to English with OPUS-MT (`da-en`).
2. Summarize the English with a T5 model that was already fine-tuned on
   English news.
3. Translate the English summaries back to Danish (`en-da`).
4. Treat those Danish strings as **silver labels** and fine-tune mT5.
5. Evaluate the fine-tuned model on Nordjylland news (human summaries).

```text
Danish article
    │
    ▼
OPUS-MT da→en     (CTranslate2, 512-token windows)
    │
    ▼
T5 news summarizer (mrm8488/t5-base-finetuned-summarize-news)
    │
    ▼
OPUS-MT en→da     (CTranslate2)
    │
    ▼
silver CSV (id, body, summary)
    │
    ▼
mT5 fine-tune     (google/mt5-large in finetune.py)
    │
    ▼
Nordjylland test  (use_model.py / eval.py)
```

## Stage 1 — Convert OPUS-MT to CTranslate2

`Ctranslate_converter.py` wraps `TransformersConverter`. CTranslate2 stores a
quantized Transformer that `translate.py` and `translate_back.py` load with
`ctranslate2.Translator`.

The script as committed converts **only** `Helsinki-NLP/opus-mt-en-da`.
`translate.py` needs `models/opus-mt-da-en_ct2`. The `da-en` converter
lines are present but commented out. Uncomment them (or run a second
converter) before step 2. See [design-notes.md](design-notes.md).

```bash
python Ctranslate_converter.py
```

Expected directories after a complete conversion:

* `models/opus-mt-da-en_ct2`
* `models/opus-mt-en-da_ct2`

## Stage 2 — Danish → English

`translate.py` reads `10000_articles_without_linebreaks.csv` (`id`,
`article text`), splits each body into windows, and writes
`translated_articles.csv` (`id`, `body`, `translated`).

Windowing:

* NLTK `sent_tokenize` for sentence boundaries.
* Sentences longer than `0.9 * 512` are passed through `split_long_sentence`.
* Packed lists are fed to `translator.translate_batch`.

The CPU example `examples/01_chunk_danish_article.py` reimplements that packing
with an explicit unit (`words` / `chars` / `tokens`) and a Danish
abbreviation list. It does not call the translator.

## Stage 3 — English summarization

`summary.py` loads `mrm8488/t5-base-finetuned-summarize-news`, splits each
English article the same way, and generates with:

| Setting | Value in the script |
| --- | --- |
| `max_length` | 80 |
| `repetition_penalty` | 5.0 |
| `num_beams` | 2 |
| `length_penalty` | 1.0 |
| `early_stopping` | True |

The output filename records those two knobs:
`summarized_file_ml80_rp5.0.csv`.

The committed script also does `pd.read_csv(...)[:10]`, so it only
summarizes the first ten rows. Remove the slice for a full run.

## Stage 4 — English → Danish silver labels

`translate_back.py` translates the `summary` column back to Danish and
writes `labeled_dataset_ml80_rp5.0.csv` (`id`, `body`, `summary`). The
English pivot column is dropped here; fine-tuning only sees Danish.

## Stage 5 — Fine-tune mT5

`finetune.py` loads `datasets/train_dataset.csv`,
`datasets/validation_dataset.csv`, and `datasets/test_dataset.csv`
(same columns as the labeled file). It tokenizes bodies to 1024 tokens and
summaries to 128, then trains `google/mt5-large` with Adafactor,
polynomial decay, and ROUGE-1 mid F-measure as the checkpoint metric.

The trained weights are written to `./large_model`.

## Stage 6 — Inspect and evaluate

* `use_model.py` prints a few generations from `small_model` on the
  ScandEval Nordjylland *mini* split (`input_text` / `target_text`).
* `eval.py` runs `Seq2SeqTrainer.evaluate()` on
  `alexandrainst/nordjylland-news-summarization` and reports ROUGE plus
  BERTScore (`xlm-roberta-large`, `lang='da'`).

Those two scripts do not load `./large_model`. They load `small_model` and
`google/mt5-small` as the tokenizer name. If you fine-tuned large, point
them at `./large_model` and `google/mt5-large`. Documented further in
[models.md](models.md).

## CPU dry-run

`examples/02_pipeline_dry_run.py` walks the same four data stages on the
fixture articles using `danish_news.glossary.GlossaryBackend`. The backend
is a phrase table. It exists so the handoff and the windowing can be
debugged without a GPU. Do not treat its strings as translations.
