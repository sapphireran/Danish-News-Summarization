# File map

One page per committed course script, plus the new docs/examples files. Line references describe the 2023 tree.

## `Ctranslate_converter.py`

- **Purpose:** Transformers → CTranslate2.
- **Active model:** `Helsinki-NLP/opus-mt-en-da`.
- **Active output:** `models/opus-mt-en-da_ct2`.
- **Commented:** NLLB 3.3B, NLLB 600M, OPUS `da-en`.
- **CLI / args:** none.
- **Imports:** `ctranslate2.converters.TransformersConverter` only.
- **Danger:** running it as-is does not satisfy `translate.py`.

## `translate.py`

- **Purpose:** Danish articles → English articles.
- **Input:** `10000_articles_without_linebreaks.csv` (`id`, `article text`).
- **Output:** `translated_articles.csv` (`id`, `body`, `translated`).
- **Model:** CTranslate2 `models/opus-mt-da-en_ct2` + HF tokenizer `Helsinki-NLP/opus-mt-da-en`.
- **Helpers:** `split_long_sentence`, `split_into_sentences`, `translate`, `translate_article`.
- **Side effect:** `nltk.download('punkt')` at import.

## `summary.py`

- **Purpose:** English articles → English summaries, pack-wise.
- **Input:** `translated_articles.csv`.
- **Output:** `summarized_file_ml80_rp5.0.csv` (`id`, `body`, `translated`, `summary`).
- **Model:** `mrm8488/t5-base-finetuned-summarize-news` on CUDA if available.
- **Helpers:** `summarize`, `split_long_sentence`, `split_into_sentences`, `sentences_to_text`, `split_article`.
- **Danger:** `df[:10]`.

## `translate_back.py`

- **Purpose:** English summaries → Danish silver labels.
- **Input:** `summarized_file_ml80_rp5.0.csv`.
- **Output:** `labeled_dataset_ml80_rp5.0.csv` (`id`, `body`, `summary`).
- **Model:** CTranslate2 `models/opus-mt-en-da_ct2` + HF tokenizer `Helsinki-NLP/opus-mt-en-da`.
- **Helpers:** `translate`, `split_into_sentences`, `translate_article`.
- **Note:** no `split_long_sentence`; a single huge English sentence could exceed 512.

## `finetune.py`

- **Purpose:** fine-tune `google/mt5-large` on silver CSVs.
- **Input:** `datasets/{train,validation,test}_dataset.csv`.
- **Output:** `mt5-summarize-large/` checkpoints, `./large_model` weights.
- **Metrics:** ROUGE-1/2/L mid F-measure; best checkpoint by ROUGE-1.
- **Does not:** evaluate the test split, save the tokenizer, set a seed, write `small_model`.

## `use_model.py`

- **Purpose:** print a few Nordjylland mini predictions.
- **Input:** hub mini dataset + local `small_model`.
- **Output:** stdout.
- **Generate:** beams=2, `no_repeat_ngram_size=1`, max 128.

## `eval.py`

- **Purpose:** corpus ROUGE + BERTScore on Nordjylland test.
- **Input:** hub full dataset + local `small_model`.
- **Output:** printed metrics dict.
- **BERTScore:** `xlm-roberta-large`, `lang='da'`.

## `README.md`

Short path through both the GPU pipeline and the CPU examples. Points here.

## `LICENSE`

MIT, copyright 2023 `pang990801` (original course commit).

## `requirements.txt` / `requirements-examples.txt`

Full stack vs example-only stack. Added with this docs expansion.

## `.gitignore`

Models, trainer dirs, root generated CSVs, caches. Example CSVs under `examples/data/` stay tracked.

## `docs/`

Prose you are reading. Index: [README.md](README.md).

## `examples/`

| Path | Role |
| --- | --- |
| `README.md` | how to run the CPU walkthrough |
| `data/*.csv` | stage-by-stage sample files |
| `data/finetune/*.csv` | three-row-scale trainer splits |
| `lib/text_chunking.py` | packer ported from the course scripts |
| `lib/schema.py` | column contracts |
| `lib/extractive_summary.py` | first-N sentence baseline |
| `validate_example_data.py` | schema + id alignment checks |
| `sentence_chunking_demo.py` | prints packs for one long article |
| `toy_labeling_pipeline.py` | writes a labeled CSV + splits from the raw sample |
| `length_stats.py` | token-ish / char length tables |

## Files the course machine had that git does not

- `10000_articles_without_linebreaks.csv`
- `models/opus-mt-*-ct2/`
- `datasets/*.csv` from the 10k run
- `small_model/`, `large_model/`, `mt5-summarize-large/`
- any `metrics` printouts or slides
