# Troubleshooting

Known mismatches between the short original README and the scripts, plus failures that show up when the 2023 code is run on a current stack.

## Converter output does not match `translate.py`

**Symptom:** `ctranslate2.Translator("models/opus-mt-da-en_ct2")` raises a missing-directory error.

**Cause:** `Ctranslate_converter.py` only converts `opus-mt-en-da`.

**Fix:** Convert `Helsinki-NLP/opus-mt-da-en` to `models/opus-mt-da-en_ct2` as well. See [models.md](models.md).

## Summaries stop after ten articles

**Symptom:** `summarized_file_ml80_rp5.0.csv` and the labeled file have 10 rows.

**Cause:** `df = pd.read_csv(input_file_path)[:10]` in `summary.py`.

**Fix:** Delete the slice for a full run. Keep it for a wiring test.

## `finetune.py` cannot find CSV columns

**Symptom:** `KeyError` on `body` / `summary` / `id` during `map`.

**Cause:** The split files were saved with the raw dump's `article text` header, or with `translated` still in place of `summary`.

**Fix:** Headers must be exactly `id,body,summary`. Validate with:

```bash
python -m examples.inspect_sample --validate-dir examples/sample_data
```

or against your own `datasets/` folder after you copy the same function.

## `load_best_model_at_end` and metric name

**Symptom:** Trainer cannot find `rouge_1_mid_fmeasure`.

**Cause:** `compute_metrics` failed (ROUGE metric download, missing `nltk.punkt`, or generate errors) so the key never appeared.

**Fix:** Download `punkt`, ensure `predict_with_generate=True`, and confirm `datasets.load_metric("rouge")` works in a REPL.

## `datasets.load_metric` is deprecated or missing

**Symptom:** `AttributeError: module 'datasets' has no attribute 'load_metric'`.

**Cause:** Newer `datasets` removed the helper.

**Fix:** `pip install evaluate` and switch those lines to `evaluate.load("rouge")` / `evaluate.load("bertscore")`. This write-up does not change the root scripts.

## `evaluation_strategy` unexpected argument

**Symptom:** `TypeError` in `Seq2SeqTrainingArguments`.

**Cause:** Transformers renamed the argument.

**Fix:** Use `eval_strategy="epoch"` on the newer package, or install a 2023-era Transformers.

## `use_auth_token` warning

**Symptom:** Deprecation warning on tokenizer load.

**Cause:** The argument was replaced by `token`.

**Fix:** Ignore, or delete `use_auth_token=False`. OPUS-MT models are public.

## CUDA / fp16

**Symptom:** `finetune.py` crashes on CPU with an fp16 error, or OOM on a small GPU.

**Cause:** `fp16=True` and `google/mt5-large` with 1024-token inputs.

**Fix:** On CPU, set `fp16=False`. On a small GPU, switch `model_name` to `google/mt5-small`, lower `per_device_train_batch_size`, or shorten `max_length` on the encoder.

## BERTScore download or OOM during `eval.py`

**Symptom:** Eval hangs on first metric call, or CUDA OOM after training succeeded.

**Cause:** `xlm-roberta-large` is pulled into the same GPU.

**Fix:** Run eval after freeing the training process. If needed, change `model_type` to a smaller multilingual encoder. Scores will not match a large-XLM-R run.

## Printed inspection inputs look misaligned

**Symptom:** The article printed in `use_model.py` does not match the reference beside it.

**Cause:** Input text is indexed by batch number, not by `batch_size * i`. See [evaluation.md](evaluation.md).

## mT5 generates empty or tiny strings

**Symptom:** Decoded hypotheses are empty or a few subwords.

**Cause:** Common on under-trained mT5 or when `pad_token` / extra ids are mishandled. Also happens if you evaluate a randomly initialized folder named `small_model`.

**Fix:** Confirm `small_model` is a real `save_pretrained` of a trained seq2seq model. Check `min_length` if you switch inspection to the training config.

## NLTK `punkt` missing

**Symptom:** `LookupError: punkt`.

**Fix:**

```bash
python -c "import nltk; nltk.download('punkt')"
```

Newer NLTK also wants `punkt_tab` for some tokenizers:

```bash
python -c "import nltk; nltk.download('punkt_tab')"
```

The example chunker in `examples/text_chunking.py` uses a small regex sentence split so the CPU demos do not depend on NLTK.

## CTranslate2 device / compute type

**Symptom:** Translator fails on GPU with a compute-type error.

**Cause:** Default export may not match the GPU.

**Fix:** Pass `compute_type` that CTranslate2 documents for your card, or run `device="cpu"` to isolate whether the issue is the converted graph or the device.

## Hugging Face dataset names

**Symptom:** `load_dataset("ScandEval/nordjylland-news-summarization-mini")` or the Alexandrainst set 404s.

**Cause:** Dataset ids move. `eval.py` already shows one such move in a comment (mini set commented out, full set used).

**Fix:** Search Hugging Face for the current Nordjylland news summarization id and update the string. Column names may also change; the scripts expect `input_text` and `target_text`.

## Example tests fail after editing sample CSVs

**Symptom:** `unittest` failures in `test_schemas` or `test_demo_pipeline`.

**Cause:** The tests pin column sets and the five known ids.

**Fix:** If you add a sixth fictional article, update the tests and the split files together. Keep fixtures author-written; do not paste copyrighted news into `examples/sample_data/`.
