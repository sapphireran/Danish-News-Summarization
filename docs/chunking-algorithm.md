# Chunking algorithm

How `translate.py` and `summary.py` cut a long news article before a 512-token seq2seq model sees it. Copied from the December 2023 helpers, then reimplemented without `nltk` / `transformers` in [`examples/dns_examples/chunking.py`](../examples/dns_examples/chunking.py).

`translate_back.py` uses a thinner variant: sentence split + pack, **no** long-sentence comma breaker. Summaries are short, so that was usually fine.

## Why pack at all

Marian OPUS-MT and the news T5 both sit on a 512-token context. A municipal or fisheries piece in the 10k dump can run well past that. Silent truncation on the encoder is worse than an extra batch call: you lose the tail of the article and never see a warning. The packer is the only piece of 2023 engineering I would keep in a rewrite.

## Three steps

```text
article
  │
  ├─ 1. sentence split
  │
  ├─ 2. if a sentence is longer than the budget:
  │        walk words; soft-break on , ; : ;
  │        else hard-break by popping the last word
  │
  └─ 3. greedy pack: add a piece to the current group
         until the next piece would overflow, then flush
```

`summary.py` then joins each group with a space and summarizes the groups independently. The English summaries are concatenated. That is why a long article can produce a silver label that is really *several* 80-token T5 outputs glued together.

## Two rulers, one budget

This is the footgun I want documented in one place.

`text_max_length = int(512 * 0.9)` is a **token** budget (460).

`split_long_sentence` does not call the tokenizer. It does:

```text
current_length += len(word) + 1    # characters + a stand-in space
```

and compares that running sum to `text_max_length`.

So a Danish sentence that is 200 Marian tokens but 500 characters will be comma-broken “because it is too long,” while a sentence that is 450 tokens and 400 characters will not. The packer in step 3 *does* use tokenizer lengths. The two loops do not share a unit.

I left that behaviour in the toy helper on purpose. A cleanup would pass `len(tokenizer.encode(chunk))` into the long-sentence walker. I am not changing `translate.py` in this pass.

## Soft break versus hard break

Words come from a Punkt-like tokenizer that peels punctuation (`"havnen,"` → `havnen` `,`).

- If the current word is `,` / `;` / `:` **and** `current_length < max_length`, flush. That is a soft break: we had room and we took a grammatical seam.
- If `current_length >= max_length`, pop the word that overflowed, flush the rest, and start a new chunk with the overflow word. That is a hard break.

A single word longer than the budget still becomes its own chunk. The 2023 code can therefore emit a group that is still over budget. The model will truncate that one.

## Greedy pack

After pieces exist, the second loop is ordinary first-fit:

```text
if current_length + next_length > budget:
    flush
    start a new group with `next`
else:
    append
```

An already-oversized piece is not split again. It becomes a solo group.

## Worked example: `oesterhavn-kvote`

The fixture is one sentence (a list of cutters, plants, and demands). On a whitespace counter with budget 20 it is too long, so step 2 walks commas:

```bash
python3 examples/pack_report.py --id oesterhavn-kvote --budget 20
```

You should see several groups, each starting after a comma flush or a hard break. On `--budget 400` the same article stays one group, because the whitespace count of the whole sentence fits.

Compare `--no-split-oversized` (the `translate_back.py` path): one group, one piece, even at budget 20. That flag is how I remind myself the back-translation helper was not the same function.

## What the toy counter is not

`WhitespaceCounter` is `len(text.split()) + 2`. It is a ruler for the demo. It is not `Helsinki-NLP/opus-mt-da-en`. Do not use these pack counts to size a GPU job.

## Copy-paste debt

`translate.py` and `summary.py` each contain their own `split_long_sentence` / `split_into_sentences`. They drifted only in names. `translate_back.py` is the odd one out. A rewrite should have *one* function and a tokenizer callback. The examples package is that function, living next to the repo instead of inside the 2023 files, so the lab notebook on `main` stays historically intact.
