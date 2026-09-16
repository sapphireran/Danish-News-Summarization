# Troubleshooting

Failures this repository actually produces, in the order you are likely to hit them.

## `FileNotFoundError: 10000_articles_without_linebreaks.csv`

`translate.py` looks in the current working directory for that exact name. The file was never in git.

**Fix:** point the literal at your dump, or copy [`examples/data/raw_danish_articles.csv`](../examples/data/raw_danish_articles.csv) to that name for a two-minute syntax run (you will still need CTranslate2 weights for a real translate).

## `RuntimeError` / CTranslate2 cannot open `models/opus-mt-da-en_ct2`

`Ctranslate_converter.py` never built that folder.

**Fix:** convert `Helsinki-NLP/opus-mt-da-en` as in [models.md](models.md). Confirm the folder contains `config.json` and a model binary.

## First word missing on every translation

Both `translate()` functions decode `hypotheses[0][1:]`. That slice assumes a forced language-code prefix. OPUS-MT often has no such prefix, so you delete a real token (`The`, `En`, a name).

**Fix:** compare `hypotheses[0]` vs `hypotheses[0][1:]` on three sentences. If the first token is a Danish/English word rather than `eng_Latn` / `dan_Latn`, stop slicing.

## Translations look like the source language

Wrong CTranslate2 folder (en-da used for da-en), or the tokenizer does not match the converter source model. The da-en script must use the da-en tokenizer; the en-da script must use the en-da tokenizer. Mixing them produces fluent junk.

## `summary.py` finishes in seconds and the CSV has 10 rows

```python
df = pd.read_csv(input_file_path)[:10]
```

Remove the slice. The output name will still say `ml80_rp5.0`; that is fine.

## `CUDA out of memory` in `finetune.py`

See the memory ladder in [training.md](training.md). Also confirm you did not accidentally start a second trainer against the same GPU. `per_device_eval_batch_size=8` with `predict_with_generate=True` and beams=4 can OOM even when training stepped fine — drop the eval batch first.

## `fp16` / `GradScaler` errors on CPU

`fp16=True` is a CUDA feature. Set it `False` on CPU, or do not run `finetune.py` on CPU.

## `sentencepiece` / tokenizer errors for mT5

Install `sentencepiece` from `requirements.txt`. Delete a half-downloaded hub folder under `~/.cache/huggingface/hub/` if the error mentions a corrupt `spiece.model`.

## `KeyError: 'article text'` or `KeyError: 'body'`

Wrong stage file. Raw dump uses `article text`. Everything after `translate.py` uses `body`. Fine-tune uses `body` + `summary`. Eval uses `input_text` + `target_text`. Run `python examples/validate_example_data.py` to see the contracts.

## `remove_columns` failed on Nordjylland

Hub schema changed (extra or renamed columns). Print `test_dataset.column_names` and edit the `remove_columns` list. Do not remove columns that no longer exist; HF will raise.

## `datasets.load_metric` ImportError / deprecation

Newer `datasets` removed `load_metric`. Install the `evaluate` package (already in `requirements.txt`) and switch to `evaluate.load("rouge")` / `evaluate.load("bertscore")`, **or** pin `datasets` to a 2.14–2.16 line that still has `load_metric`.

## Eval numbers are nonsense / tokenizer warning about unused tokens

You loaded `small_model` weights that came from `mT5-large` (or the other way around) with the opposite tokenizer. Match hub size, folder, and `from_pretrained` id.

## Printed article in `use_model.py` does not match the printed summary

Batch size 2 vs index `i`. See [evaluation.md](evaluation.md).

## ROUGE is 0.0 for every epoch

Usual causes:

- generations are empty (`min_length` / bad checkpoint / all-pad decode),
- labels stayed as `-100` because decode ran before the `np.where` fix (the committed code does fix this),
- NLTK `punkt` missing so `sent_tokenize` misbehaves (less often → exactly 0.0),
- you evaluated a randomly initialized config without `from_pretrained` weights (the committed script does load weights).

Print three `decoded_preds` inside `compute_metrics` before you touch hyperparameters.

## BERTScore downloads a huge XLM-R and then dies

Disk or network. `model_type="xlm-roberta-large"` is required by the committed script. You can temporarily switch to `xlm-roberta-base` for a smoke test; do not compare those F1s to a large run.

## CTranslate2 wheel is CPU-only on a GPU machine

`pip show ctranslate2` and check the filename. Reinstall the CUDA build that matches your driver. `Translator(..., device="cuda")` then stops falling back.

## Excel destroyed `æøå`

Re-export the CSV as UTF-8. The Python scripts already request `encoding='utf-8'`. The damage happens in the spreadsheet, not in OPUS-MT.

## Example scripts: `nltk` punkt missing

`examples/lib/text_chunking.py` falls back to a regex sentence splitter. Results will not match NLTK exactly. Install punkt for apples-to-apples pack boundaries (`python -c "import nltk; nltk.download('punkt')"`).

## Example `toy_labeling_pipeline.py` summaries look too extractive

That is the point. The toy path is first-N Danish sentences, not T5. Compare them to the hand-written pivot summaries in `examples/data/labeled_danish.csv` using `examples/length_stats.py`.
