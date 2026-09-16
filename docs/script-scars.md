# December 2023 scripts, left as they are

This branch documents the root files. It does not patch them. A later
fine-tune should see the same scars the 2023 hand-in had.

| File | What it actually does | Scar worth a sticky note |
| --- | --- | --- |
| `Ctranslate_converter.py` | Converts `opus-mt-en-da` into `models/opus-mt-en-da_ct2` | da→en and both NLLB converts are commented out |
| `translate.py` | Reads `10000_articles_without_linebreaks.csv` (`id`, `article text`) and writes `translated_articles.csv` | NLLB prefixes; needs the da→en CT2 dir that the converter does not build |
| `summary.py` | Reads `translated_articles.csv`, T5-summarizes `translated` | `df = pd.read_csv(...)[:10]` is still there. `max_length=80`, `repetition_penalty=5.0` |
| `translate_back.py` | Reads `summarized_file_ml80_rp5.0.csv`, writes `labeled_dataset_ml80_rp5.0.csv` | Same NLLB prefix decode; column `summary` is now Danish |
| `finetune.py` | Loads `datasets/{train,validation,test}_dataset.csv`, trains `google/mt5-large`, saves `./large_model` | No script writes those three CSVs. 20 epochs, Adafactor, `fp16`, metric `rouge_1_mid_fmeasure` |
| `use_model.py` | Loads `small_model`, prints 5 generations on ScandEval mini | Train saved `large_model` |
| `eval.py` | Loads `small_model`, scores Nordjylland-News test with ROUGE + BERTScore | `input_text` / `target_text`, not `body` / `summary`. `xlm-roberta-large` |

## Filenames the scripts agree on

```
10000_articles_without_linebreaks.csv
        → translated_articles.csv
        → summarized_file_ml80_rp5.0.csv
        → labeled_dataset_ml80_rp5.0.csv
        → (manual split) datasets/train_dataset.csv
                         datasets/validation_dataset.csv
                         datasets/test_dataset.csv
```

`maalestok fixtures` writes the same *column contracts* on sixteen
fictional rows. It does not invent a 10k dump.

## Eval column rename

`finetune.py` tokenizes `body` / `summary`. `eval.py` tokenizes
`input_text` / `target_text` and drops `text_len` / `summary_len`.
A labeled CSV from `translate_back.py` cannot be passed to `eval.py`
without a rename. The public Nordjylland set is a different distribution
than the silver labels anyway.
