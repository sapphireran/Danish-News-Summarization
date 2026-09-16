# Silver-label walkthrough (synthetic)

This walk-through follows **SYN-001** (short, one pack) and **SYN-004** (long, several packs under the demo budget) through the factory. Texts are the committed sample CSVs. No GPU is required; you are reading the files, not generating them.

Related code: [docs/01-pipeline.md](../docs/01-pipeline.md), [docs/04-dataset-schema.md](../docs/04-dataset-schema.md).

## SYN-001 — one window, clean entities

### Raw body

From `data/sample_articles.csv`:

> Havneby åbner en ny cykelsti mellem stationen og havnen på lørdag. Kommunen har brugt to år på at forhandle med lodsejere langs ruten. Borgmesteren kalder stien et løft for både pendlere og weekendgæster.

Three sentences, well under 512 tokens. `run_chunking_demo.py --id SYN-001 --budget 16` still splits them because the *demo* budget is tiny. In the 2023 factory they would be a single CTranslate2 batch.

### After da→en

From `data/sample_translated.csv`:

> Havneby is opening a new cycle path between the station and the harbour on Saturday. The municipality has spent two years negotiating with landowners along the route. The mayor calls the path a boost for both commuters and weekend visitors.

Things a real OPUS-MT hop might get wrong, and that this hand text deliberately keeps right:

- **Havneby** stays a proper name (not "Harbour town").
- **lørdag** → Saturday, not an off-by-one weekday.
- **lodsejere** → landowners, not "lodgers."

If you revive CTranslate2, compare those three items first.

### After English T5 (hand-shaped lead)

From `data/sample_summaries_en.csv`:

> Havneby opens a new cycle path from the station to the harbour on Saturday after two years of talks with landowners.

The mayor quote and the commuter/weekend distinction are gone. That is typical T5-news behaviour: keep the event, drop colour. Silver labels will therefore teach mT5 to prefer events over quotes.

### After en→da

From `data/sample_labeled_da.csv`:

> Havneby åbner lørdag en ny cykelsti fra stationen til havnen efter to års forhandlinger med lodsejere.

Danish is idiomatic enough to train on, but notice the mild translationese:

- English "opens" became **åbner lørdag** (adverb placement is fine).
- "talks" became **forhandlinger**, which matches the source article better than "snakke."
- The mayor is still missing — the factory cannot recover a fact the English summarizer dropped.

**Training pair** for `finetune.py`: Danish `body` (original, not the back-translation of the English article) + Danish `summary` above. The model must learn to go **straight** from the three Danish sentences to the short lead.

## SYN-004 — collage risk on a long council story

### Raw body (compressed recap)

Klitsogn council passes a budget that moves **18 million kroner** to elder care and schools, delays the **Sønderby** bypass for two years, adds reading coaches, caps marina fees (Kystlisten), and is opposed by people who wanted the road. Mayor **Ingrid Holm** calls it a compromise. Effective **1 January**.

That is ten sentences in the CSV. `python examples/compare_budgets.py --id SYN-004` shows three regimes:

| budget | what you see |
| --- | --- |
| 16 | The first long sentence is *character-split* into fragments (`Byrådet i`, `Klitsogn`, …) because `split_long_sentence` compares a character running sum to the token cap. This is the 2023 unit mismatch, magnified. |
| 40 | Pieces stay mostly sentence-sized; a few sentences share a pack. |
| 460 | The whole article is one pack — what OPUS-MT would actually do for this short text. |

The collage risk is about the 40-token *idea* applied to a 3,000-token feature, not about shredding SYN-004 at budget 16.

### Hand-shaped English summary

> Klitsogn's council passed a budget deal shifting 18 million kroner to elder care and schools, delaying the Sønderby bypass for two years. Mayor Ingrid Holm called it a compromise; the opposition voted no.

Kept: 18 million, elder care, schools, Sønderby delay, mayor, opposition.
Dropped: night meetings, party names except as "opposition," marina fee cap, January review, protesters' signs, reading coaches.

A pack-wise T5 run on the real factory might have **added** a second sentence about marina fees if that pack was summarized separately. The stitched silver label would then look like two leads glued together. mT5 would copy that habit.

### Hand-shaped Danish silver summary

> Klitsogns byråd vedtog et budgetforlig, der flytter 18 millioner kroner til ældrepleje og skoler og udskyder omfartsvejen ved Sønderby i to år. Borgmester Ingrid Holm kaldte det et kompromis; oppositionen stemte nej.

Entity checklist you should reuse on real outputs:

| Fact | Must survive |
| --- | --- |
| Klitsogn | yes (not "the municipality" only) |
| 18 millioner | yes (not 80, not 18 billion) |
| ældrepleje + skoler | yes |
| Sønderby / omfartsvej / to år | yes |
| Ingrid Holm | yes |
| marina fee cap | optional; dropped here on purpose |

If a real back-translation turned "18 million" into "18 billion", drop the row before fine-tune. The 2023 scripts never did that filter.

## How the split uses these rows

| id | split | reason |
| --- | --- | --- |
| SYN-001, 002, 003, 004, 006 | train | Mix of short / long / sports / weather / culture |
| SYN-005, 007 | validation | Institutions (library, school), numbers and abbreviations |
| SYN-008 | internal test | Ferry timetable — lots of clock times to overfit |

This internal test is **not** Nordjylland News. Quoting scores on SYN-008 as if they were official eval is the leakage pattern described in `docs/06-limitations-and-ethics.md`.

## Exercises (no GPU)

1. Run `python examples/compare_budgets.py --id SYN-004` and contrast budget 16 (character shredding) with 40 (sentence packs) and 460 (one window). Then mark which facts would land in separate English leads if a *long* feature were packed at ~512 tokens.
2. Run `python examples/metrics_toy_eval.py` and find `fact_swap_budget`. Change 18 to 81 in a copy of SYN-004's silver summary (do not commit it) and compute token F1 against the committed summary — it will stay high.
3. Run `python examples/inspect_sample_dataset.py` after renaming column `body` to `article text` in `sample_labeled_da.csv` (again, do not commit). The inspector should refuse the file.

## What a GPU walk-through would add

If you have converted OPUS-MT models, take **only** SYN-001's body, run the three factory scripts on a one-row CSV, and diff against the hand-written hops. Do not expect a string match. Expect the entity checklist to hold. If it does not, stop before spending compute on 10,000 rows.
