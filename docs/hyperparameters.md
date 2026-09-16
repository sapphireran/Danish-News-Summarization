# Hyperparameter cheat sheet

Values below are copied from the checked-in scripts. They are not claims about optimality.

## Sentence packing (translation and summarization)

| Knob | `translate.py` | `summary.py` | `translate_back.py` |
| --- | --- | --- | --- |
| Model max | 512 | 512 | 512 |
| Pack budget | `int(512 * 0.9)` = 460 | 512 | called with 512 (`max_length`), not 460 |
| Long-sentence splitter | yes, on `,;:` and overflow | yes | no |
| Tokenizer used for lengths | OPUS `da-en` | T5 news | OPUS `en-da` |

Packing is by **tokenizer tokens**, not characters. The long-sentence helper, however, increments `current_length` by `len(word) + 1` (characters) and compares to a token budget. That unit mix is documented in [design-notes.md](design-notes.md).

## English T5 decode (`summary.py`)

| Knob | Value |
| --- | --- |
| `num_beams` | 2 |
| `max_length` | 80 |
| `repetition_penalty` | 5.0 |
| `length_penalty` | 1.0 |
| `early_stopping` | True |
| rows processed | **10** (`[:10]`) |

## mT5 training (`finetune.py`)

| Knob | Value |
| --- | --- |
| base | `google/mt5-large` |
| source max | 1024 |
| target max | 128 |
| epochs | 20 |
| LR | 3e-4 |
| scheduler | polynomial |
| warmup | 1000 steps |
| optimizer | Adafactor |
| weight decay | 0.01 |
| train batch | 8 |
| eval batch | 8 |
| grad accum | 1 |
| fp16 | True |
| dropout (config) | 0.1 |
| beams (config) | 4 |
| gen max (config / trainer) | 128 |
| min gen length (config) | 9 |
| length penalty (config) | 0.8 |
| no-repeat ngram (config) | 3 |
| best-model metric | ROUGE-1 mid F |

## mT5 qualitative decode (`use_model.py`)

| Knob | Value |
| --- | --- |
| tokenizer name | `google/mt5-small` |
| weights | `small_model` |
| source max | 1024 |
| label max (tokenize only) | 180 |
| `num_beams` | 2 |
| `no_repeat_ngram_size` | 1 |
| `max_length` | 128 |
| dataloader batch | 2 |
| printed batches | 5 |

## mT5 quantitative decode (`eval.py`)

| Knob | Value |
| --- | --- |
| tokenizer name | `google/mt5-small` |
| weights | `small_model` |
| source max | 1024 |
| label max (tokenize only) | 128 |
| eval batch | 64 |
| `dataloader_drop_last` | True (last incomplete batch discarded) |
| BERTScore model | `xlm-roberta-large` |

Trainer evaluate uses the model’s generation config plus `predict_with_generate=True`. It does not copy `use_model.py`’s `no_repeat_ngram_size=1`.

## Suggested experiment axes (if you rerun)

These are personal notes, not a sweep that was run in 2023:

1. English `max_length` ∈ {40, 80, 128} — filename already anticipates this.
2. `repetition_penalty` ∈ {1.5, 3.0, 5.0} — 5.0 is unusually high.
3. Pivot model: OPUS-MT vs NLLB-600M (prefixes already written for NLLB).
4. Fine-tune size: `mt5-small` vs `mt5-base` vs `mt5-large`.
5. Target truncation 128 vs 180 vs 256, especially if silver summaries are concatenations.
6. Drop the `[:10]` cap, then sample 500 / 2k / full 10k silver pairs and plot Nordjylland ROUGE vs pair count.

Log each run as a new CSV suffix and a new output directory. Do not overwrite `labeled_dataset_ml80_rp5.0.csv` until you are sure you do not want that baseline.
