# Reproducing the 2023 GPU run

This page is the long form of the root README. It assumes a machine with a
CUDA GPU, a few tens of GB of disk, and network access to Hugging Face.

## 0. Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt')"
```

`requirements-examples.txt` is enough for the offline walkthroughs and is
the only install the documentation tests use.

## 1. Convert both OPUS-MT models

Edit `Ctranslate_converter.py` so **both** `opus-mt-da-en` and
`opus-mt-en-da` convert. As committed, only en→da runs.

```bash
python Ctranslate_converter.py
```

Expect `models/opus-mt-da-en_ct2` and `models/opus-mt-en-da_ct2`.

## 2. Provide the Danish dump

Place a CSV named `10000_articles_without_linebreaks.csv` in the repository
root with columns `id` and `article text`. The 2023 dump is not in git.

To practise the rest of the tooling on invented text:

```bash
cp examples/data/sample_danish_articles.csv 10000_articles_without_linebreaks.csv
```

`translate.py` will then produce a ten-row English file.

## 3. Translate to English

```bash
python translate.py
```

Writes `translated_articles.csv`. Runtime is dominated by the number of
sentence windows, not the number of articles. Very long features cost more.

## 4. Summarise in English

Open `summary.py` and remove the `[:10]` slice if you want the full dump.
Then:

```bash
python summary.py
```

Writes `summarized_file_ml80_rp5.0.csv`. The first run downloads
`mrm8488/t5-base-finetuned-summarize-news`.

## 5. Translate summaries back

```bash
python translate_back.py
```

Writes `labeled_dataset_ml80_rp5.0.csv`.

## 6. Split for fine-tuning

Create `datasets/` and split the labelled file into
`train_dataset.csv`, `validation_dataset.csv`, and `test_dataset.csv`
(columns `id`, `body`, `summary`). The repository does not include a
splitter; `danish_news_sum.dataset.write_article_csv` is a convenient
writer if you script the split yourself.

Sanity-check first:

```bash
python examples/inspect_silver_labels.py --csv labeled_dataset_ml80_rp5.0.csv
```

## 7. Fine-tune

```bash
python finetune.py
```

Writes trainer logs to `mt5-summarize-large/` and the final weights to
`./large_model`. Copy or symlink into `small_model` if you want the
evaluation scripts to see the new run without editing paths.

## 8. Inspect and score

```bash
python use_model.py
python eval.py
```

`use_model.py` downloads the ScandEval mini split. `eval.py` downloads
Nordjylland News and, on first run, XLM-RoBERTa large for BERTScore.

## Offline path (no GPU)

```bash
pip install -r requirements-examples.txt
python examples/dry_run_pipeline.py
python examples/chunk_sample_articles.py
python examples/inspect_silver_labels.py
python examples/score_sample_summaries.py
python -m pytest tests
```

That is the path this documentation change is built around.

## Hyperparameter checklist

If you do not want to read the Python, print the dataclasses:

```bash
python examples/print_configs.py
```

or open `examples/configs/*.json`. They match the 2023 scripts. Changing
the JSON files does **not** change `finetune.py`; the root scripts still
use literals.
