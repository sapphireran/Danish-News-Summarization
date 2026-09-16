# Manchet and the inverted pyramid

Danish newsrooms still teach the *manchet*: the first sentence (sometimes
the first two) should carry who did what, when, and where. Why and how
can wait. The 2023 T5 hop was trained on English news, so it often keeps
a recognisable lede. The later Danish back-translation then thins that
lede. Names fall off. Times become "later". Quotes vanish.

The desk scores **the first sentence only** against four slots:

| Slot | Why it belongs in the manchet |
| --- | --- |
| WHO | Speaker or institution the brief is about |
| WHAT | The event |
| WHEN | Clock or calendar |
| WHERE | Harbour, school, church, sandbank |

A silver label can still be a *good paragraph* and a *bad manchet*.
`SEJ-001` is the worked example.

Danish body, first sentence:

> Sejerøfærgen til Havnsø bliver i eftermiddag aflyst på grund af kuling
> fra nordvest, oplyser havnefoged Karen Møller.

That sentence already has WHO, WHAT, WHEN, WHERE, and a slice of WHY.

Silver Danish summary:

> Færgen til Havnsø er aflyst i eftermiddag på grund af kuling, sagde
> havnefogeden. En senere sejlads kan køre kl. 18.30.

The first sentence still covers the four lede slots if we accept
*havnefogeden* as an alias of Karen Møller. The name itself is gone.
The quote about an extra evening sailing is gone. HOW (SMS alert, extra
sailing) lives only in the second sentence as a vague "later sailing".

Oracle Danish manchet:

> Sejerøfærgen til Havnsø er aflyst i eftermiddag på grund af kuling.
> Havnefoged Karen Møller venter næste afgang tidligst kl. 18.30 og
> varsler en ekstra aftenafgang, hvis vejret tillader det.

The oracle puts the name back and keeps the conditional extra sailing.
That is the difference the desk is for.

Run:

```bash
PYTHONPATH=. python3 examples/inspect_manchet.py --id SEJ-001
```
