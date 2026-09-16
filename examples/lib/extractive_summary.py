"""First-N sentence baseline used by the toy labeling pipeline.

This is *not* the 2023 neural teacher. It exists so the example tree can
emit a ``body`` / ``summary`` CSV without OPUS-MT or T5, and so you can
compare a boring-but-faithful Danish lede with the hand-written pivot
summaries in ``examples/data/labeled_danish.csv``.
"""

from __future__ import annotations

from examples.lib.text_chunking import sent_tokenize_text


def extractive_summary(
    article: str,
    max_sentences: int = 2,
    *,
    language: str = "danish",
    max_chars: int | None = 480,
) -> str:
    """Return the first ``max_sentences`` sentences, optionally clipped."""
    sentences = sent_tokenize_text(article, language=language)
    if not sentences:
        return ""
    chosen = sentences[: max(1, max_sentences)]
    text = " ".join(chosen).strip()
    if max_chars is not None and len(text) > max_chars:
        clipped = text[: max_chars - 1].rsplit(" ", 1)[0]
        return clipped.rstrip(",;:") + "…"
    return text


def lead_k_chars(article: str, max_chars: int = 240) -> str:
    """Even cruder baseline: the opening characters on a word boundary."""
    text = " ".join((article or "").split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rsplit(" ", 1)[0] + "…"
