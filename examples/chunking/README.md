# Chunking example

`article_chunker.py` is a readable copy of the sentence packer in
`translate.py` and `summary.py`:

1. Sentence-split (NLTK `punkt` if installed, else a small regex).
2. Break over-long sentences on `,` / `;` / `:` or a character budget.
3. Greedy-pack sentences until the tokenizer-length sum hits the limit.

```bash
python examples/chunking/demo_chunking.py
python examples/chunking/demo_chunking.py --id sample-003 --limit 40
python examples/chunking/demo_chunking.py --column body --csv examples/data/labeled_dataset.sample.csv --limit 60
python examples/chunking/demo_chunking.py --demo-long-sentence
```

The default `--limit 80` is low on purpose so `sample-010` splits into
several groups with the whitespace stand-in tokenizer. Production
limits are 460 (OPUS-MT packer) and 512 (T5).
