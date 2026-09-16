# Setup

## Python

The 2023 scripts were written against a fairly standard Hugging Face stack: `transformers`, `datasets`, `evaluate`, `torch`, `nltk`, `pandas`, and `ctranslate2`. A root [`requirements.txt`](../requirements.txt) now records those libraries. The example scripts have a thinner file, [`requirements-examples.txt`](../requirements-examples.txt).

Suggested layout:

```bash
cd /path/to/Danish-News-Summarization
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-examples.txt   # laptop / CI
# or
pip install -r requirements.txt            # full pipeline
```

`torch` wheels are platform-specific. If you are installing the full stack on a CUDA box, install the PyTorch build that matches your driver *first*, then the rest of `requirements.txt`.

## NLTK punkt

`translate.py`, `translate_back.py`, `summary.py`, and `use_model.py` all call `nltk.download('punkt')` at import time. The example scripts do the same, but they also fall back to a regex splitter if punkt is missing so a docs walkthrough is not blocked by a download.

On a clean machine:

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

`punkt_tab` is the newer NLTK 3.8.2+ resource name. Older scripts only mention `punkt`.

## Hardware

| Stage | Practical minimum | Notes |
| --- | --- | --- |
| Example scripts | Any CPU, < 200 MB RAM | No model weights |
| OPUS-MT via CTranslate2 | CPU works; GPU is much faster | 10k articles is painful on CPU |
| English T5 summarizer | GPU recommended | `summary.py` generates per chunk |
| `mT5-large` fine-tune | One 16–24 GB GPU is the intended setup | `per_device_train_batch_size=8`, `fp16=True` |
| `mT5-small` eval | 8 GB GPU or a patient CPU | `eval.py` uses eval batch 64 |

`finetune.py` sets `fp16 = True`. That flag is a CUDA path. A CPU-only attempt will need it turned off and the batch size dropped.

## Disk

Plan for:

- Helsinki-NLP OPUS-MT `da-en` and `en-da` (a few hundred MB each, plus CTranslate2 copies under `models/`).
- `mrm8488/t5-base-finetuned-summarize-news`.
- `google/mt5-large` (this is the big one) and trainer checkpoints in `mt5-summarize-large/`.
- Hugging Face hub cache (`~/.cache/huggingface/`).
- Intermediate CSVs. A 10k-article run with full article text in three languages is not a tiny file.

`.gitignore` already excludes `models/`, `large_model/`, `small_model/`, `mt5-summarize-*/`, and the root-level generated CSVs.

## Hugging Face access

Some scripts still pass `use_auth_token=False` into `AutoTokenizer.from_pretrained`. That argument is the old name for “do not send a token”. You do **not** need a Hugging Face login for:

- `Helsinki-NLP/opus-mt-da-en`
- `Helsinki-NLP/opus-mt-en-da`
- `google/mt5-small` / `google/mt5-large`
- `mrm8488/t5-base-finetuned-summarize-news`
- `alexandrainst/nordjylland-news-summarization`
- `ScandEval/nordjylland-news-summarization-mini`

If a download 401s, it is usually a cache / network problem, not a missing gated-model agreement.

## Environment variables the scripts do *not* read

There is no `.env`, no `argparse`, and no config file. Paths are string literals:

| Script | Hard-coded input | Hard-coded output / model |
| --- | --- | --- |
| `Ctranslate_converter.py` | `Helsinki-NLP/opus-mt-en-da` | `models/opus-mt-en-da_ct2` |
| `translate.py` | `10000_articles_without_linebreaks.csv` | `translated_articles.csv`, `models/opus-mt-da-en_ct2` |
| `summary.py` | `translated_articles.csv` | `summarized_file_ml80_rp5.0.csv` |
| `translate_back.py` | `summarized_file_ml80_rp5.0.csv` | `labeled_dataset_ml80_rp5.0.csv`, `models/opus-mt-en-da_ct2` |
| `finetune.py` | `datasets/train_dataset.csv` (and val/test) | `mt5-summarize-large/`, `./large_model` |
| `use_model.py` | HF mini Nordjylland split | local folder `small_model` |
| `eval.py` | HF full Nordjylland test split | local folder `small_model` |

If you want to point a script at the example CSVs, copy or symlink them to those names, or edit the literals. The example scripts read from `examples/data/` instead so they never clobber a real run.

## Tokenizer / sentencepiece

`mT5` needs `sentencepiece`. If `AutoTokenizer.from_pretrained("google/mt5-small")` raises a SentencePiece error, install `sentencepiece` from `requirements.txt` and retry. Do not try to reuse a BERT wordpiece tokenizer here; the scripts assume the model’s own tokenizer.

## CUDA vs CPU device strings

Translation scripts build a `torch.device` *and* pass `device="cuda" if torch.cuda.is_available() else "cpu"` into `ctranslate2.Translator`. Those two should stay in sync. CTranslate2 will not automatically follow `CUDA_VISIBLE_DEVICES` in every build; if you see “no GPU” while `nvidia-smi` shows one, check that the `ctranslate2` wheel is the CUDA build, not the CPU-only wheel.
