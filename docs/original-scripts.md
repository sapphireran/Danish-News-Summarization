# Original scripts

A map from each repository-root script to the stage config in
`danish_news_summarization.config.PIPELINE_STAGES`. Use this when you
are standing in the 2023 files and want the matching doc page.

## `Ctranslate_converter.py`

- **Stage name:** `convert_models`
- **Does:** `TransformersConverter("Helsinki-NLP/opus-mt-en-da")` →
  `models/opus-mt-en-da_ct2`
- **Also present, commented out:** NLLB 3.3B, NLLB 600M, opus-mt-da-en
- **Read next:** [models.md](models.md)

## `translate.py`

- **Stage name:** `translate_da_en`
- **Reads:** `10000_articles_without_linebreaks.csv` (`id`, `article text`)
- **Writes:** `translated_articles.csv` (`id`, `body`, `translated`)
- **Model:** `models/opus-mt-da-en_ct2`
- **Pack budget:** `int(512 * 0.9)`
- **Read next:** [pipeline.md](pipeline.md), [dataset.md](dataset.md)

## `summary.py`

- **Stage name:** `summarize_en`
- **Reads:** `translated_articles.csv`
- **Writes:** `summarized_file_ml80_rp5.0.csv`
- **Model:** `mrm8488/t5-base-finetuned-summarize-news`
- **Generate:** `max_length=80`, `repetition_penalty=5.0`, `num_beams=2`
- **Smoke-test slice:** `[:10]`
- **Read next:** [models.md](models.md)

## `translate_back.py`

- **Stage name:** `translate_en_da`
- **Reads:** the summarized CSV
- **Writes:** `labeled_dataset_ml80_rp5.0.csv` (`id`, `body`, `summary`)
- **Model:** `models/opus-mt-en-da_ct2`
- **Read next:** [dataset.md](dataset.md)

## `finetune.py`

- **Stage name:** `finetune_mt5`
- **Reads:** `datasets/train|validation|test_dataset.csv`
- **Writes:** `mt5-summarize-large/` checkpoints and `./large_model`
- **Model:** `google/mt5-large`
- **Best-model metric:** `rouge_1_mid_fmeasure`
- **Read next:** [training.md](training.md)

## `use_model.py`

- **Stage name:** `inspect_predictions`
- **Reads:** `ScandEval/nordjylland-news-summarization-mini` (test)
- **Writes:** stdout
- **Weights:** `small_model/`
- **Tokenizer:** `google/mt5-small`
- **Read next:** [evaluation.md](evaluation.md)

## `eval.py`

- **Stage name:** `evaluate`
- **Reads:** `alexandrainst/nordjylland-news-summarization` (test)
- **Writes:** a metrics dict to stdout
- **Weights:** `small_model/`
- **Metrics:** ROUGE mid F, BERTScore (da, xlm-roberta-large)
- **Read next:** [evaluation.md](evaluation.md)

## Run order (GPU)

```bash
python Ctranslate_converter.py   # uncomment da→en first
python translate.py
python summary.py                # remove [:10] for a full run
python translate_back.py
# split labeled_dataset_*.csv into datasets/{train,validation,test}_dataset.csv
python finetune.py
python use_model.py
python eval.py
```

## Run order (docs / examples, no GPU)

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
PYTHONPATH=. python examples/walk_one_article.py dn-001
PYTHONPATH=. python examples/compare_chunk_strategies.py
PYTHONPATH=. python examples/dry_run_pipeline.py
```
