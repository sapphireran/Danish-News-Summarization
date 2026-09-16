# Why examples exist

Sapphire, September 2026. Looking back at a public student repo from a December 2023 ITU final.

I opened this tree again and could not run a single root script. That is not a moral failure — course code is allowed to be a notebook — but it made the README a museum caption. “Run `python translate.py`” is not an instruction when the CSV and the CTranslate2 directory are gone.

I wanted two things from a documentation pass:

1. Write down what the 2023 files actually do, including the ugly parts (NLLB prefixes on Marian, `[:10]`, `small_model` vs `large_model`).
2. Leave something a future clone can *execute* without 12 GB of weights.

(2) is the examples folder. The ten stories are invented towns on a made-up fjord. They are not a sneaky republish of Nordjylland. They exist so `article text` stays a real column name with a test on it, and so the packer has one maliciously long sentence to chew.

I am deliberately not “fixing” `translate.py` in this pass. Fixing it would be a different promise: a reproduction. I do not have the 10k dump or the 2023 GPU notes, and I will not pretend a clean-up commit is a rerun. Documentation plus fixtures is the honest increment.

If I ever do rerun training, I want the examples to stay. They are the regression tests for the schema. The day I rename `article text` to `article_text` without updating `translate.py`, `validate_schema.py` will not save me — but the day I rename the *fixture* and forget the space, it will.
