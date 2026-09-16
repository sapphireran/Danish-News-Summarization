# Examples guide

The 2023 scripts are a lab notebook that bottoms out on missing CSVs and missing weights. This page is the map of the **replacement** I added in 2026: ten fictional stories and a standard-library pipeline that keeps the same column names.

If you only open one examples page, open [`../examples/README.md`](../examples/README.md) and run the five commands there. This file is the longer why.

## Why examples at all

I cannot commit `10000_articles_without_linebreaks.csv`. I will not commit `large_model/`. A README that only says “run `python translate.py`” is a wish. The examples exist so that:

1. The schema is *executable* (`validate_schema.py` fails if I rename `article text`).
2. The packer is *visible* (`pack_report.py` on `oesterhavn-kvote`).
3. The three hops are *ordered* (`run_toy_pipeline.py` writes four CSVs in the 2023 shapes).
4. A lead-1 baseline can sit next to a silver summary (`compare_hops.py`) without downloading `evaluate`.

That is the whole job. It is not a second implementation of Marian.

## Layout

```text
examples/
  data/                 fictional fixtures + 6/2/2 splits
  dns_examples/         importable helpers (no torch)
  *.py                  CLIs
tests/                  unittest, stdlib only
```

Helpers are split on purpose:

| Module | Responsibility |
| --- | --- |
| `sentences.py` | Period-space-capital splitter + word tokens. |
| `chunking.py` | 2023 `split_long_sentence` + greedy pack. |
| `schema.py` | Header contracts and split partition. |
| `metrics.py` | Tiny ROUGE-N / ROUGE-L / compression. |
| `mock_models.py` | Fixture lookup and `[da→en]` fallback. |
| `pipeline.py` | Glue for the toy CLI. |
| `io.py` | UTF-8 `csv` read/write. |

The 2023 root scripts are **not** imported. They pull `ctranslate2` at module level. Importing `translate.py` would download `punkt` and look for a model directory.

## Fixture design

Towns are fake: Klintelund, Vesterø, Strandholt, Mosevang, Sandvig, Østerhavn, Grønmark, Havneby. I kept the *register* of a small-town Danish news brief (council votes, ferry timetables, a bakery closing) because that is what the original dump looked like, without copying a line of it.

Nine stories have matching Danish/English sentence counts so a future alignment demo can zip hop 1. `oesterhavn-kvote` is one long comma-heavy sentence so the character-based long-sentence breaker has work to do.

Hand-written summaries are one sentence, closer to the T5 `max_length=80` habit than to a multi-paragraph abstract.

## Counters versus Marian

`WhitespaceCounter` counts `len(text.split()) + 2`. Marian counts subwords. The toy budget is therefore a **different unit** than `text_max_length = 460` in `translate.py`. I kept the packer *control flow* and changed the ruler so the demo is readable. [chunking-algorithm.md](chunking-algorithm.md) spells out the 2023 character/token mix-up that this also preserves.

## Adding an eleventh story

1. Append a row to `examples/data/sample_articles.csv` (`id`, `article text`).
2. Re-run `python3 examples/run_toy_pipeline.py`. The new id will appear with `[da→en]` markers.
3. If you want it to look like the others, add matching rows to the three other fixture CSVs and assign the id to exactly one split file.
4. Run `python3 examples/validate_schema.py` and `python3 -m unittest discover -s tests -t .`.

Do not paste real articles. The fixtures stay fictional so the repo remains a personal course archive, not a news scrape.

## Dependencies

CPython 3.11+ is enough. I did not add an `examples/requirements.txt` because there is nothing to pin. The root [`requirements.txt`](../requirements.txt) is only for people who intend to re-run the 2023 GPU scripts.
