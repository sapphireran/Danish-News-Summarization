# Sample CSVs

All articles, translations and summaries in this folder are original
text written for the examples. They are **not** from TV2 Nord,
Nordjylland, or the 2023 course dump.

Place names (Østerhavn, Klitvig, Bøgebro, Gråholm, Havnkær) are
fictional. Any resemblance to a real news item is accidental.

| File | Pipeline stage |
| --- | --- |
| `sample_articles.csv` | raw dump (`id`, `article text`) |
| `sample_translated.csv` | after DA→EN |
| `sample_summarized.csv` | after English T5 |
| `sample_labeled.csv` | after EN→DA |
| `sample_finetune_{train,validation,test}.csv` | mT5 splits |

Do not edit these CSVs by hand. Change `examples/sample_catalog.py` and
run `python3 examples/write_sample_csvs.py`.

`ex-006-havn` is deliberately long so `chunking_demo.py` has to emit
several batches at `--max-length 40`.
