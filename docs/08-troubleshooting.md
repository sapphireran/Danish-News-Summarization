# Troubleshooting

Symptoms you actually hit with these scripts, grouped by stage. Example-suite issues are at the end.

## Environment

### `CUDA out of memory` during `finetune.py`

- Lower `per_device_train_batch_size` from 8 to 2 and set `gradient_accumulation_steps=4`.
- Switch `google/mt5-large` → `google/mt5-base` for a smoke run.
- Turn off `predict_with_generate` on train-time eval if you only need a loss curve first.
- Confirm nothing else holds the GPU (`nvidia-smi`). CTranslate2 translators from a previous notebook cell will.

### `fp16` overflow / `nan` loss

mT5 + fp16 on older GPUs can diverge. Try:

- `bf16=True` and `fp16=False` on Ampere+.
- A lower learning rate (`1e-4`).
- Gradient clipping via `max_grad_norm=1.0` (not set in the 2023 args).

### `ImportError: cannot import name 'load_metric'`

Modern `datasets` dropped `load_metric`. Either:

```bash
python -m pip install "datasets<2.16"
```

or change the metric block to `evaluate.load("rouge")` / `evaluate.load("bertscore")`. The example toy script avoids this import entirely.

### `Seq2SeqTrainingArguments` unexpected keyword `evaluation_strategy`

Rename to `eval_strategy` on Transformers 4.41+, or pin `transformers<4.41`.

## Conversion and translation

### CTranslate2 cannot open `models/opus-mt-da-en_ct2`

The committed converter only writes the **en→da** directory. Uncomment the da→en block (or run a second converter) before `translate.py`.

### Translations look like they dropped the first letter / first word

`translate()` decodes `hypotheses[0][1:]`, assuming a language-code prefix. OPUS-MT may not emit one, so you strip a real piece of the sentence. Inspect `result.hypotheses[0][:3]` on a single example. If you do not see a language code, decode the full hypothesis.

### Entire articles become one English sentence with missing periods

Pack joining uses spaces, and OPUS-MT sometimes drops terminal punctuation. `sent_tokenize` on the English side then under-splits, and T5 sees a wall of text. A cheap repair: re-insert `". "` when a generated sentence lacks sentence-final punctuation before joining.

### `LookupError: resource punkt`

```python
import nltk
nltk.download("punkt")
nltk.download("punkt_tab")
```

On air-gapped machines, download once elsewhere and point `NLTK_DATA` at the folder.

## Summarization

### Output CSV has 10 rows

`summary.py` contains `df[:10]`. Remove it.

### English summaries repeat the same clause

`repetition_penalty=5.0` should suppress this; if it still happens, the pack is mostly boilerplate (sports line scores, weather tables). Filter tables before summarizing.

### Summaries are in English after `translate_back.py`

You pointed `model_path` at the da→en converter, or you never ran Stage 4 and are reading `summarized_file_*.csv` by mistake. Check the filename and a single `summary` cell for `æøå`.

## Fine-tuning

### `KeyError: 'body'` or `'summary'`

The split CSVs do not match [04-dataset-schema.md](04-dataset-schema.md). A common mistake is keeping `article text` or `target_text`.

### `KeyError: rouge_1_mid_fmeasure`

`compute_metrics` failed or returned empty (generation error). Look a few lines higher for a tokenize / decode exception. Also confirm `predict_with_generate=True`.

### Validation ROUGE is excellent, official eval is poor

You evaluated the silver-label "test" split, or the official test overlaps your dump. See [06-limitations-and-ethics.md](06-limitations-and-ethics.md).

### `use_model.py` prints the wrong article next to a generation

Known alignment bug: it indexes `input_text[i]` with the batch index. Use `eval.py` or write a tiny aligned loop if you need to quote examples.

## Evaluation

### BERTScore download of `xlm-roberta-large` fails

Network or disk. You can temporarily comment the BERTScore block and report ROUGE only; document the omission.

### Metrics dict keys look like `rouge_rouge1_mid_fmeasure`

Expected. See [05-evaluation.md](05-evaluation.md).

### Extremely low ROUGE with fluent-looking Danish

The model may be generating Danish that does not overlap the reference lead (still useful, poorly scored) *or* it may be generating fluent off-topic text. Read 10 examples before retuning.

## Example suite

### `pytest` cannot import `examples.text_chunking`

Run from the repository root:

```bash
python -m pytest tests/
```

`tests/conftest.py` puts the repo root on `sys.path`.

### Chunking demo wants NLTK data

Same `punkt` download as above. Tests that need sentence tokenization call a helper that skips or downloads.

### Pandas `UnicodeDecodeError` on a sample CSV

Re-save as UTF-8. The committed files are UTF-8 without BOM. Windows Excel often rewrites them as cp1252; do not commit that.

### Someone added a real news article to `examples/data/`

Do not. Revert the file. The tests do not catch copyright; reviewers must. Example ids must stay `SYN-*`.
