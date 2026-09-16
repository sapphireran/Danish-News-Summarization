# Examples

These examples do **not** download OPUS-MT, T5, or mT5. They walk a
handwritten fictional magazine corpus through the same *shapes* the 2023
scripts used: Danish source → English pivot → English summary → Danish
silver label.

The original GPU scripts in the repository root are unchanged.

## Why this corpus exists

A clean clone cannot run `translate.py`. The 10k-article dump, the
CTranslate2 directories, and `datasets/*.csv` were never committed. Other
personal branches already reconstruct those CSV contracts and mock the
hops. This folder is a different experiment: **what happens to names,
numbers, and Danish compounds at each hop**, measured on original fiction
about the invented island chain *Hjelmøerne*.

The articles are not municipal-meeting minutes and they are not
Nordjylland-News copy.

## Commands

From the repository root (CPython 3.11+, standard library only):

```bash
python3 -m kystlinje list
python3 -m kystlinje show kz-07
python3 -m kystlinje ledger
python3 -m kystlinje ledger --id kz-05
python3 -m kystlinje align kz-08
python3 -m kystlinje pack kz-03 --budget 80
python3 -m kystlinje quiz --answers
python3 -m kystlinje validate
python3 -m kystlinje write-tables
python3 -m kystlinje report
python3 examples/inspect_brief.py kz-17
python3 examples/run_workbook.py
```

`write-tables` refreshes the CSVs under `examples/data/` so they keep the
2023 headers (`article text`, `body`, `translated`, `summary`).
`report` rebuilds `examples/report/index.html`.

## Planted scars worth opening first

| id | What was planted |
| --- | --- |
| `kz-05` | `11` living hives become `12` in the silver label |
| `kz-07` | `Lærke Holm` is flattened to `Larke Holm` and never restored; `22` hours become `20` |
| `kz-08` | lock year `1904` becomes `1914` |
| `kz-17` | night ferry `23:40` becomes `23:30` |
| `kz-02` | `86` trees become “nearly a hundred” |
| `kz-18` | `7` performances become `otte` |

These are teaching scars, not model output.

## Tests

```bash
python3 -m unittest discover -s tests -t . -v
```
