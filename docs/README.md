# Blåhøj notes

These pages are personal reconstruction notes for the 2023 ITU Danish
summarization scripts. They are written around **measures** — the numbers,
units, clocks, and Danish date words that the silver-label hops chew up —
not around another copy of the six-step README.

| Page | What it is for |
| --- | --- |
| [why-measures.md](why-measures.md) | Why a number dies even when the story survives |
| [danish-numbers.md](danish-numbers.md) | Comma, thousand-dot, `kr.`, `kl.`, `mio.` |
| [packing-budgets.md](packing-budgets.md) | Character `+ 1` vs subword windows |
| [nllb-prefixes.md](nllb-prefixes.md) | NLLB codes on OPUS-MT, then `hypotheses[0][1:]` |
| [script-scars.md](script-scars.md) | What the December 2023 files still do |
| [mt5-length.md](mt5-length.md) | 1024 / 128 / `min_length=9` against Danish |
| [almanac.md](almanac.md) | The fictional parish and the 10/3/3 split |
| [workbook.md](workbook.md) | Commands for the `maalestok` lab |

The HTML telescope lives at `examples/report/index.html` after
`python3 -m maalestok report`.
