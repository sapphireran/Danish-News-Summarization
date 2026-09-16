# Length inflation and packing windows

The 2023 scripts do not agree with each other about length.

| Script | Budget | Overflow cutter | Length idea |
| --- | --- | --- | --- |
| `translate.py` | `int(512 * 0.9)` = 460 | yes, on `,;:` | OPUS tokenizer ids, then `len(word)+1` |
| `summary.py` | 512 to pack, 80 to generate | yes | T5 tokenizer ids, same cutter |
| `translate_back.py` | 512 | **no** | OPUS tokenizer ids only |
| `finetune.py` | 1024 in, 128 out | truncation | mT5 tokenizer |

`sejeroe.packing` keeps those policies as named presets and adds two
word-budgets that make a Sejerø brief overflow on purpose:

| Preset | Budget | Notion | Typical windows on `SEJ-001` |
| --- | --- | --- | --- |
| `manchet-tight` | 16 | words | several (the lede still fits in window 0) |
| `manchet-lead` | 40 | words | one or two |
| `t5-summary-cap` | 80 | rough subwords | one |
| `forward-hop` | 460 | rough subwords | one |
| `back-hop` | 512 | rough subwords | one |

The interesting disagreement is not 460 vs 512. It is **words vs
subwords** on Danish compounds.

| Compound in the briefs | Whitespace words | Rough 4-char pieces |
| --- | --- | --- |
| `færgeafgang` | 1 | 3 |
| `novemberomsætningen` | 1 | 5 |
| `industrihorisont` | 1 | 4 |
| `SMS-varslingen` | 1 | 4 |

English "ferry departure" is already two words. Packing the Danish body
on a *word* budget therefore under-counts relative to the English hop.
Packing both on a crude subword budget moves them closer. That is why
the desk prints both ratios:

```bash
PYTHONPATH=. python3 -m sejeroe length
PYTHONPATH=. python3 examples/pack_lede.py --id SEJ-001 --policy manchet-tight
```

`summary.py` also has a silent row cap: `df[:10]`. A 10 000-row English
file becomes a 10-row summary file unless that slice is removed. The
desk does not reproduce that cap; the eight briefs are already smaller
than ten.
