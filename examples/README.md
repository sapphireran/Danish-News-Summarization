# Fjordpressen examples

These scripts talk to the closed-world Vesterklit gazette. They do not
download OPUS-MT, mT5, or the Nordjylland Hugging Face sets.

```bash
python -m fjordpress corpus
python -m fjordpress pack --budget 40 -v
python -m fjordpress hops
python -m fjordpress ledger --article vk-001
python -m fjordpress lexicon
python -m fjordpress schemas
python -m fjordpress fixtures
python -m fjordpress report --snapshot --stdout
```

Thin wrappers live next to this file if you prefer a path you can open
in an editor:

| script | what it prints |
| --- | --- |
| `pack_vesterklit.py` | 2023-style windows on each Danish source |
| `run_hops.py` | oracle vs gloss four-hop replay |
| `score_ledger.py` | entity retention and lexical ROUGE |
| `render_report.py` | writes the HTML lab notes |
| `dump_lexicon.py` | DA→EN coverage + a sample of the word list |
| `compare_length_notions.py` | char+1 vs word vs ×1.3 subword guess |
| `validate_fixtures.py` | regenerate CSVs and check 2023 column names |

Sample tables in `data/` use the same column names as the 2023 scripts.
`00_raw_articles.csv` still has the awkward `article text` header because
`translate.py` reads that name.
