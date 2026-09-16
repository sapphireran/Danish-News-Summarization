# Hop error budget

Why this project is three models in a trench coat, and what each hop is allowed to break.

This is personal method notes for the ITU 2023 final, written in 2026 while adding examples. It is not a paper.

## The question I actually asked

> If I only have unlabeled Danish news, can I borrow an English news summarizer and still fine-tune a Danish mT5?

That question has a cheap yes: translate, summarize, translate back, train. It also has a list of ways the yes is dirty. I wanted the dirty list to be *visible*, which is why the examples keep the hops as separate CSVs instead of one magic `summarize_da()`.

## Hop 1 — DA→EN (fidelity)

**Job:** put the article into the only language the news T5 understands.

**Allowed to break:** wordplay, names with Danish morphology, measurements written with a decimal comma, quoted speech.

**Not allowed to break (ideally):** who / what / where / numbers that will appear in a summary. If hop 1 drops “4,2 millioner” or turns 17–4 into a tie, hop 2 cannot recover it.

**2023 risk I can still see in code:** NLLB `eng_Latn` prefixes on Marian, and a `[1:]` strip that assumes a language token. That can eat the first real word of a pack. The toy pipeline does not reproduce that bug; it copies a hand-written English article.

## Hop 2 — EN summarize (compression)

**Job:** throw away most of the article. This is the only hop that is *supposed* to lose information.

**Allowed to break:** order of secondary facts, attribution, “the climate committee said.”

**Not allowed to break:** invent a budget number, swap the winner of a football match, or attach the ferry cut to the wrong town.

**2023 settings that push the hop:** `max_length=80` and `repetition_penalty=5.0` are aggressive. High repetition penalty was me fighting loops on short news T5; it also starves the decoder of repeated entity names. Multi-pack articles become several 80-token summaries glued together, so a long fisheries piece can read like a list of leads.

Lead-1 (the toy fallback) is a different failure mode: it is faithful to the first sentence and blind to the rest. `compare_hops.py` exists so I can see that on the fixtures — silver lines were written to mention the *news* (the vote, the close, the quota), not just the opener.

## Hop 3 — EN→DA (fluency back)

**Job:** put the compressed string into the language mT5 will be asked to generate.

**Allowed to break:** style. A TV2 Nord journalist does not write like Marian.

**Not allowed to break:** the remaining facts. If hop 2 said “week 12” and hop 3 says “uge 11”, the silver label is wrong and mT5 will learn the wrong number.

**2023 risk:** same NLLB prefix habit (`dan_Latn`) and no long-sentence breaker. Fine for 80-token English. Bad if I ever pointed this script at a full article.

## Error that compounds

```text
entity drop at hop 1  →  T5 never sees it  →  silver cannot contain it
number mutation at hop 3 →  mT5 is trained to emit the mutated number
style lock-in at hop 3   →  eval on human Nordjylland summaries looks worse than the model “is”
```

Automatic ROUGE on a *different* human distribution punishes hop-3 style even when hop 2 was reasonable. That is why I refuse to invent a score table in these docs. `eval.py` was aimed at Nordjylland gold, not at a held-out slice of the silver CSV. Those are two different exams.

## What the examples can show

On the fixtures, hop error is **zero by construction** — I wrote all four strings. The useful demonstration is structural:

- the article language never flips (hop 1 writes a new column; `body` stays Danish);
- compression is a new column at hop 2, still English;
- hop 3 overwrites only that compressed column into Danish;
- packing is visible *before* hop 1, which is where Marian would have truncated.

For actual error, I would need to run the 2023 models or label a 32-row sheet by hand. I did not do that in this pass. The honest sentence is: the method is designed to leak, and the repo still has no measured leak.
