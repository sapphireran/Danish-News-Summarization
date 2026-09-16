# Script scars in the frozen 2023 files

Pakhuset does not patch the root scripts. `pakhus.scars` reads them with
the AST and asserts that the scars below are still present, so these
notes stay tied to the files rather than to memory.

## Direction mismatch

`Ctranslate_converter.py` converts **only** `Helsinki-NLP/opus-mt-en-da`.
The da-en converter is commented out. `translate.py` nevertheless loads
`models/opus-mt-da-en_ct2`. A clean run of the README order cannot
translate Danish articles until that path exists. `translate_back.py`
does match the converter.

## NLLB language prefixes on OPUS-MT

Both translation scripts pass `target_prefix=[[tgt_lang]]` with
`dan_Latn` / `eng_Latn`, and they decode `hypotheses[0][1:]` to drop a
forced first token. That protocol belongs to NLLB-200, whose converters
are commented in `Ctranslate_converter.py`. OPUS-MT does not speak those
language tags. Depending on the CTranslate2 export, the prefix is either
ignored, treated as an unknown token, or actually consumed so the first
real word is dropped by the `[1:]` slice.

The tokenizer calls also pass `src_lang=...`, which OPUS Marian tokenizers
do not use in the same way as NLLB.

## `summary.py` only labels ten rows

```python
df = pd.read_csv(input_file_path)[:10]
```

The README describes a dataset-scale silver-label run. The file as
committed labels a smoke slice. A full run needs that slice removed.

## Model size triangle

| File | Checkpoint |
| --- | --- |
| `finetune.py` | `google/mt5-large`, saved under `./large_model` |
| `use_model.py` | tokenizer `google/mt5-small`, weights `small_model` |
| `eval.py` | tokenizer `google/mt5-small`, weights `small_model` |

Demo and evaluation do not load the checkpoint `finetune.py` writes.
`use_model.py` also draws its test split from
`ScandEval/nordjylland-news-summarization-mini`, while `eval.py` uses
`alexandrainst/nordjylland-news-summarization`. Column names
(`input_text` / `target_text`) match, but the rows do not.

## Generation settings that fight each other

- Labelling T5: `num_beams=2`, `max_length=80`, `repetition_penalty=5.0`.
  A repetition penalty of 5 is extreme; it is a blunt instrument against
  copied source n-grams.
- Fine-tune generate: `num_beams=4`, `no_repeat_ngram_size=3`,
  `length_penalty=0.8`, `min_length=9`, `max_length=128`.
- `use_model.py` demo: `no_repeat_ngram_size=1`. That forbids repeating
  *any* token, including Danish function words. It is a display bug, not
  a decoding strategy.

## Deprecated calls that will bite a 2026 rerun

- `use_auth_token=False` on `from_pretrained` (transformers now wants
  `token=`).
- `datasets.load_metric` (moved to `evaluate`).
- `evaluation_strategy` (renamed `eval_strategy` in recent
  transformers).
- `fp16=True` on mT5. mT5 + fp16 was a known source of NaNs; bf16 or
  full fp32 is the usual workaround.

## `translate_back.py` budget drift

The file computes `text_max_length = int(512 * 0.9)` and then calls
`split_into_sentences(article, max_length, tokenizer)` with `max_length`
(512), not `text_max_length`. Combined with the missing long-sentence
saw, back-translation packing is a different algorithm from hop 1.

`pakhus.scars.scan_repo()` prints this inventory. The workbook treats
each scar as an exercise, not as a silent fix.
