# 5W1H slot cards

Each Sejerø brief has a gold card written *before* the hops, not inferred
from the silver CSV. Surface forms (Danish and English) are stored next
to the canonical string so a match can survive a gloss.

| Id | WHO | WHAT | WHEN | WHERE |
| --- | --- | --- | --- | --- |
| SEJ-001 | Karen Møller | færgeafgang aflyst | i eftermiddag | Havnsø |
| SEJ-002 | Ida Kruse | lukke 3.-6. klasse | næste august | Sejerø Skole |
| SEJ-003 | Niels Abildgaard | 12.000 m³ mudring | mandag morgen | Sejerby Havn |
| SEJ-004 | Trine Holm | høring om kystmøller | i aften | forsamlingshuset |
| SEJ-005 | Lene Frost | søndagslukning | 1. november | Sejerø Købmand |
| SEJ-006 | Morten Dahl | ny tankvogn | lørdag kl. 11 | Mastrup |
| SEJ-007 | Anne Lisbjerg | kirketag | fra mandag | Sejerø Kirke |
| SEJ-008 | Emil Ravn | 100 meters afstand | sidste søndag | sandbanken |

WHY and HOW are scored as well, but they are allowed to leave the
manchet. A silver label that drops HOW is typical of `summary.py`
(`max_length=80`, `repetition_penalty=5.0`). A silver label that flips
WHY is a real error even if ROUGE-1 stays high.

## Planted failures

`examples/data/07_planted_errors.csv` holds broken Danish summaries:

| Kind | What it does | Typical blind spot |
| --- | --- | --- |
| `who-swap` | Puts the event on the wrong town or office | Unigrams of the lede survive |
| `when-drop` | Strips the clock from an otherwise intact lede | ROUGE barely moves |
| `why-flip` | Turns "too few pupils" into "too many", or healthy seals into sick ones | Contrast words may remain |
| `number-swap` | 12.000 m³ becomes 1.200 m³ | Most tokens unchanged |
| `polarity-flip` | Winter cut becomes an expansion | Shared nouns inflate ROUGE |
| `quote-loss` | The T5-like hop never picked up the quote | Slot recall can stay flat |

```bash
PYTHONPATH=. python3 examples/score_slots.py --planted
```
