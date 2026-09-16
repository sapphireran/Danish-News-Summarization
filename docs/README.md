# Personal methods lab

This folder is the write-up that belongs with `silverlab/`. It does **not**
re-tell the seven 2023 scripts beat by beat — those files are still on `main`
and still do what they did in December. What was missing is a way to think
about the project without a GPU or the private article dump.

| Note | Question it answers |
| --- | --- |
| [course-report.md](course-report.md) | What I would still defend as the method |
| [related-work.md](related-work.md) | Where the hop sits in the 2020–2023 literature |
| [extractive-baselines.md](extractive-baselines.md) | What to run before converting OPUS-MT |
| [metrics-from-scratch.md](metrics-from-scratch.md) | How this repo's ROUGE is computed |
| [error-catalog.md](error-catalog.md) | A typology for da→en→sum→da bruises |
| [annotation-rubric.md](annotation-rubric.md) | Five 1–5 axes I wish I had used |
| [nordjylland.md](nordjylland.md) | Public eval set vs the private 10k dump |
| [danish-language.md](danish-language.md) | Why a news T5 in English is a loaded teacher |
| [ablation-protocol.md](ablation-protocol.md) | What I would ablate if I retrained |
| [bibliography.md](bibliography.md) | Papers and datasets named in the notes |
| [script-scars.md](script-scars.md) | Defects left in the 2023 scripts on purpose |

Runnable surface: `python3 -m silverlab --help`. Narrative for the CLIs is in
[`examples/README.md`](../examples/README.md).
