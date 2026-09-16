# Reproducing the 2023 run

This is a personal course project. There is no Docker image, no `requirements.txt` in the original commit, and no data in git. The steps below reconstruct what the scripts assume.

If you only want to see the schemas and the chunking logic, skip this file and run [`../examples`](../examples). Those demos use the Python standard library plus the synthetic CSVs.

## Hardware

| Stage | Realistic device |
| --- | --- |
| CTranslate2 conversion | CPU is fine |
| `translate.py` / `translate_back.py` on 10k articles | one CUDA GPU; CPU only for a handful of rows |
| `summary.py` full file | one CUDA GPU |
| `finetune.py` (`mt5-large`, batch 8, 1024 tokens, fp16) | a 24 GB-class GPU or better; 16 GB may OOM |
| `eval.py` with BERTScore XLM-R large | GPU strongly preferred |
| `use_model.py` | GPU or CPU for a few batches |

The scripts all choose `cuda` if `torch.cuda.is_available()` else `cpu`. There is no multi-GPU `accelerate` config.

## Software (approximate 2023 stack)

The original environment was not frozen. A working-enough set for a rerun:

```
python>=3.9
torch          # CUDA build matching the driver
transformers
datasets
evaluate
accelerate     # often pulled in by recent trainers
sentencepiece  # required by MarianMT and mT5
protobuf
ctranslate2
pandas
numpy
nltk
tqdm
rouge-score    # backend for datasets/evaluate rouge
bert-score
```

Install NLTK punkt once:

```bash
python -c "import nltk; nltk.download('punkt')"
```

`use_auth_token=False` in the translate scripts is a deprecated Transformers argument. Current versions want `token=False` or just omit it for public models.

`datasets.load_metric` may error on new `datasets`. Switch those calls to `evaluate.load`.

## Directory layout the scripts expect

```
.
├── 10000_articles_without_linebreaks.csv
├── Ctranslate_converter.py
├── translate.py
├── summary.py
├── translate_back.py
├── finetune.py
├── eval.py
├── use_model.py
├── models/
│   ├── opus-mt-da-en_ct2/
│   └── opus-mt-en-da_ct2/
├── datasets/
│   ├── train_dataset.csv
│   ├── validation_dataset.csv
│   └── test_dataset.csv
├── large_model/          # written by finetune.py
└── small_model/          # read by eval.py and use_model.py
```

Create `models/` and `datasets/` yourself. The scripts do not mkdir except `./large_model` at the end of training.

## Command order

```bash
# 1. Convert both OPUS directions (uncomment da-en in Ctranslate_converter.py first)
python Ctranslate_converter.py

# 2. Danish articles → English
python translate.py

# 3. Remove the [:10] slice in summary.py before a full run
python summary.py

# 4. English summaries → Danish silver labels
python translate_back.py

# 5. Split labeled_dataset_ml80_rp5.0.csv into datasets/*.csv
#    (no script in repo; do this yourself)

# 6. Fine-tune
python finetune.py

# 7. Point eval/use_model at the checkpoint you actually trained
python use_model.py
python eval.py
```

Each step assumes the previous CSV exists in the **current working directory**. There are no CLI flags.

## Data you have to bring

1. A UTF-8 CSV named `10000_articles_without_linebreaks.csv` with `id` and `article text`.
2. Hugging Face access to:
   - `Helsinki-NLP/opus-mt-da-en`
   - `Helsinki-NLP/opus-mt-en-da`
   - `mrm8488/t5-base-finetuned-summarize-news`
   - `google/mt5-large` (train)
   - `google/mt5-small` (eval scripts as written)
   - `alexandrainst/nordjylland-news-summarization`
   - `ScandEval/nordjylland-news-summarization-mini`
   - `xlm-roberta-large` (BERTScore)

The Nordjylland datasets are public. The 10k dump is not redistributed here.

## Hugging Face cache

Plan for a populated `~/.cache/huggingface/`. Conversion plus T5 plus mT5-large plus XLM-R is many gigabytes. Set `HF_HOME` if the default disk is small.

## Determinism

Seeds are not set. CTranslate2, HF generate, and Adafactor will not replay bit-identical CSVs or metrics. For a paper-style table, fix:

```python
import random, numpy as np, torch
random.seed(s); np.random.seed(s); torch.manual_seed(s)
```

and record the Transformers / CTranslate2 versions.

## Minimal smoke test without the 10k dump

Use the fixtures:

```bash
python examples/demo_schema_walkthrough.py
python examples/demo_sentence_chunking.py
python examples/demo_pipeline_dry_run.py
python examples/demo_finetune_preview.py
python examples/demo_offline_metrics.py
```

Those commands do not need CUDA, CTranslate2, or Hub access. They are the supported way to check this documentation repo on a laptop.

## Legal / personal-use reminder

The silver-label pipeline copies news text through two translation models and a summarizer. That is fine as a student experiment on data you are allowed to use. Do not publish the 10k dump, the intermediate CSVs, or generated summaries of copyrighted articles unless you have the rights. The fixtures under `examples/data` are fictional and are the only sample articles intended to live in git.
