# Two length notions in the 2023 packer

`split_long_sentence` in `translate.py` and `summary.py` is
character-budgeted:

```text
current_length += len(word) + 1
if word in [',', ';', ':'] and current_length < max_length:
    flush
elif current_length >= max_length:
    pop last word, flush, start again
```

`split_into_sentences` is subword-budgeted. It asks
`len(tokenizer.encode(sentence))` and packs until
`current_length + length > text_max_length`.

For OPUS-MT, `text_max_length = int(512 * 0.9)` = 460. For the English
T5, `text_max_length = 512`.

## Why the mix matters for measures

A Danish clause with `3.200 kr., 2,4 ha og 6,8 t/ha` has three commas.
The character helper will flush on each comma long before 460 characters.
Each flush becomes its own translation call. The amount, the area, and
the yield can be translated in isolation and then concatenated with
spaces. That is how a later summary sees three fragment sentences
instead of one harvest sentence.

The subword helper, on the same text, may still have room. So a
sentence that *looks* short in tokens is split anyway if you walk the
historical path, and a sentence that looks long in tokens is split
differently if you only walk the character path.

`maalestok pack bh-02 --budget 40` and `maalestok budget bh-02 --budget 40`
print both numbers on the same windows. The token count is an
approximation (`approx_subword_len`); it is not Helsinki-NLP.

## Comma peel

NLTK `word_tokenize` turns `Aalborg,` into `Aalborg` + `,`. The flush
test looks at the lone comma. `maalestok.tokenize.word_tokenize` peels
the same marks so a laptop run matches the 2023 scar without downloading
NLTK.

## Near-limit vs historical

`pack_article(..., historical_long_split=True)` is the default and the
one the fixtures document. Turning it off is useful only as a contrast:
you will see fewer windows and fewer comma-final fragments.
