# Workbook

Stdlib only. CPython 3.11+. No Hugging Face, no CTranslate2, no GPU.

```bash
python3 -m maalestok list
python3 -m maalestok show bh-02
python3 -m maalestok pack bh-02 --budget 40
python3 -m maalestok budget bh-01 --budget 80
python3 -m maalestok ledger
python3 -m maalestok ledger --article bh-06
python3 -m maalestok scar
python3 -m maalestok fixtures
python3 -m maalestok report
python3 -m maalestok validate
python3 examples/run_almanac.py
python3 -m unittest discover -s tests -v
```

`report` writes `examples/report/index.html` and a one-screen snapshot
at `docs/generated/almanac-ledger.txt`.

`fixtures` rewrites the course-shaped CSVs under `examples/data/`.
Those files are fiction with the 2023 headers (`article text` on the
raw table, `body`/`translated`/`summary` later, `input_text` /
`target_text` on the public-eval shape).
