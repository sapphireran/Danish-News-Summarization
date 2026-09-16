# Known issues in the 2023 root scripts

These are observations from reading the checked-in files. The scripts were left as submitted; the new `docs/` and `examples/` layers document them instead of silently rewriting course history.

## Converter and translator disagree

`Ctranslate_converter.py` only converts `Helsinki-NLP/opus-mt-en-da`.

`translate.py` loads `models/opus-mt-da-en_ct2`.

A clean clone plus `python Ctranslate_converter.py` is not enough to run step 2. Uncomment the da→en converter (already present as comments) or convert that direction yourself.

## `summary.py` labels ten rows

```python
df = pd.read_csv(input_file_path)[:10]
```

This is a leftover smoke-test. A full silver set needs that slice removed. The output filename (`summarized_file_ml80_rp5.0.csv`) does not mention the slice, so it is easy to fine-tune on ten rows by accident.

## NLLB prefixes on OPUS-MT

Both translation scripts set `src_lang` / `tgt_lang` to Flores codes (`dan_Latn`, `eng_Latn`) and pass `target_prefix=[[tgt_lang], ...]`. That API matches the commented NLLB experiments in the converter. Marian/OPUS-MT models are not trained to expect those prefixes. Measure quality with prefixes stripped if you revive the pipeline.

## Fine-tune writes `large_model`, eval reads `small_model`

| Script | Base id | Local dir |
| --- | --- | --- |
| `finetune.py` | `google/mt5-large` | `./large_model` |
| `use_model.py` / `eval.py` | `google/mt5-small` | `small_model` |

Either a small model was trained in a later local edit that was never committed, or eval was pointed at an older checkpoint. Align names before trusting numbers.

## `use_model.py` prints the wrong article after batch 0

The generate loop iterates dataloader batches with `batch_size=2` but prints `split_dataset["test"]["input_text"][i]` where `i` is the batch index. Gold and prediction text come from the batch; the “input” line does not.

## `use_model.py` generate settings ≠ training config

Training config: beams 4, `no_repeat_ngram_size=3`, `min_length=9`, `length_penalty=0.8`.

Inspect script: beams 2, `no_repeat_ngram_size=1`, no min length.

`no_repeat_ngram_size=1` is especially harsh in Danish.

## Eval drops the last batch

`dataloader_drop_last=True` with `per_device_eval_batch_size=64` silently ignores a remainder of up to 63 Nordjylland test rows.

## Deprecated Hugging Face APIs

- `datasets.load_metric` → `evaluate.load`
- `use_auth_token=False` on `from_pretrained` → `token=False` or omit
- `evaluation_strategy` → `eval_strategy` in Transformers 4.41+ / 5
- `Seq2SeqTrainer(..., tokenizer=...)` → `processing_class` in recent Transformers

`requirements.txt` caps Transformers below 5 so the 2023 argument names still work.

## Mixed length units in `split_long_sentence`

Sentence packing uses tokenizer length. The overflow splitter uses `len(word) + 1` characters against the same numeric budget (460). See [pipeline.md](pipeline.md). Usually safe, sometimes over-split.

## `translate_back.py` packing uses `max_length` not `text_max_length`

`split_into_sentences` is called as `split_into_sentences(article, max_length, tokenizer)` with `max_length=512`, while `text_max_length = int(512 * 0.9)` is computed and unused. Summaries are short, so this rarely matters.

## No requirements file existed originally

Reproducing the course environment was guesswork. `requirements.txt` is a reconstructed list, not a frozen lockfile from 2023.

## Hardcoded paths, no CLI

Every I/O path is a module-level string. There is no `argparse`. The examples tree uses explicit paths under `examples/data/` so documentation runs do not overwrite a real `translated_articles.csv` at the repo root.

## `punkt` downloaded on every import

`nltk.download('punkt')` runs at import time in several scripts. Fine on a networked GPU box; noisy and slow in a tight loop or offline.

## No training seed

`finetune.py` does not set seeds. Numbers in a report should be treated as single-run.

## Silver `test_dataset.csv` vs Nordjylland test

`finetune.py` loads `datasets/test_dataset.csv` but never evaluates it. `eval.py` ignores that file and loads Nordjylland from the Hub. The silver test split is unused by the checked-in eval path.

## What the new examples do not fix

`examples/` does not patch the root scripts. It documents behavior and gives a safe playground. If you later fix the issues above, keep this list honest: delete a bullet only when the corresponding script change lands.
