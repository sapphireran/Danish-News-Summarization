# Toftevig examples

CPU-only walkthroughs of the packing house. They import `pakhus` and do
not download OPUS-MT, T5, or mT5. Fixture copy is fictional.

| Script | What it prints |
| --- | --- |
| `walk_windows.py --article tof-001` | Hop-1 and hop-2 pane bars |
| `pack_article.py --article tof-008 --packer course_translate` | One named packer |
| `compare_splitters.py --article tof-003` | Naive vs Danish sentence cuts |
| `inspect_concat.py --article tof-001` | 128-token cap, echoes, figure survival |
| `validate_contracts.py` | CSV column contracts, including `article text` |
| `scan_scars.py` | Frozen 2023 script inventory |
| `write_lab_csvs.py` | Regenerates `examples/data/*.csv` |
| `render_atlas.py` | Writes `examples/report/index.html` |

```bash
python examples/walk_windows.py --article tof-001
python examples/pack_article.py --article tof-008 --packer course_translate
python examples/pack_article.py --article tof-008 --packer consistent
python examples/pack_article.py --article tof-010 --packer course_back
python examples/compare_splitters.py --article tof-003
python examples/inspect_concat.py --article tof-001
python examples/validate_contracts.py
python examples/scan_scars.py
python examples/render_atlas.py
```

Same commands as `python -m pakhus ...`. See [docs/09-workbook.md](../docs/09-workbook.md).
