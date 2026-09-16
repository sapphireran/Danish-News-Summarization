# One-article walkthrough (conceptual)

No real article from the 10k dump is in git, so this is a **made-up** TV2-Nord-shaped example. I am tracing the *machinery*, not scoring a real story. Names and facts below are fictional.

## Source (`x_da`)

> En 47-årig mand fra Hjørring blev onsdag eftermiddag anholdt, efter at politiet blev tilkaldt til et hus på Søndergade. Ifølge Nordjyllands Politi drejer sagen sig om grov vold. Ingen andre er kommet til skade. Manden fremstilles i grundlovsforhør torsdag.

Gold-style blurb I would expect from TV2 Nord (also invented):

> 47-årig anholdt for grov vold i Hjørring.

That is short, entity-heavy, and extractive in spirit. It is **not** what the silver pipeline is trying to emit.

## Hop 1 — `translate.py`

Sentence tokenize: one or two Danish sentences, well under 460 tokens. No packer drama.

OPUS-MT da-en, if well behaved, might produce something like:

> A 47-year-old man from Hjørring was arrested Wednesday afternoon after police were called to a house on Søndergade. According to the North Jutland Police, the case concerns aggravated assault. No one else was injured. The man will appear in a preliminary hearing on Thursday.

Failure modes I would look at on a *real* row:

- `Hjørring` → `Hjorring` / a different town
- `grundlovsforhør` → a mushy “court hearing” or a wrong legal term
- `Nordjyllands Politi` → “the police” with the region dropped

If the NLLB prefix `eng_Latn` is forced on Marian, the first English word can be missing (`A` dropped) or a junk token can appear. That is S1 in the defect list.

## Hop 2 — `summary.py`

The English fit in 512 tokens, so there is **one** T5 call, not map-reduce.

With `max_length=80` and `repetition_penalty=5.0`, a news T5 often returns a single lead:

> A 47-year-old man was arrested in Hjørring on Wednesday after police were called to a house in connection with aggravated assault.

Typical T5 edits: drop `Søndergade`, drop Thursday’s hearing, maybe invent “in connection with” hedging. `repetition_penalty=5.0` is unlikely to matter on a text this short; it mattered on longer translated municipal reports that looped “the council the council.”

If this article had been 3,000 tokens, I would have three such leads concatenated. Training would then cut at 128 SentencePiece tokens — often the first lead plus a stump.

## Hop 3 — `translate_back.py`

Marian en-da on the English lead:

> En 47-årig mand blev onsdag anholdt i Hjørring, efter at politiet blev tilkaldt til et hus i forbindelse med grov vold.

That is the **silver label** `s_da`. Compare to the invented gold:

| | Text |
| --- | --- |
| Gold | 47-årig anholdt for grov vold i Hjørring. |
| Silver | En 47-årig mand blev onsdag anholdt i Hjørring, efter at politiet blev tilkaldt til et hus i forbindelse med grov vold. |

Same incident, different genre. Silver is a sentence; gold is a headline-blurb. ROUGE-1 will share `47-årig`, `anholdt`, `grov`, `vold`, `Hjørring` and still look only “okay” because of the extra function words. BERTScore will look happier. A human ENT score should be 5 if the hops did not move the town.

This is the good case. The bad case is the same fluency with `Aalborg` instead of `Hjørring`.

## What `finetune.py` sees

Encoder: the original Danish paragraph.  
Labels: the silver sentence, truncated at 128 tokens (irrelevant here).

mT5 is asked to map a Danish story to *silver genre*, not to gold genre. After 20 epochs it may learn “write a full sentence with ‘efter at politiet blev tilkaldt’” because that template is frequent in English-news-T5 back-translations.

## What `eval.py` would compare

Prediction (student, hoped): something silver-shaped.  
Reference: Nordjylland gold, headline-shaped.

If the student is a good student, it is punished for being the thing I trained it to be. That is not a paradox; it is the project. The evaluation note’s job is to say that out loud.

## What `use_model.py` might print (and get wrong)

For row 0, batch 0, `batch_size=2`, the article on screen matches the generation. For row-as-printed `i=1` (second batch), the article is dataset row 1 and the generation is dataset rows 2–3. I would not debug ENT errors from that printer.

## Why I wrote a fictional walkthrough

Because the real CSV is absent, a fictional row is the only way to show the *style gap* without pretending I still have 2023 outputs. If I recover a real triple, it goes in `notes/runs/`, not here, and this file stays the cartoon.
