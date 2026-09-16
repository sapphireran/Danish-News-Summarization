# Archaeology of the 2023 root scripts

The files at the repository root are the course hand-in. This note lists
the contracts and the scars that the Sejerø desk is written against.
Nothing here changes those files.

## `Ctranslate_converter.py`

Only `Helsinki-NLP/opus-mt-en-da` is converted. The `opus-mt-da-en` lines
are commented out, even though `translate.py` expects
`models/opus-mt-da-en_ct2`. A rebuild has to uncomment the forward model.

## `translate.py`

- Reads `10000_articles_without_linebreaks.csv` columns `id`, `article text`.
- Writes `translated_articles.csv` columns `id`, `body`, `translated`.
- Loads `Helsinki-NLP/opus-mt-da-en` with `src_lang="dan_Latn"` and then
  prefixes every batch with `eng_Latn`. Those NLLB language tags are not
  part of the OPUS vocabulary. The converter comments still mention NLLB
  3.3B / 600M, which is the leftover of an earlier plan.
- Packs sentences to 460 tokenizer ids and cuts long sentences on commas
  using `len(word) + 1`.

## `summary.py`

- Reads `translated_articles.csv`.
- Uses `mrm8488/t5-base-finetuned-summarize-news`.
- **Slices `df[:10]`**. This is the easiest foot-gun in the folder.
- `generate(..., num_beams=2, max_length=80, repetition_penalty=5.0,
  length_penalty=1.0, early_stopping=True)`.
- Splits long English bodies into windows, summarizes each window, and
  concatenates. A long article therefore gets a *stitched* silver
  summary, not one global lede.
- Writes `summarized_file_ml80_rp5.0.csv`.

## `translate_back.py`

- Reads the stitched English summaries.
- Writes `labeled_dataset_ml80_rp5.0.csv` with Danish `summary`.
- Uses `opus-mt-en-da` and the same leftover `eng_Latn` / `dan_Latn`
  prefixes.
- Packs to **512**, not 460, and does **not** cut a long sentence.

## `finetune.py`

- `google/mt5-large`, Adafactor, polynomial decay, `lr=3e-4`,
  20 epochs, warmup 1 000, batch 8, fp16, `length_penalty=0.8`,
  `no_repeat_ngram_size=3`, `num_beams=4`.
- Tokenizes `body` to 1024 and `summary` to 128.
- Best checkpoint chosen by `rouge_1_mid_fmeasure` via the deprecated
  `datasets.load_metric("rouge")`.
- Saves `./large_model`.

## `eval.py` and `use_model.py`

- Both load a local `small_model` while the tokenizer comes from
  `google/mt5-small`.
- `eval.py` scores
  `alexandrainst/nordjylland-news-summarization` with ROUGE and
  BERTScore (`xlm-roberta-large`, `lang='da'`), `batch_size=64`,
  `dataloader_drop_last=True`.
- `use_model.py` prints five generations from
  `ScandEval/nordjylland-news-summarization-mini` with
  `no_repeat_ngram_size=1`. That n-gram ban is much harsher than the
  training config's 3-gram ban and can make the printed samples look
  worse than the checkpoint.

## Column rename across hops

| Hop | Input columns | Output columns |
| --- | --- | --- |
| raw | `id`, `article text` | — |
| translate | `article text` | `id`, `body`, `translated` |
| summarize | `translated` | `id`, `body`, `translated`, `summary` (EN) |
| translate back | `summary` (EN) | `id`, `body`, `summary` (DA) |
| fine-tune | `id`, `body`, `summary` | — |
| public eval | `input_text`, `target_text`, `text_len`, `summary_len` | metrics |

`examples/data/` uses those names on purpose.
