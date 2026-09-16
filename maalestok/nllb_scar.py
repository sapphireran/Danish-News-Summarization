"""Executable note for the NLLB language-code scar on OPUS-MT.

``translate.py`` and ``translate_back.py`` do all of the following:

1. Load Helsinki-NLP OPUS-MT (not NLLB).
2. Pass ``src_lang='dan_Latn'`` / ``'eng_Latn'`` into ``from_pretrained``.
3. Set ``target_prefixes = [[tgt_lang] ...]`` with those NLLB codes.
4. Decode ``hypotheses[0][1:]``, i.e. drop the first generated token.

OPUS-MT does not speak NLLB codes. If the converter echoes the prefix, step
4 is harmless. If it ignores the prefix, step 4 drops the first real word —
often a number or a name sitting at the start of a summary.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScarCase:
    name: str
    hypothesis: tuple[str, ...]
    decoded: tuple[str, ...]
    dropped: str
    harmless: bool
    note: str


def scar_decode(hypothesis: list[str] | tuple[str, ...], *, skip_first: bool = True) -> list[str]:
    tokens = list(hypothesis)
    if skip_first:
        return tokens[1:]
    return tokens


def demo_cases() -> tuple[ScarCase, ...]:
    echoed = ("eng_Latn", "Graesbjerg", "recorded", "47.2", "mm")
    ignored = ("Graesbjerg", "recorded", "47.2", "mm")
    number_first = ("47,2", "mm", "faldt", "i", "juni")
    return (
        ScarCase(
            name="model_echoes_prefix",
            hypothesis=echoed,
            decoded=tuple(scar_decode(echoed)),
            dropped=echoed[0],
            harmless=True,
            note="Prefix is discarded; the sentence still starts on Graesbjerg.",
        ),
        ScarCase(
            name="model_ignores_prefix",
            hypothesis=ignored,
            decoded=tuple(scar_decode(ignored)),
            dropped=ignored[0],
            harmless=False,
            note="First real word is discarded. A parish name vanishes.",
        ),
        ScarCase(
            name="number_leads_the_summary",
            hypothesis=number_first,
            decoded=tuple(scar_decode(number_first)),
            dropped=number_first[0],
            harmless=False,
            note="The June total is the first token and is the one that is dropped.",
        ),
    )
