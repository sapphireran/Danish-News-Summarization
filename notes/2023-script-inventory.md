# 2023 script inventory

One screen. Details in [`docs/script-contracts.md`](../docs/script-contracts.md).

| File | Input | Output | Model |
| --- | --- | --- | --- |
| `Ctranslate_converter.py` | Hub Marian | `models/opus-mt-en-da_ct2` | converter |
| `translate.py` | `10000_articles_without_linebreaks.csv` | `translated_articles.csv` | `opus-mt-da-en` ct2 |
| `summary.py` | `translated_articles.csv` `[:10]` | `summarized_file_ml80_rp5.0.csv` | news T5 |
| `translate_back.py` | that summarized CSV | `labeled_dataset_ml80_rp5.0.csv` | `opus-mt-en-da` ct2 |
| `finetune.py` | `datasets/{train,validation,test}_dataset.csv` | `./large_model` | `mt5-large` |
| `use_model.py` | ScandEval mini | stdout | `small_model` + `mt5-small` tok |
| `eval.py` | Nordjylland test | metrics dict | `small_model` + `mt5-small` tok |

Mismatches I will trip over on a rerun:

1. Converter does not build the DA→EN model `translate.py` loads.
2. Fine-tune writes `large_model`; eval/use read `small_model`.
3. Fine-tune is `mt5-large`; eval tokenizes as `mt5-small`.
4. `eval.py` column names look like ScandEval, not the alexandrainst card.
5. No `requirements` pin from the course machine (see [`requirements.txt`](../requirements.txt) for a reconstructed import list).
