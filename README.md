# Danish News Summarization

ITU *Advanced Natural Language Processing and Deep Learning* (2023) final
project: a Danish summarization student trained on **silver labels** from a
Danish → English → summarize → Danish hop.

This clone is a personal archive. The seven course scripts are unchanged. The
10k article dump, CTranslate2 directories, and 2023 metric printout are not
in git and will not be invented here.

What *is* new on this branch is a **methods lab** that runs on CPython
without weights: extractive baselines, a from-scratch ROUGE, a hop-error
catalog, and an HTML notebook over sixteen original fictional briefs.

## Personal methods lab (no GPU)

```bash
python3 -m silverlab list
python3 -m silverlab baselines --id lab-01
python3 -m silverlab metrics --against abstractive
python3 -m silverlab catalog
python3 -m silverlab rubric
python3 -m silverlab validate
python3 -m silverlab report --out examples/lab_report/index.html
python3 -m unittest discover -s tests -v
```

`examples/lab_report/index.html` is a self-contained report: mean ROUGE for
lead-1/2, longest, keyword, and TextRank, plus every brief and every catalog
row. Those numbers describe the fiction corpus only.

Start at [`docs/README.md`](docs/README.md). The argument is in
[`docs/course-report.md`](docs/course-report.md).

## 2023 course scripts (GPU, local dump)

Still the original hop. They need models and CSVs that this repository does
not ship.

| Step | Script | Input it expects |
| --- | --- | --- |
| 1 | `Ctranslate_converter.py` | Hub access; writes `models/opus-mt-en-da_ct2` (da→en is commented out) |
| 2 | `translate.py` | `10000_articles_without_linebreaks.csv`, `models/opus-mt-da-en_ct2` |
| 3 | `summary.py` | `translated_articles.csv` — and a `[:10]` debug slice |
| 4 | `translate_back.py` | `summarized_file_ml80_rp5.0.csv`, `models/opus-mt-en-da_ct2` |
| 5 | `finetune.py` | `datasets/{train,validation,test}_dataset.csv`, `google/mt5-large` |
| 6 | `use_model.py` | `small_model`, ScandEval Nordjylland mini |
| 7 | `eval.py` | `small_model`, Alexandra Nordjylland test |

```bash
python Ctranslate_converter.py
python translate.py
python summary.py
python translate_back.py
python finetune.py
python use_model.py
python eval.py
```

Known mismatches (converter direction, NLLB prefixes on OPUS-MT, `large_model`
vs `small_model`, Nordjylland column names) are listed in
[`docs/script-scars.md`](docs/script-scars.md) and left unpatched.

GPU-script imports are listed in `requirements.txt`. The lab does not use
that file.

## Layout

```text
silverlab/          stdlib methods lab
examples/           fiction JSON/CSV, HTML report, CLI wrapper
docs/               course-report reconstruction and method notes
tests/              unittest for the lab only
*.py                2023 course scripts (untouched)
```

## License

MIT (see `LICENSE`). The fictional briefs and the hop-error catalog are
original to this personal lab and are not TV2 Nord, not the private 10k
dump, and not employer text.
