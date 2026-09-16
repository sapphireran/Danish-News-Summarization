# Silver-label pipeline

This document follows one Danish article from raw CSV through a finished training pair. Commands match the scripts at the repository root. Synthetic numbers and texts in the examples are original; they are not from the 2023 corpus.

## Stage 0 — Inputs

`translate.py` expects a CSV named `10000_articles_without_linebreaks.csv` with at least:

| column | meaning |
| --- | --- |
| `id` | Stable article identifier |
| `article text` | Full Danish body, line breaks already flattened |

The filename is historical. Nothing in the code requires exactly 10,000 rows; that was the slice used for the course run. Newline flattening matters because `nltk.sent_tokenize` and the later CSV round-trips are simpler when bodies are single-line.

Place converted CTranslate2 models at:

- `models/opus-mt-da-en_ct2` — used by `translate.py`
- `models/opus-mt-en-da_ct2` — used by `translate_back.py` and produced by `Ctranslate_converter.py`

## Stage 1 — Model conversion

`Ctranslate_converter.py` wraps `ctranslate2.converters.TransformersConverter`. The committed file converts `Helsinki-NLP/opus-mt-en-da` into `models/opus-mt-en-da_ct2`. Sister conversions for `opus-mt-da-en` and the NLLB family are present but commented out.

CTranslate2 is used for two reasons:

1. **Throughput.** Label generation walks every article twice (da→en and en→da). Transformer greedy/beam decode in Python is the bottleneck.
2. **Memory.** Keeping OPUS-MT in CTranslate2 leaves the GPU free-er for the English T5 and, later, mT5.

Conversion is one-shot. Re-run it only when you change the Hugging Face revision you want to freeze.

## Stage 2 — Danish → English (`translate.py`)

For each body:

1. Sentence-tokenize with NLTK `punkt`.
2. Measure each sentence in **tokenizer tokens**, not characters.
3. If a single sentence exceeds `text_max_length` (90% of 512 = 460), split it on commas/semicolons/colons, falling back to a hard word cut.
4. Pack consecutive sentences into lists whose token sum stays ≤ 460.
5. Translate each list with CTranslate2 `translate_batch`.
6. Concatenate hypotheses with spaces.

The tokenizer is loaded as:

```python
AutoTokenizer.from_pretrained(
    "Helsinki-NLP/opus-mt-da-en",
    use_auth_token=False,
    src_lang="dan_Latn",
)
```

`src_lang="dan_Latn"` is an NLLB-style argument. OPUS-MT tokenizers typically ignore it. The translate function also builds `target_prefix=[[tgt_lang]]` with `tgt_lang='eng_Latn'` and then **drops the first generated token** when decoding (`hypotheses[0][1:]`). That pattern is correct for NLLB (where the first target token is a language code) and is a no-op or a one-token trim for OPUS-MT depending on what the decoder actually emits. Treat it as a 2023 implementation leftover if you revive the pipeline: validate a handful of outputs before spending a night on 10k articles.

Output: `translated_articles.csv` with `id`, `body` (original Danish), `translated` (English).

## Stage 3 — English summarization (`summary.py`)

Model: `mrm8488/t5-base-finetuned-summarize-news`, a T5-base checkpoint fine-tuned on English news.

Generation settings in the committed script:

| knob | value | intent |
| --- | --- | --- |
| `num_beams` | 2 | Cheap beam search |
| `max_length` | 80 | Short news lead, not a multi-paragraph brief |
| `repetition_penalty` | 5.0 | Aggressive; reduces "the the the" loops |
| `length_penalty` | 1.0 | Neutral length bias |
| `early_stopping` | True | Stop when all beams emit EOS |

Articles are again packed into 512-token windows. Each window is summarized independently; window summaries are joined with a space. A long feature therefore becomes a **concatenated multi-lead**, not a single globally-aware abstract. That is a structural limitation of the label factory (see [06-limitations-and-ethics.md](06-limitations-and-ethics.md)).

The script slices `df[:10]` before iterating. That is a debug guard from the course notebook. For a full run, delete the slice.

Output: `summarized_file_ml80_rp5.0.csv` with `id`, `body`, `translated`, `summary` (English).

## Stage 4 — English → Danish (`translate_back.py`)

Same CTranslate2 pattern as Stage 2, opposite direction. Only the **summary** column is translated; the Danish `body` is passed through unchanged so the fine-tuner never sees English source text.

Sentence packing here uses `max_length` (512) rather than the 90% budget used in `translate.py`. Summaries are short, so the difference rarely matters, but it is another historical inconsistency.

Output: `labeled_dataset_ml80_rp5.0.csv` with `id`, `body`, `summary` (Danish silver label).

## Stage 5 — Split and fine-tune (`finetune.py`)

The course run split the labeled CSV into:

- `datasets/train_dataset.csv`
- `datasets/validation_dataset.csv`
- `datasets/test_dataset.csv`

`finetune.py` does **not** perform the split. You must create those three files yourself (see [04-dataset-schema.md](04-dataset-schema.md)). Tokenization:

- article `body` → 1024 tokens
- `summary` → 128 tokens
- batch size 128 for the `map` call, train batch 8, Adafactor, polynomial decay, 20 epochs

The trainer's best checkpoint is selected by `rouge_1_mid_fmeasure` on the validation split. The model is then saved to `./large_model`.

## Stage 6 — Qualitative check and official eval

`use_model.py` and `eval.py` do **not** read the silver-label CSVs. They load an external Danish benchmark so you are not scoring the model on its own machine translations.

That separation is intentional. If you evaluate on silver labels, you mostly measure "how well mT5 copies OPUS-MT+T5," which inflates scores and hides hallucination.

## End-to-end data contract

```
10000_articles_without_linebreaks.csv
        │  translate.py
        ▼
translated_articles.csv
        │  summary.py
        ▼
summarized_file_ml80_rp5.0.csv
        │  translate_back.py
        ▼
labeled_dataset_ml80_rp5.0.csv
        │  (manual split)
        ▼
datasets/{train,validation,test}_dataset.csv
        │  finetune.py
        ▼
./large_model  +  mt5-summarize-large/
```

Column names change at the first hop (`article text` → `body`). Downstream scripts never look for `article text` again. When you write new loaders, alias early.

## Failure modes at each hop

| Stage | Typical failure | What you see |
| --- | --- | --- |
| Conversion | Missing `sentencepiece` / HF auth | Converter exits before writing `models/` |
| da→en | Unconverted `opus-mt-da-en` | CTranslate2 `RuntimeError` on model path |
| da→en | `punkt` missing | `LookupError` inside `sent_tokenize` |
| Summarize | 10-row slice forgotten | Tiny output CSV, fine-tune set is useless |
| Summarize | OOM on long packs | CUDA OOM; reduce pack length or batch |
| en→da | Empty English summary | Empty Danish label; mT5 learns to emit almost nothing |
| Fine-tune | `load_metric("rouge")` on new `datasets` | Import/runtime error; install `rouge-score` or switch to `evaluate` |
| Eval | `small_model` missing | `OSError` from `from_pretrained` |

Richer debugging notes live in [08-troubleshooting.md](08-troubleshooting.md).

## Worked micro-example

A three-sentence synthetic article (also in `examples/data/sample_articles.csv`, id `SYN-001`):

> Havneby åbner en ny cykelsti mellem stationen og havnen på lørdag. Kommunen har brugt to år på at forhandle med lodsejere langs ruten. Borgmesteren kalder stien et løft for både pendlere og weekendgæster.

Packed as a single window (well under 460 tokens), translated to English, summarized to a short lead, and translated back, you should get a Danish sentence that still mentions **Havneby**, the **cykelsti**, and roughly **who benefits**. If the silver summary drops the place name or invents a budget figure, the factory is leaking. The walkthrough in `examples/silver_label_walkthrough.md` records one fully written (hand-simulated) pass so you can see the intended shape without running GPUs.
