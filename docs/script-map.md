# Script map

One page per original course file: inputs, outputs, hidden assumptions.

## `Ctranslate_converter.py`

| | |
| --- | --- |
| Purpose | Convert Helsinki-NLP OPUS-MT (and optionally NLLB) to CTranslate2 |
| Reads | Hugging Face hub checkpoints |
| Writes | `models/opus-mt-en-da_ct2` (only this line is active) |
| GPU | Not required for conversion |
| Hidden assumption | You will uncomment the da→en block before `translate.py` |

Commented experiments in the same file: `facebook/nllb-200-3.3B` and
`facebook/nllb-200-distilled-600m`. Those would need different token prefixes
than OPUS-MT.

## `translate.py`

| | |
| --- | --- |
| Purpose | Danish article → English article |
| Reads | `10000_articles_without_linebreaks.csv` (`id`, `article text`) |
| Writes | `translated_articles.csv` (`id`, `body`, `translated`) |
| Model dir | `models/opus-mt-da-en_ct2` |
| Tokenizer | `Helsinki-NLP/opus-mt-da-en` |
| Max window | `int(512 * 0.9)` tokens |

Helper functions worth reading before changing anything:

- `split_long_sentence` — word-budget split, prefers `,` / `;` / `:`
- `split_into_sentences` — pack sentences into encoder windows
- `translate` — CTranslate2 batch with `target_prefix`
- `translate_article` — window loop, join with spaces

The module downloads `nltk` `punkt` at import time.

## `summary.py`

| | |
| --- | --- |
| Purpose | English article → English summary |
| Reads | `translated_articles.csv` |
| Writes | `summarized_file_ml80_rp5.0.csv` |
| Model | `mrm8488/t5-base-finetuned-summarize-news` |
| Debug slice | `pd.read_csv(...)[:10]` |

Chunking is duplicated from `translate.py` rather than imported. The two
copies have drifted (return types and long-sentence handling are not
identical). If you change one, do not assume the other follows.

## `translate_back.py`

| | |
| --- | --- |
| Purpose | English summary → Danish summary |
| Reads | `summarized_file_ml80_rp5.0.csv` |
| Writes | `labeled_dataset_ml80_rp5.0.csv` (`id`, `body`, `summary`) |
| Model dir | `models/opus-mt-en-da_ct2` |
| Tokenizer | `Helsinki-NLP/opus-mt-en-da` |

`split_into_sentences` here does **not** break oversized single sentences.
A long English summary without a period can exceed the 512-token budget. In
practice T5 outputs are short, so this rarely fired in the course run.

The English `translated` column is discarded.

## `finetune.py`

| | |
| --- | --- |
| Purpose | Fine-tune `google/mt5-large` on silver Danish pairs |
| Reads | `datasets/{train,validation,test}_dataset.csv` |
| Writes | `mt5-summarize-large/` checkpoints and `./large_model` |
| Metric | ROUGE-1 mid F-measure |

`test_dataset` is loaded into the `DatasetDict` but never passed to the
trainer. Only train + validation are used. The test CSV is still required to
exist because the script loads it unconditionally.

## `use_model.py`

| | |
| --- | --- |
| Purpose | Print a few generations vs references |
| Reads | Hugging Face `ScandEval/nordjylland-news-summarization-mini` |
| Weights | `small_model` |
| Tokenizer | `google/mt5-small` |

See [design-notes.md](design-notes.md) for the row-index vs batch-index
mismatch in the printed source text.

## `eval.py`

| | |
| --- | --- |
| Purpose | Corpus-level ROUGE + Danish BERTScore |
| Reads | `alexandrainst/nordjylland-news-summarization` test split |
| Weights | `small_model` |
| Tokenizer | `google/mt5-small` |

`evaluate` is imported and unused. Metrics still go through
`datasets.load_metric`.

## Files this map does not cover

- `LICENSE` — MIT, copyright 2023 `pang990801`
- `README.md` — short course workflow; the longer story is under `docs/`
- `examples/` and `tests/` — personal archive additions, model-free
