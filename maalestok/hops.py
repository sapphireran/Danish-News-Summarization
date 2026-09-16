"""Compare measures across silver-label hops and name the failure.

A later checkout should be able to say *why* a number died, not only that
it is missing. The labels below are the ones the Blåhøj fixtures plant.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from .measures import Measure


@dataclass(frozen=True)
class HopPair:
    source: Measure
    target: Measure | None
    label: str
    detail: str


def classify_pair(source: Measure, target: Measure | None) -> HopPair:
    if target is None:
        return HopPair(source, None, "missing", "no counterpart in this hop")

    s_kind, s_val, s_unit = source.normalized()
    t_kind, t_val, t_unit = target.normalized()

    if s_val is not None and t_val is not None and s_val == t_val and s_unit == t_unit and s_kind == t_kind:
        if source.extra and target.extra and source.extra != target.extra and s_kind in {"feast", "date", "dimension", "clock_range"}:
            if s_kind == "feast":
                return HopPair(source, target, "feast_swap", f"{source.extra} → {target.extra}")
            if s_kind == "dimension":
                return HopPair(source, target, "dimension_shift", f"second axis {source.extra} → {target.extra}")
            if s_kind == "clock_range":
                return HopPair(source, target, "clock_shift", f"range end {source.extra} → {target.extra}")
            return HopPair(source, target, "extra_rewrite", f"{source.extra} → {target.extra}")
        return HopPair(source, target, "ok", "same normalized value and unit")

    if s_kind == "feast" and t_kind == "feast" and source.extra != target.extra:
        return HopPair(source, target, "feast_swap", f"{source.extra} → {target.extra}")

    if s_kind == "line" and t_kind == "line" and s_val != t_val:
        return HopPair(source, target, "line_swap", f"{s_val} → {t_val}")

    if s_kind == "clock" and t_kind == "clock" and s_val is not None and t_val is not None:
        if abs(s_val - t_val) == Decimal(12 * 60):
            return HopPair(source, target, "clock_12h", f"{source.extra} → {target.extra}")
        return HopPair(source, target, "clock_shift", f"{source.extra} → {target.extra}")

    if s_kind == "clock_range" and t_kind == "clock_range":
        return HopPair(source, target, "clock_shift", f"{source.raw} → {target.raw}")

    if s_kind == "money" and t_kind == "money" and s_unit != t_unit:
        return HopPair(source, target, "currency_swap", f"{s_unit} → {t_unit}")

    if s_kind == "temperature" and t_kind == "temperature":
        if s_val is not None and t_val is not None and s_val == -t_val:
            return HopPair(source, target, "sign_drop", "minus dropped")
        if s_val is not None and t_val is not None and abs(s_val) == abs(t_val) and source.sign != target.sign:
            return HopPair(source, target, "sign_drop", "minus dropped")

    if s_kind == "dimension" and t_kind == "dimension":
        return HopPair(source, target, "dimension_shift", f"{source.raw} → {target.raw}")

    if s_val is not None and t_val is not None and s_unit != t_unit and _same_magnitude(s_val, t_val):
        return HopPair(source, target, "unit_swap", f"{s_unit} → {t_unit}")

    if s_val is not None and t_val is not None:
        if _is_comma_shift(s_val, t_val):
            return HopPair(source, target, "comma_shift", f"{s_val} → {t_val}")
        if _is_scale_shift(source, target, s_val, t_val):
            return HopPair(source, target, "scale_shift", f"{s_val} → {t_val}")
        if _is_precision_loss(s_val, t_val):
            return HopPair(source, target, "precision_loss", f"{s_val} → {t_val}")

    if s_unit != t_unit:
        return HopPair(source, target, "unit_swap", f"{s_unit} → {t_unit}")
    return HopPair(source, target, "value_shift", f"{s_val} → {t_val}")


def align_measures(source: Iterable[Measure], target: Iterable[Measure]) -> list[HopPair]:
    """Greedy alignment: same kind first, then unused nearest value."""
    remaining = list(target)
    pairs: list[HopPair] = []
    for item in source:
        match = _best_match(item, remaining)
        if match is not None:
            remaining.remove(match)
        pairs.append(classify_pair(item, match))
    for extra in remaining:
        pairs.append(HopPair(extra, extra, "hallucinated", "appears only after the hop"))
    return pairs


def _best_match(source: Measure, pool: list[Measure]) -> Measure | None:
    # Same kind only. Cross-kind leftovers used to steal clocks and dates
    # and report a fake unit_swap instead of ``missing``.
    candidates = [m for m in pool if m.kind == source.kind]
    if not candidates:
        return None

    def score(other: Measure) -> tuple[int, Decimal]:
        kind_penalty = 0 if other.kind == source.kind else 1
        unit_penalty = 0 if other.unit == source.unit else 1
        _, s_val, _ = source.normalized()
        _, t_val, _ = other.normalized()
        if s_val is None or t_val is None:
            dist = Decimal(10**9)
        else:
            dist = abs(s_val - t_val)
            # Prefer comma-shift / 12h partners over a distant same-kind number.
            if _is_comma_shift(s_val, t_val):
                dist = Decimal("0.5")
            if source.kind == "clock" and abs(s_val - t_val) == Decimal(12 * 60):
                dist = Decimal("0.25")
        return (kind_penalty + unit_penalty, dist)

    return min(candidates, key=score)


def _same_magnitude(a: Decimal, b: Decimal) -> bool:
    return a == b or abs(a) == abs(b)


def _is_comma_shift(a: Decimal, b: Decimal) -> bool:
    if a == 0 or b == 0:
        return False
    ratio = abs(b / a)
    return ratio in {Decimal(10), Decimal(100), Decimal("0.1"), Decimal("0.01")}


def _is_scale_shift(source: Measure, target: Measure, s_val: Decimal, t_val: Decimal) -> bool:
    if source.scale != target.scale:
        return True
    return _is_comma_shift(s_val, t_val) and source.kind == "money"


def _is_precision_loss(a: Decimal, b: Decimal) -> bool:
    if a == b:
        return False
    # Rounded toward the integer or one fewer decimal place.
    try:
        if b == a.to_integral_value() or a.to_integral_value() == b:
            return True
    except Exception:
        return False
    return abs(a - b) <= Decimal("1") and max(abs(a), abs(b)) >= 1
