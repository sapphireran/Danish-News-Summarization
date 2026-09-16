# Label-generation and training pipeline

This is the flow the 2023 scripts implement. Paths are the **literal filenames** hardcoded in the Python files, not suggestions.

```
10000_articles_without_linebreaks.csv
        │
        │  translate.py
        │  model: models/opus-mt-da-en_ct2
        ▼
translated_articles.csv
        │
        │  summary.py
        │  model: mrm8488/t5-base-finetuned-summarize-news
        ▼
summarized_file_ml80_rp5.0.csv
        │
        │  translate_back.py
        │  model: models/opus-mt-en-da_ct2
        ▼
labeled_dataset_ml80_rp5.0.csv
        │
        │  manual / unpublished split into
        ▼
datasets/train_dataset.csv
datasets/validation_dataset.csv
datasets/test_dataset.csv
        │
        │  finetune.py
        │  base: google/mt5-large
        ▼
./large_model
        │
        ├── use_model.py   (loads ./small_model in the checked-in script)
        └── eval.py        (loads ./small_model in the checked-in script)
```

The `ml80_rp5.0` suffix is not a framework convention. It records the English summarizer's `max_length=80` and `repetition_penalty=5.0` so later experiments with other generation settings do not overwrite each other.

## Stage 0 — Convert OPUS-MT to CTranslate2

`Ctranslate_converter.py` uses `ctranslate2.converters.TransformersConverter` to write a CTranslate2 model directory.

The file as checked in only converts `Helsinki-NLP/opus-mt-en-da` to `models/opus-mt-en-da_ct2`. The `da→en` conversion is present but commented out. `translate.py` **requires** `models/opus-mt-da-en_ct2`. Uncomment those lines before a full rerun, or convert the missing direction by hand:

```text
Helsinki-NLP/opus-mt-da-en  →  models/opus-mt-da-en_ct2
Helsinki-NLP/opus-mt-en-da  →  models/opus-mt-en-da_ct2
```

NLLB conversions (`facebook/nllb-200-3.3B`, `facebook/nllb-200-distilled-600m`) are also commented. They were an earlier experiment. The rest of the pipeline assumes OPUS-MT, not NLLB. See [models-and-conversion.md](models-and-conversion.md).

## Stage 1 — Danish → English (`translate.py`)

Input CSV: `10000_articles_without_linebreaks.csv`

Required columns:

- `id`
- `article text`  (note the space)

The script:

1. Loads every row (no `nrows` cap).
2. Picks CUDA if `torch.cuda.is_available()`, otherwise CPU.
3. Builds a CTranslate2 `Translator` from `models/opus-mt-da-en_ct2`.
4. Tokenizes with `Helsinki-NLP/opus-mt-da-en`.
5. Splits each article into sentence packs that stay under `int(512 * 0.9)` tokenizer tokens.
6. If a single sentence is still too long, `split_long_sentence` walks word tokens and cuts on `,`, `;`, `:`, or at the length cap.
7. Translates each pack with `translator.translate_batch`.
8. Writes `translated_articles.csv` with columns `id`, `body`, `translated`.

`body` is a copy of the original Danish `article text`. Downstream scripts never look at `article text` again.

The translate function still builds NLLB-style `target_prefix` tokens (`eng_Latn`). OPUS-MT does not use those language tags. That is a leftover from the NLLB experiment and is one of the first things to disable on a clean rerun. Details in [design-notes.md](design-notes.md).

## Stage 2 — English summarization (`summary.py`)

Input CSV: `translated_articles.csv`

Required columns: `id`, `body`, `translated`

The script:

1. **Only keeps the first 10 rows** (`df = pd.read_csv(...)[:10]`). This is a debug leftover. Remove the slice for a full labeling run.
2. Loads `mrm8488/t5-base-finetuned-summarize-news` with Hugging Face Transformers on GPU/CPU.
3. Splits each English article with the same sentence-packing idea, now using the T5 tokenizer and a hard `text_max_length = 512`.
4. Calls `model.generate` per sub-article with `num_beams=2`, `max_length=80`, `repetition_penalty=5.0`, `length_penalty=1.0`, `early_stopping=True`.
5. Concatenates sub-summaries with a single space.
6. Writes `summarized_file_ml80_rp5.0.csv` with columns `id`, `body`, `translated`, `summary`.

`summary` is still English at this point. `body` is still the original Danish article.

Long Danish articles become several English sub-articles and therefore several short English summaries glued together. The Danish fine-tune later sees one long silver summary, not a single T5 decode.

## Stage 3 — English → Danish (`translate_back.py`)

Input CSV: `summarized_file_ml80_rp5.0.csv`

Required columns: `id`, `body`, `summary`

The script:

1. Loads `models/opus-mt-en-da_ct2` and the `Helsinki-NLP/opus-mt-en-da` tokenizer.
2. Sentence-packs each English summary (no `split_long_sentence` fallback; summaries are short).
3. Translates packs back to Danish.
4. Writes `labeled_dataset_ml80_rp5.0.csv` with columns `id`, `body`, `summary`.

The English `translated` column is dropped. After this file, `summary` means **Danish silver summary**.

`split_into_sentences` is called with `max_length` (512) rather than `text_max_length` (`int(512 * 0.9)`). That is inconsistent with `translate.py` but usually harmless because summaries are well under 512 tokens.

## Stage 4 — Split into train / validation / test

There is **no checked-in split script**. `finetune.py` expects:

```
datasets/train_dataset.csv
datasets/validation_dataset.csv
datasets/test_dataset.csv
```

Each file must have columns `id`, `body`, `summary`. How the 2023 run was split is not recorded in git. A reasonable default for a rerun:

- shuffle with a fixed seed
- 80% train / 10% validation / 10% test
- keep `id` so you can audit silver labels later

Do not confuse this **silver** test split with the public Nordjylland evaluation sets used by `eval.py` and `use_model.py`. Those are different corpora with different column names.

## Stage 5 — Fine-tune mT5 (`finetune.py`)

1. Loads the three CSVs through `datasets.load_dataset('csv', ...)`.
2. Tokenizes `body` to 1024 tokens and `summary` to 128 tokens with the `google/mt5-large` tokenizer.
3. Drops `id`, `body`, `summary` after tokenization.
4. Trains with `Seq2SeqTrainer` for 20 epochs, Adafactor, polynomial LR, `fp16=True`, generation during eval.
5. Selects the best checkpoint by `rouge_1_mid_fmeasure`.
6. Saves the trainer model to `./large_model`.

Training arguments also write epoch checkpoints under `mt5-summarize-large/` and keep only one extra checkpoint (`save_total_limit=1`).

## Stage 6 — Look at predictions (`use_model.py`)

This script does **not** read the silver CSVs. It:

1. Loads `ScandEval/nordjylland-news-summarization-mini` test split.
2. Tokenizes `input_text` / `target_text`.
3. Loads weights from `./small_model` (not `./large_model`).
4. Prints a few generated summaries next to the gold `target_text`.

If you only trained `./large_model`, either copy/symlink it to `small_model` or change `local_model_path`.

## Stage 7 — Score (`eval.py`)

`eval.py` loads the **full** `alexandrainst/nordjylland-news-summarization` test split, a different (larger) public set than `use_model.py`. It also loads `./small_model` and reports ROUGE plus BERTScore (`lang='da'`, `xlm-roberta-large`).

See [evaluation.md](evaluation.md) for what those numbers do and do not mean.

## Data that is not in git

None of the following were committed, which is correct for a news corpus:

- `10000_articles_without_linebreaks.csv`
- intermediate CSVs
- `datasets/*.csv`
- `models/*_ct2`
- `./large_model`, `./small_model`, `mt5-summarize-large/`

The [`../examples/data`](../examples/data) fixtures are **synthetic** stand-ins with the same column names. They are safe to commit and small enough to run on a laptop.

## Failure points that stop the whole chain

1. Missing `models/opus-mt-da-en_ct2` after only running the checked-in converter.
2. Leaving `[:10]` in `summary.py` and thinking the labeled set has 10k rows.
3. Feeding `labeled_dataset_ml80_rp5.0.csv` to `finetune.py` without creating the `datasets/` split files.
4. Evaluating `./small_model` after training `./large_model` and wondering why metrics look like an untrained or older run.
5. Running any stage on CPU against the full 10k-article file. CTranslate2 on CPU is usable for a handful of articles; T5 and mT5-large are not practical without a GPU.
