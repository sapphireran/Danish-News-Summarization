# Reproduction runbook

A practical checklist for rerunning the 2023 project on a personal machine.
Weights and the original news dump stay local.

## Directory layout

From the repository root:

```text
Danish-News-Summarization/
├── Ctranslate_converter.py
├── translate.py
├── summary.py
├── translate_back.py
├── finetune.py
├── use_model.py
├── eval.py
├── docs/
├── examples/
├── tests/
├── 10000_articles_without_linebreaks.csv   # not in git
├── translated_articles.csv                 # generated
├── summarized_file_ml80_rp5.0.csv          # generated
├── labeled_dataset_ml80_rp5.0.csv          # generated
├── datasets/
│   ├── train_dataset.csv
│   ├── validation_dataset.csv
│   └── test_dataset.csv
├── models/
│   ├── opus-mt-da-en_ct2/
│   └── opus-mt-en-da_ct2/
├── mt5-summarize-large/                    # trainer checkpoints
├── large_model/                            # finetune.py export
└── small_model/                            # eval / use_model default
```

Create the empty folders before the first script:

```bash
mkdir -p models datasets
```

## Python environment

The course scripts expect a 2023-era stack: PyTorch with CUDA, Transformers,
datasets, evaluate, CTranslate2, NLTK, pandas, tqdm, and a ROUGE extra.

A starting pin set (personal rerun, not the original lab image):

```text
torch
transformers
datasets
evaluate
ctranslate2
sentencepiece
protobuf
nltk
pandas
tqdm
numpy
accelerate
rouge-score
bert-score
```

`requirements.txt` at the repo root lists the same packages. The
model-free examples only need the standard library; their tests run with
`python3 -m unittest`.

After installing NLTK, download the sentence model once:

```bash
python3 -c "import nltk; nltk.download('punkt')"
```

Newer NLTK versions may want `punkt_tab` as well.

## GPU vs CPU

| Step | GPU needed? |
| --- | --- |
| CTranslate2 conversion | No, but the conversion itself downloads OPUS-MT |
| `translate.py` / `translate_back.py` | Strongly preferred |
| `summary.py` | Strongly preferred |
| `finetune.py` mT5-large, fp16 | Yes |
| `use_model.py` / `eval.py` | Preferred |
| `examples/*` and `tests/*` | No |

On CPU, CTranslate2 still runs, just slowly. mT5-large fine-tuning with
`fp16=True` will not.

## Command order

```bash
# 1. Convert both OPUS-MT directions (uncomment da→en first)
python Ctranslate_converter.py

# 2. Danish articles → English
python translate.py

# 3. English summaries (remove the [:10] slice for a full run)
python summary.py

# 4. Summaries → Danish silver labels
python translate_back.py

# 5. Split labeled_dataset_ml80_rp5.0.csv into datasets/*.csv
python examples/split_labeled_dataset.py \
  --input labeled_dataset_ml80_rp5.0.csv \
  --output-dir datasets \
  --train-ratio 0.8 \
  --val-ratio 0.1

# 6. Fine-tune
python finetune.py

# 7. Inspect / evaluate (point at the directory you actually trained)
python use_model.py
python eval.py
```

## Smoke-test the CSV contracts without models

```bash
python3 examples/validate_csvs.py --sample-dir examples/sample_data
python3 examples/inspect_dataset.py --path examples/sample_data/03_labeled_sample.csv
python3 examples/demo_chunking.py
python3 examples/toy_pipeline.py --sample-dir examples/sample_data --output-dir /tmp/dns-toy
python3 -m unittest discover -s tests -v
```

Those commands are the ones this archive guarantees. The GPU scripts depend
on local weights and on Hugging Face being reachable.

## Common failures

| Symptom | Likely cause |
| --- | --- |
| `Translator` cannot open `models/opus-mt-da-en_ct2` | Converter left that direction commented out |
| `KeyError: 'article text'` | Stage 0 CSV used `body` instead of `article text` |
| `KeyError: 'translated'` | `summary.py` pointed at a labeled file, not stage 1 |
| `summary.py` finishes in seconds | The `[:10]` debug slice is still there |
| CUDA / fp16 error in `finetune.py` | No GPU, or `fp16=True` on CPU |
| `save_pretrained` missing tokenizer | Expected; load `google/mt5-large` tokenizer separately |
| ROUGE import error | `rouge-score` extra not installed |
| BERTScore download hang | First-time `xlm-roberta-large` pull |
| Empty generations | Local `small_model` directory missing or incomplete |

## What not to commit

Do not add the news dump, CTranslate2 directories, trainer checkpoints, or
exported mT5 folders. The root `.gitignore` already lists those names.
