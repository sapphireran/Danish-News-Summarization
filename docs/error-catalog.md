# Hop-error catalog

Silver labels are not "noisy the way dropout is noisy". They are noisy the
way a chain of translators is noisy: a fact can flip and then look fluent.

The catalog in `examples/data/error_items.json` is **invented**. Each
`source_span` is a real substring of a `lab-*` brief. Each `silver_span` is a
teacher mistake I wrote on purpose. Severity is 1–5.

```bash
python3 -m silverlab catalog
```

## Codes

| Code | Meaning | Typical hop |
| --- | --- | --- |
| `HOP-TR` | Forward translation bent a fact or name | da→en |
| `HOP-SM` | English teacher invented or dropped content | T5 news |
| `HOP-BK` | Back-translation drifted | en→da |
| `ENT` | Person / place / organization swapped | any |
| `NUM` | Number, date, time, or unit changed | any |
| `TNS` | Tense or mood no longer matches | often HOP-BK |
| `OMIS` | Load-bearing fact disappeared | often HOP-SM |
| `ADD` | Fact that is not in the article appeared | often HOP-SM |
| `STYLE` | English calque or leftover source word | often HOP-BK |

Codes stack. `err-02` is `HOP-TR` + `ENT` because Saturn/Saturday is both a
translation bruise and an entity swap.

## Why these fourteen

They cover the failure modes I actually worry about:

- **Numeral folding** (`80` → `18`, `under 40` → `140`).
- **Unit promotion** (metres → kilometres) — the most dangerous `HOP-SM`.
- **Toponym rhyme** (Skørping/Skærbæk, Odense/Odessa, Tórshavn/Tromsø).
- **Dropped backup plans** (the Sunday rain date in `lab-01`).
- **English leakage** (`from a tent on the square`).
- **Institutional hallucination** (NASA walking into a moth count).

If I ever retrain, I want a human sheet that uses these codes, not a
free-text "the summary is a bit off".

## What the catalog is not

- Not a sample of the 2023 GPU output. Those hypotheses were never saved.
- Not TV2 Nord. The articles are fiction.
- Not a substitute for BERTScore. A fluent wrong number can score well.

## Severity anchors

| Sev | Anchor |
| --- | --- |
| 1 | Style only; a desk would shrug |
| 2 | Tense or small qualifier |
| 3 | Missing secondary fact or mild add |
| 4 | Wrong named entity or plausible wrong number |
| 5 | Wrong unit, inverted quantity, or injected institution |

`err-07` (two metres → two kilometres of dune travel) is a 5. The sentence
still looks like science journalism.
