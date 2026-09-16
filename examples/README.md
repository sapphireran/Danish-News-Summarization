# Examples

Runnable stand-ins for the December 2023 GPU pipeline. Personal / course material only.

The scripts on the repository root (`translate.py`, `summary.py`, `translate_back.py`, `finetune.py`, `eval.py`, `use_model.py`) need CTranslate2 models, a news T5, mT5, and CSVs that were never committed. This folder exists so I can still show **column shapes**, **sentence packing**, and **the three hops** on a laptop with the Python standard library.

No Hugging Face download. No CUDA. No employer data.

## What you get

| Path | What it is |
| --- | --- |
| [`data/`](data/README.md) | Ten fictional Danish news rows, plus hand-written English pivots and Danish silver summaries. |
| [`dns_examples/`](dns_examples/) | Importable helpers: sentence split, 2023-style packing, schema checks, tiny ROUGE, toy hops. |
| [`run_toy_pipeline.py`](run_toy_pipeline.py) | Walk every sample row through DA→EN → EN summarize → EN→DA and write four CSVs. |
| [`validate_schema.py`](validate_schema.py) | Check headers, unique ids, and the 6/2/2 split partition. |
| [`inspect_samples.py`](inspect_samples.py) | Token counts and compression ratios for the fixtures. |
| [`compare_hops.py`](compare_hops.py) | Silver summary vs lead-1 baseline overlap against the Danish article. |
| [`pack_report.py`](pack_report.py) | How the 2023 packer cuts each article at several budgets. |

Longer prose: [`../docs/examples-guide.md`](../docs/examples-guide.md), [`../docs/toy-pipeline.md`](../docs/toy-pipeline.md), [`../docs/chunking-algorithm.md`](../docs/chunking-algorithm.md).

## Run from the repository root

```bash
python3 examples/validate_schema.py
python3 examples/inspect_samples.py
python3 examples/pack_report.py --id oesterhavn-kvote --budget 20
python3 examples/compare_hops.py --id lund-bageri
python3 examples/run_toy_pipeline.py --output /tmp/dns-toy --budget 40
```

`examples/output/` is gitignored. Point `--output` at `/tmp` or that folder.

## Tests

```bash
python3 -m unittest discover -s tests -t . -v
```

Fifty-odd tests cover the packer, the fixtures, and a CLI smoke run. They should pass on a bare CPython 3.11+ with no `pip install`.

## What a green toy run does *not* prove

- It does not prove OPUS-MT or T5 quality. Known ids replay hand-written strings.
- It does not prove the 2023 fine-tune. There is no mT5 here.
- It does not prove Nordjylland scores. Those scripts still need `eval.py` and a downloaded dataset.

Unknown ids (a row you add yourself) are wrapped in `[da→en]` / `[en→da]` so you can see the hop without a silent identity function.

## Why the pack budget defaults to 40

`translate.py` used `int(512 * 0.9)` = 460 **Marian subword** tokens. A whitespace counter on these short fixtures almost never overflows at 460, so the demo would look like a no-op. 40 whitespace-tokens is enough to cut `oesterhavn-kvote` into several packs and still leave the short municipal stories in one group. Pass `--budget 460` if you want the original number with the wrong unit.
