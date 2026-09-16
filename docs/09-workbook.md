# Workbook

Run these against the Toftevig fixtures. Answers are not committed as
prose; the commands should print them.

## 1. Count panes

```bash
python examples/walk_windows.py --article tof-001
python examples/walk_windows.py --article tof-009
```

`tof-001` is a harbour story that should spill. `tof-009` is a short
notice that should be a single pane at hop 1. If hop 2 pane counts differ
from hop 1 on `tof-001`, that is repacking, not a bug in the printer.

## 2. Force the character saw

```bash
python examples/pack_article.py --article tof-008 --packer course_translate
python examples/pack_article.py --article tof-008 --packer consistent
```

`tof-008` is one long Danish sentence with commas. Course packing should
emit several chunks near 460 **characters**. Consistent packing should
keep more of it in one crate if the approx. token sum still fits.

## 3. Clock and money cuts

```bash
python examples/compare_splitters.py --article tof-003
```

Naive regex split will cut `kl. 19.30` and `3,2 mio. kr.`. The Danish
splitter should not. Note how pane fill changes when those become extra
"sentences".

## 4. Empty window

```bash
python examples/pack_article.py --article tof-010 --packer course_back
```

`tof-010` is a single over-budget English-like sentence packed with the
`translate_back.py` algorithm (no saw, budget 512). Expect an empty list
emitted before the singleton. `pack_consistent` should not emit empties.

## 5. Concatenation vs the 128 cap

```bash
python examples/inspect_concat.py --article tof-001
```

Check `would_truncate_at_128` and `echo_names`. Pane 0 should dominate
the prefix that training would keep.

## 6. Scar scan

```bash
python -m pakhus scars
```

Confirm the converter still exports only en-da, `summary.py` still
slices `[:10]`, and `use_model.py` still has `no_repeat_ngram_size=1`.
If this scan ever goes quiet, someone edited the frozen exam files.

## 7. Schema guard

```bash
python examples/validate_contracts.py
```

Must fail if `article text` is renamed to `article_text`. The 2023 hop 0
reader is a literal pandas column lookup.

## 8. Full atlas

```bash
python -m pakhus report
```

Open `examples/report/index.html`. Each article page should show pane
bars, leftover fill, and which figures sit in which crate.
