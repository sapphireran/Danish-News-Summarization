# Toy pipeline

What `examples/run_toy_pipeline.py` does, hop by hop, and how that maps onto the 2023 models I am *not* downloading here.

## Command

```bash
python3 examples/run_toy_pipeline.py --output /tmp/dns-toy --budget 40
```

Exit 0 writes four CSVs and a pack preview on stdout.

| Output file | 2023 twin | Columns |
| --- | --- | --- |
| `toy_articles.csv` | `10000_articles_without_linebreaks.csv` | `id`, `article text` |
| `toy_translated.csv` | `translated_articles.csv` | `id`, `body`, `translated` |
| `toy_summaries_en.csv` | `summarized_file_ml80_rp5.0.csv` | `id`, `body`, `translated`, `summary` |
| `toy_labeled.csv` | `labeled_dataset_ml80_rp5.0.csv` | `id`, `body`, `summary` |

## Hop 1 — Danish article → English article

**2023:** CTranslate2 `opus-mt-da-en`, packed at 460 Marian tokens, NLLB prefixes left in by mistake.

**Toy:** if `id` is in `sample_translated.csv`, copy that English string. Otherwise wrap the Danish body in `[da→en] …`.

Packing still runs on the Danish side so the stdout report is real. The English string is *not* produced by concatenating per-pack translations. Doing that with a lookup table would require sentence-level alignments for every cut; I only guaranteed sentence-count alignment on the nine short stories, not pack-level alignment.

## Hop 2 — English article → English summary

**2023:** `mrm8488/t5-base-finetuned-summarize-news`, 80 tokens, repetition penalty 5.0, one generate per packed span, then join.

**Toy:** if `id` is in `sample_summaries_en.csv`, copy that summary. Otherwise take the first English sentence (`lead-1`).

A lead-1 fallback is closer to extractive news than to T5, which is the point: an unknown row should look obviously cheaper than the fixtures.

## Hop 3 — English summary → Danish summary

**2023:** CTranslate2 `opus-mt-en-da` on the summary only. Article body is passed through.

**Toy:** if `id` is in `sample_labeled.csv`, copy that Danish silver line. Otherwise wrap the English summary in `[en→da] …`.

The Danish `body` on the labeled CSV is always the original article, never the English pivot. That is the contract `finetune.py` depends on.

## Unknown-row walkthrough

Add a one-line article and run the CLI. You should see:

```text
[da→en] <your Danish>
EN summary: <first English sentence of the marked text, or the marked text>
DA silver:  [en→da] <that summary>
```

If hop 1 is marked, hop 2 is summarizing marked text. That is ugly and correct: the examples refuse to invent fluent Danish for a story I did not write.

## Pack budget

Default `--budget 40` is whitespace-tokens plus two specials. See [chunking-algorithm.md](chunking-algorithm.md) for why that is not 460. `--no-split-oversized` switches the packer to the `translate_back.py` behaviour.

## What I would do next (and did not)

- Wire pack-level translation for the nine aligned stories (zip sentences, translate each pack independently, join) so hop 1 is not a whole-article lookup.
- Add a tiny character-level “scrambler” so unknown rows still change surface form.
- Keep mT5 out of this folder.

The first of those is tempting and would make the demo lie less about pack boundaries. I stopped at whole-article lookup because the fixtures are the teaching object, not a fake decoder.
