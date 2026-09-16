"""Extractive pane briefs and concatenation scores.

The 2023 T5 hop emitted up to 80 tokens per English pane and joined them.
Fine-tuning then truncated the Danish silver label at 128 mT5 tokens.
This module scores that shape on Toftevig fixtures without running T5.
"""

from __future__ import annotations

from dataclasses import dataclass

from pakhus.packing import PackResult, pack_course_summary
from pakhus.sentences import split_naive
from pakhus.tokenize import approx_encode_len, word_tokenize
from pakhus.world import find_figures, find_names


LABEL_CAP = 128  # finetune.py max_length on the summary column
PANE_BRIEF_CAP = 80  # summary.py max_length per pane


def truncate_to_units(text: str, cap: int) -> str:
    """Keep whole words until approx_encode_len would exceed cap."""
    words = text.split()
    kept: list[str] = []
    for word in words:
        trial = " ".join(kept + [word])
        if kept and approx_encode_len(trial) > cap:
            break
        kept.append(word)
    return " ".join(kept)


def pane_brief(text: str, cap: int = PANE_BRIEF_CAP) -> str:
    """Lead sentence plus figure sentences, capped like the T5 decoder."""
    if not text.strip():
        return ""
    sentences = split_naive(text) or [text.strip()]
    chosen: list[str] = [sentences[0]]
    for sent in sentences[1:]:
        if sent in chosen:
            continue
        if find_figures(sent):
            chosen.append(sent)
        elif find_names(sent) and approx_encode_len(" ".join(chosen)) < cap // 2:
            chosen.append(sent)
    return truncate_to_units(" ".join(chosen), cap)


def silver_from_panes(result: PackResult, cap: int = PANE_BRIEF_CAP) -> tuple[str, list[str]]:
    briefs = [pane_brief(pane.text, cap=cap) for pane in result.panes if not pane.empty]
    return " ".join(b for b in briefs if b).strip(), briefs


@dataclass(frozen=True)
class ConcatScore:
    article_id: str
    n_panes: int
    silver_units: int
    would_truncate_at_128: bool
    truncated_units: int
    pane0_share: float
    echo_names: tuple[str, ...]
    figures_in_source: tuple[str, ...]
    figures_in_silver: tuple[str, ...]
    figure_survival: float
    leftover_fill: float
    silver: str
    silver_kept_at_128: str

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.article_id,
            "n_panes": self.n_panes,
            "silver_units": self.silver_units,
            "would_truncate_at_128": self.would_truncate_at_128,
            "truncated_units": self.truncated_units,
            "pane0_share": round(self.pane0_share, 4),
            "echo_names": ";".join(self.echo_names),
            "figure_survival": round(self.figure_survival, 4),
            "leftover_fill": round(self.leftover_fill, 4),
            "figures_in_source": ";".join(self.figures_in_source),
            "figures_in_silver": ";".join(self.figures_in_silver),
        }


def _echo_names(briefs: list[str]) -> tuple[str, ...]:
    counts: dict[str, int] = {}
    for brief in briefs:
        for name in find_names(brief):
            counts[name] = counts.get(name, 0) + 1
    return tuple(sorted(name for name, n in counts.items() if n > 1))


def score_concat(
    article_id: str,
    source_text: str,
    pack_result: PackResult | None = None,
) -> ConcatScore:
    result = pack_result or pack_course_summary(source_text)
    silver, briefs = silver_from_panes(result)
    units = approx_encode_len(silver) if silver else 0
    kept = truncate_to_units(silver, LABEL_CAP)
    pane0_units = approx_encode_len(briefs[0]) if briefs else 0
    figures_src = tuple(find_figures(source_text))
    figures_sil = tuple(find_figures(silver))
    survival = (
        0.0
        if not figures_src
        else len([f for f in figures_src if f.lower() in silver.lower()]) / len(figures_src)
    )
    leftover = result.panes[-1].fill_ratio if result.panes else 0.0
    return ConcatScore(
        article_id=article_id,
        n_panes=len([p for p in result.panes if not p.empty]),
        silver_units=units,
        would_truncate_at_128=units > LABEL_CAP,
        truncated_units=max(0, units - LABEL_CAP),
        pane0_share=(pane0_units / units) if units else 0.0,
        echo_names=_echo_names(briefs),
        figures_in_source=figures_src,
        figures_in_silver=figures_sil,
        figure_survival=survival,
        leftover_fill=leftover,
        silver=silver,
        silver_kept_at_128=kept,
    )


def lcs_len(a: list[str], b: list[str]) -> int:
    if not a or not b:
        return 0
    dp = [0] * (len(b) + 1)
    for tok in a:
        prev = 0
        for j, other in enumerate(b, start=1):
            stored = dp[j]
            if tok == other:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            prev = stored
    return dp[-1]


def rouge_l(pred: str, ref: str) -> float:
    """Token-level ROUGE-L F1 on whitespace words (lab metric, not evaluate.rouge)."""
    pred_toks = [t.lower() for t in word_tokenize(pred) if t.strip()]
    ref_toks = [t.lower() for t in word_tokenize(ref) if t.strip()]
    if not pred_toks or not ref_toks:
        return 0.0
    overlap = lcs_len(pred_toks, ref_toks)
    prec = overlap / len(pred_toks)
    rec = overlap / len(ref_toks)
    if prec + rec == 0:
        return 0.0
    return 2 * prec * rec / (prec + rec)
