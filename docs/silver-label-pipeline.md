# Silver-label pipeline

Four scripts turn unlabelled Danish news into fine-tuning rows. They share one
idea: never send a whole article through a 512-token encoder if it does not
fit. Split on sentences, pack greedily, run the model, concatenate.

## Step 1 — Convert OPUS-MT

`Ctranslate_converter.py` wraps `ctranslate2.converters.TransformersConverter`.
The file as committed converts `Helsinki-NLP/opus-mt-en-da` only. The da→en
converter is present but commented out. A full replay must uncomment that
block (or run the converter twice) before `translate.py` can load
`models/opus-mt-da-en_ct2`.

CTranslate2 is used because the labelling pass is closer to machine-translation
serving than to research training: long inputs, batch decode, no gradient.

## Step 2 — Danish to English

`translate.py` reads `10000_articles_without_linebreaks.csv` with columns
`id` and `article text`. For each body it:

1. Sentence-splits with `nltk.sent_tokenize`.
2. Encodes each sentence with the OPUS-MT da→en tokenizer.
3. If a single sentence is longer than `0.9 * 512` tokens, calls
   `split_long_sentence`, which walks *characters* (`len(word) + 1`) and
   prefers to break on `,`, `;`, or `:`.
4. Packs sentences into windows that stay under that budget.
5. Runs `translator.translate_batch` and joins the hypotheses with spaces.

The output is `translated_articles.csv` with `id`, `body` (original Danish),
and `translated` (English).

`danish_news_sum.chunking` is the same packing algorithm with a whitespace
tokenizer so `examples/chunk_sample_articles.py` can show the windows without
SentencePiece.

### Known quirk: mixed length units

`split_long_sentence` measures characters. The packer measures tokenizer
ids. A comma-heavy Danish sentence can therefore be cut earlier than the
token budget requires, or — more rarely — a very long compound word can
still overflow. The 2023 run lived with this. Do not "fix" it in the root
scripts unless you are prepared to regenerate the silver labels; the
examples package documents the mix instead of silently changing it.

## Step 3 — English summarisation

`summary.py` loads `mrm8488/t5-base-finetuned-summarize-news` and the
translated CSV. As committed it only keeps the first ten rows
(`df = pd.read_csv(...)[:10]`), which is a debug leftover. A real labelling
pass must drop that slice.

Each English body is packed with the same sentence windows, this time against
a hard 512-token T5 limit. Each window is decoded with:

| Generation flag | Value | Why it is there |
| --- | --- | --- |
| `num_beams` | 2 | Cheap beam search on long dumps |
| `max_length` | 80 | Short news lede, not a paragraph |
| `repetition_penalty` | 5.0 | Aggressive; T5 otherwise loops on names |
| `length_penalty` | 1.0 | Neutral length preference |
| `early_stopping` | True | Stop when all beams hit EOS |

Window summaries are concatenated with a space. The filename
`summarized_file_ml80_rp5.0.csv` encodes those two knobs.

## Step 4 — English summaries back to Danish

`translate_back.py` translates **only** the `summary` column. The Danish
`body` is copied through unchanged. That is the important alignment: the
fine-tuner must see the same Danish source a reader would see, not a
round-tripped body.

The script always loads `models/opus-mt-en-da_ct2`. It still attaches
NLLB-style language prefixes (`eng_Latn` / `dan_Latn`) when it calls
`translate_batch`. OPUS-MT does not use those prefixes the way NLLB does;
they are leftover from an earlier NLLB experiment that is still commented
out in `Ctranslate_converter.py`. On OPUS-MT the prefix is an extra token
the decoder is asked to start from. If back-translated summaries look like
they start with a language tag or drop the first word, this is the first
place to look.

Output: `labeled_dataset_ml80_rp5.0.csv` with `id`, `body`, `summary`.

## After the four steps

The labelled CSV is not consumed by `finetune.py` as-is. You split it into
`datasets/train_dataset.csv`, `datasets/validation_dataset.csv`, and
`datasets/test_dataset.csv` (same three columns). The 2023 project did that
split outside the repository. `examples/inspect_silver_labels.py` is the
check you want before that split: empty summaries, extreme compression, and
length tails.

## Worked fixture

`examples/dry_run_pipeline.py` walks the four committed CSVs in order. The
English and Danish summaries in those files are hand-written, so they are
cleaner than a real OPUS-MT + T5 chain. Use them to learn the schemas and
the packing behaviour, not to estimate ROUGE.
