"""Write course-shaped CSVs and ledger tables from the handwritten corpus."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .corpus import SPLIT_IDS, Brief, all_briefs, briefs_for_split
from .ledger import HOPS, build_all_ledgers
from .schemas import COURSE_SCHEMAS

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA = REPO_ROOT / "examples" / "data"


def write_all_tables(out_dir: Path | None = None) -> list[Path]:
    dest = Path(out_dir) if out_dir else DEFAULT_DATA
    dest.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    written.append(_write_csv(dest / "kystlinje_articles.csv", _source_rows(), ("id", "article text")))
    written.append(
        _write_csv(
            dest / "kystlinje_translated.csv",
            _translated_rows(),
            ("id", "body", "translated"),
        )
    )
    written.append(
        _write_csv(
            dest / "kystlinje_summarized.csv",
            _summarized_rows(),
            ("id", "body", "translated", "summary"),
        )
    )
    written.append(
        _write_csv(
            dest / "kystlinje_labeled.csv",
            _labeled_rows(),
            ("id", "body", "summary"),
        )
    )
    for split in ("train", "validation", "test"):
        written.append(
            _write_csv(
                dest / f"kystlinje_{split}.csv",
                _labeled_rows(briefs_for_split(split)),
                ("id", "body", "summary"),
            )
        )
    written.append(_write_ledger_csv(dest / "kystlinje_ledger.csv"))
    written.append(_write_error_csv(dest / "kystlinje_planted_errors.csv"))
    written.append(_write_json(dest / "kystlinje_briefs.json", _briefs_json()))
    written.append(_write_schema_json(dest / "course_schemas.json"))
    return written


def _source_rows(briefs: tuple[Brief, ...] | None = None) -> list[dict[str, str]]:
    return [{"id": b.id, "article text": b.body_da} for b in (briefs or all_briefs())]


def _translated_rows(briefs: tuple[Brief, ...] | None = None) -> list[dict[str, str]]:
    return [
        {"id": b.id, "body": b.body_da, "translated": b.pivot_en}
        for b in (briefs or all_briefs())
    ]


def _summarized_rows(briefs: tuple[Brief, ...] | None = None) -> list[dict[str, str]]:
    return [
        {
            "id": b.id,
            "body": b.body_da,
            "translated": b.pivot_en,
            "summary": b.summary_en,
        }
        for b in (briefs or all_briefs())
    ]


def _labeled_rows(briefs: tuple[Brief, ...] | None = None) -> list[dict[str, str]]:
    return [
        {"id": b.id, "body": b.body_da, "summary": b.silver_da}
        for b in (briefs or all_briefs())
    ]


def _write_csv(path: Path, rows: list[dict[str, str]], columns: tuple[str, ...]) -> Path:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns))
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row[col] for col in columns})
    return path


def _write_ledger_csv(path: Path) -> Path:
    columns = (
        "id",
        "entity_key",
        "kind",
        "surface",
        *HOPS,
    )
    rows: list[dict[str, str]] = []
    for ledger in build_all_ledgers():
        for row in ledger.rows:
            rec = {
                "id": ledger.brief.id,
                "entity_key": row.entity.key,
                "kind": row.entity.kind,
                "surface": row.entity.surface,
            }
            for hop in HOPS:
                rec[hop] = "1" if row.survived(hop) else "0"
            rows.append(rec)
    return _write_csv(path, rows, columns)


def _write_error_csv(path: Path) -> Path:
    columns = ("id", "code", "hop", "source_span", "drifted_span", "note")
    rows = [
        {
            "id": brief.id,
            "code": err.code,
            "hop": err.hop,
            "source_span": err.source_span,
            "drifted_span": err.drifted_span,
            "note": err.note,
        }
        for brief in all_briefs()
        for err in brief.planted
    ]
    return _write_csv(path, rows, columns)


def _briefs_json() -> dict[str, object]:
    return {
        "world": "Hjelmøerne / Kystlinje magazine (fiction)",
        "splits": {name: list(ids) for name, ids in SPLIT_IDS.items()},
        "briefs": [
            {
                "id": b.id,
                "title_da": b.title_da,
                "title_en": b.title_en,
                "themes": list(b.themes),
                "planted": [
                    {
                        "code": e.code,
                        "hop": e.hop,
                        "source_span": e.source_span,
                        "drifted_span": e.drifted_span,
                        "note": e.note,
                    }
                    for e in b.planted
                ],
            }
            for b in all_briefs()
        ],
    }


def _write_json(path: Path, payload: object) -> Path:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _write_schema_json(path: Path) -> Path:
    payload = [
        {
            "name": s.name,
            "script": s.script,
            "columns": list(s.columns),
            "notes": s.notes,
        }
        for s in COURSE_SCHEMAS
    ]
    return _write_json(path, payload)
