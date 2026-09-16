# NLLB language codes on an OPUS-MT decoder

`Ctranslate_converter.py` as committed converts **only**
`Helsinki-NLP/opus-mt-en-da`. The da→en convert call is commented out.
`translate.py` still points at `models/opus-mt-da-en_ct2`.

Both translate scripts then do something that belongs to NLLB, not OPUS:

```python
tokenizer = AutoTokenizer.from_pretrained(
    "Helsinki-NLP/opus-mt-da-en",
    use_auth_token=False,
    src_lang="dan_Latn",
)
target_prefixes = [[tgt_lang] for _ in source_tokens]  # eng_Latn / dan_Latn
results = translator.translate_batch(source_tokens, target_prefix=target_prefixes)
translations = [
    tokenizer.decode(tokenizer.convert_tokens_to_ids(result.hypotheses[0][1:]))
    for result in results
]
```

## Two decoder behaviours

`python3 -m maalestok scar` walks three toy hypotheses.

1. **The model echoes the prefix.** Hypothesis starts with `eng_Latn`.
   Dropping token 0 is correct. The parish name survives.
2. **The model ignores the prefix.** Hypothesis starts with
   `Graesbjerg`. Dropping token 0 deletes the name.
3. **A number leads the sentence.** Hypothesis starts with `47,2`.
   Dropping token 0 deletes the June total. This is the measure case.

The 2023 scripts cannot tell which behaviour they got. CTranslate2 will
not write a postcard. The lab keeps the scar executable so a later
checkout does not have to rediscover it in `translate.py:36`.

## Why measures sit on the scar

English news summaries often start with the number (`47 mm of rain…`,
`24 ha of barley…`). Danish silver lines do the same
(`47 mm regn i juni…`). If the back-translation ignores `dan_Latn` and
the decode still skips index 0, the first casualty is the amount.
