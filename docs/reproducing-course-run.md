# Reproducing the 2023 course run

This is a checklist, not a guarantee. The original dump, GPU box, and hub revisions are gone from this repo. You can still reconstruct the *procedure*.

## 0. Decide what “reproduced” means

| Claim | What you need |
| --- | --- |
| Scripts still import and the CSV contracts hold | `examples/` + this docs folder |
| A Danish mT5 that was trained the same *way* | CUDA, both OPUS-MT directions, a news dump, hours of training |
| The same numeric ROUGE as the 2023 slide | not possible from git alone (no metrics file, no seed, no dump) |

## 1. Environment

- [ ] Python 3.10 or 3.11 (3.12 may work; untested in 2023)
- [ ] CUDA torch that matches the driver
- [ ] `pip install -r requirements.txt`
- [ ] `nltk.download('punkt')`
- [ ] `huggingface-cli` login only if your network setup requires it (public models otherwise)

## 2. Models on disk

- [ ] Convert `Helsinki-NLP/opus-mt-da-en` → `models/opus-mt-da-en_ct2`
- [ ] Convert `Helsinki-NLP/opus-mt-en-da` → `models/opus-mt-en-da_ct2`
- [ ] Confirm both folders load:  
      `python -c "import ctranslate2; ctranslate2.Translator('models/opus-mt-da-en_ct2', device='cpu')"`

## 3. Unlabeled dump

- [ ] CSV named `10000_articles_without_linebreaks.csv`
- [ ] Columns `id`, `article text`
- [ ] UTF-8, unique ids, no HTML
- [ ] Spot-check that articles are Danish news, not mixed-language crawls

If you only want to test plumbing, copy the 12-row example file to that name and keep `summary.py`’s `[:10]` for a minute.

## 4. Labeling

- [ ] `python translate.py` → `translated_articles.csv`
- [ ] Read 5 random `translated` cells. If the first word is missing, fix the `[1:]` slice *before* summarizing 10k rows
- [ ] Remove `[:10]` in `summary.py`
- [ ] `python summary.py` → `summarized_file_ml80_rp5.0.csv`
- [ ] Read 5 English summaries. If they are generic (“The article discusses…”), the English hop or chunking is off
- [ ] `python translate_back.py` → `labeled_dataset_ml80_rp5.0.csv`
- [ ] Read 5 Danish `summary` cells with a Danish speaker if you have one

## 5. Split

- [ ] Shuffle by `id`
- [ ] Write `datasets/train_dataset.csv`, `datasets/validation_dataset.csv`, `datasets/test_dataset.csv`
- [ ] Columns `id`, `body`, `summary`
- [ ] No id in more than one split
- [ ] Optional: hold out any article you know is also in Nordjylland

`examples/toy_labeling_pipeline.py` shows one simple split for the tiny corpus.

## 6. Train

- [ ] Confirm GPU memory vs `mT5-large` + batch 8 + fp16
- [ ] `python finetune.py`
- [ ] Expect one generate-eval per epoch (slow)
- [ ] Confirm `./large_model` exists and contains `config.json` + weights
- [ ] Record the printed train log even though `log_level="error"` hides most of it (`logging_steps` still writes some trainer lines)

## 7. Point eval at the model you actually trained

- [ ] Either copy `large_model` → `small_model` **and** change `model_name` to `google/mt5-large` in both eval scripts,  
      or train a true small model into `small_model` and keep `google/mt5-small`
- [ ] `python use_model.py` — read the text, do not only glance
- [ ] Set `dataloader_drop_last=False` in `eval.py` if you intend to report a number
- [ ] `python eval.py` — save the dict

## 8. What to write down

A reproduction note should include:

- date, GPU type, torch + transformers + ctranslate2 versions,
- hub revisions (`huggingface-cli repo info ...` or the commit in the cache folder name),
- row counts at each CSV stage,
- whether the OPUS prefix slice was left intact,
- generate settings for T5 (`ml80_rp5.0`) and mT5,
- Nordjylland dataset name + split,
- ROUGE-1/2/L and BERTScore F1.

Without that paragraph, the next you will not know what the numbers mean.

## 9. Faster “did I break the repo?” path

Skip GPUs:

```bash
pip install -r requirements-examples.txt
python examples/validate_example_data.py
python examples/sentence_chunking_demo.py
python examples/toy_labeling_pipeline.py
python examples/length_stats.py
```

All four should exit 0. That is the regression gate for documentation changes.
