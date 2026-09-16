"""Length functions used by the packing house.

The 2023 files mix two notions of length:

- `split_long_sentence` accumulates `len(word) + 1` (characters + a space)
  after an NLTK-style word tokenize.
- Window packing uses `len(tokenizer.encode(text, add_special_tokens=True))`.

This module keeps both, plus a deterministic stand-in for encoder ids so
the lab can run without SentencePiece or Hugging Face.
"""

from __future__ import annotations

import re
from typing import Iterable

# Mirrors how transformers tokenizers usually add bos/eos-style specials
# when `add_special_tokens=True`. Marian/T5 differ in the exact count;
# one extra id is enough to make short sentences more expensive per hop,
# which is the packing behaviour we need to show.
SPECIAL_TOKEN_OVERHEAD = 1

# Long Danish compounds are one orthographic word and several subwords.
# The stand-in peels them into chunks of this many characters.
SUBWORD_CHARS = 6

_TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def word_tokenize(text: str) -> list[str]:
    """NLTK-like tokenize: words (unicode) and each punctuation mark."""
    if not text:
        return []
    return _TOKEN_RE.findall(text)


def detokenize_course(tokens: Iterable[str]) -> str:
    """Join the way `translate.py` does: spaces between every token.

    Punctuation therefore appears with a leading space (`havnen , kajen`).
    That spacing is a silver-label scar, not a bug in this helper.
    """
    return " ".join(tok for tok in tokens if tok != "")


def detokenize_tight(tokens: Iterable[str]) -> str:
    """Join words with spaces; glue punctuation to the left token."""
    pieces: list[str] = []
    for tok in tokens:
        if not tok:
            continue
        if pieces and re.fullmatch(r"[^\w\s]+", tok, flags=re.UNICODE):
            pieces[-1] = pieces[-1] + tok
        elif pieces:
            pieces.append(" " + tok)
        else:
            pieces.append(tok)
    return "".join(pieces)


def char_word_len(tokens: Iterable[str]) -> int:
    """Sum of `len(word) + 1` as in `split_long_sentence`."""
    return sum(len(tok) + 1 for tok in tokens)


def running_char_len(tokens: list[str]) -> list[int]:
    """Inclusive running character budget after each token."""
    out: list[int] = []
    acc = 0
    for tok in tokens:
        acc += len(tok) + 1
        out.append(acc)
    return out


def _subword_pieces(word: str) -> int:
    if re.fullmatch(r"\d+[.,]?\d*", word):
        return 1
    if len(word) <= SUBWORD_CHARS:
        return 1
    # ceil(len / SUBWORD_CHARS)
    return (len(word) + SUBWORD_CHARS - 1) // SUBWORD_CHARS


def approx_encode_ids(text: str, add_special_tokens: bool = True) -> list[str]:
    """Deterministic pseudo-subword ids. Not SentencePiece.

    Punctuation is one id. Short words are one id. Longer tokens (Danish
    compounds, hyphenated names) are split every `SUBWORD_CHARS`
    characters so a packing budget in "ids" is stricter than a word count
    and looser than a character count — the same direction as Marian/T5.
    """
    ids: list[str] = []
    if add_special_tokens:
        ids.append("<s>")
    for tok in word_tokenize(text):
        if re.fullmatch(r"[^\w\s]+", tok, flags=re.UNICODE):
            ids.append(tok)
            continue
        if len(tok) <= SUBWORD_CHARS:
            ids.append(tok.lower())
            continue
        for i in range(0, len(tok), SUBWORD_CHARS):
            ids.append(tok[i : i + SUBWORD_CHARS].lower())
    if add_special_tokens:
        ids.append("</s>")
    return ids


def approx_encode_len(text: str, add_special_tokens: bool = True) -> int:
    return len(approx_encode_ids(text, add_special_tokens=add_special_tokens))


def whitespace_word_count(text: str) -> int:
    return len(text.split())
