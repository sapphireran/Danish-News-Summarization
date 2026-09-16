# Danish sentence cuts

NLTK `sent_tokenize` with `punkt` is what the 2023 files download at
import time. Default punkt is English-trained. On Danish news it
over-splits on:

| Pattern | Example from Toftevig fixtures | What should happen |
| --- | --- | --- |
| Clock abbreviation | `kl. 19.30` | stay in one sentence |
| Ordinal date | `den 12. oktober` | the `12.` is not a sentence end |
| Latin-style abbrev. | `bl.a.`, `f.eks.`, `m.fl.`, `osv.` | stay in one sentence |
| Money | `18,4 mio. kr.` | `mio.` is not a sentence end |
| Numbered items | `nr. 14` | stay in one sentence |
| Initials | `E. Kragh sagde` | stay in one sentence |

Over-splits change packing. A false sentence boundary is a chance to
start a new window, and a chance for the character saw to fire on a
fragment that was never a grammatical sentence.

## What Pakhuset uses instead

`pakhus.sentences.split_danish` is a small scanner, not a full linguistic
pipeline:

- Multi-character abbreviations (`bl.a.`, `f.eks.`, `d.v.s.`, `t.o.m.`)
  are protected before the scan.
- A `.` after a known abbreviation token does not end a sentence.
- A `.` after digits does not end a sentence when the next word is a
  Danish month (`oktober`, `okt.`) or another digit (clocks).
- `?` and `!` end a sentence when followed by space and an uppercase
  letter or a quote.
- Closing quotes (`«` `»` `”`) may trail the terminator.

It will still fail on rare abbreviations and on period-separated
acronyms that are not in the list. The point is to show the *difference*
against a naive `regex split on (?<=[.!?])\s+`, which the workbook
compares in `examples/compare_splitters.py`.

## Quotes

Danish news often uses `»...«` or `"..."`. The 2023 files do not special-
case quotes. A period inside a quote ends the NLTK sentence. Pakhuset's
splitter keeps the quote attached to the surrounding sentence when the
terminator is followed by a lowercase continuation, but it does **not**
implement full quote-aware parsing. Planted fixture `tof-008` has a quote
with an internal period so the atlas can show both behaviours.

## Why this belongs in a packing lab

Window fill ratio is downstream of sentence segmentation. If `kl. 19.30`
becomes two sentences, hop 1 may put `kl.` at the end of pane 0 and
`19.30` at the start of pane 1. The English T5 then sees a time of day
without its article, and the silver label is allowed to drop it. Several
"the model forgot the time" errors are packing errors with a Danish
surface.
