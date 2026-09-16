"""Plain-text and HTML desk notes for the Sejerø workbook."""

from __future__ import annotations

import html
from pathlib import Path

from sejeroe.fixtures import ARTICLES
from sejeroe.length import pair_lengths
from sejeroe.manchet import score_manchet
from sejeroe.metrics import planted_blind_spots, score_article
from sejeroe.packing import PRESETS, pack_text
from sejeroe.paths import GENERATED_DOCS, REPORT_DIR, ensure_output_dirs
from sejeroe.tokenize import LengthNotion


def build_text_report() -> str:
    lines: list[str] = [
        "Sejerø Tidende — manchet desk notes",
        "==================================",
        "",
        "Closed-world fiction. No scraped news. No course weights.",
        f"Briefs: {len(ARTICLES)}  "
        f"train={sum(1 for a in ARTICLES if a.split=='train')}  "
        f"validation={sum(1 for a in ARTICLES if a.split=='validation')}  "
        f"test={sum(1 for a in ARTICLES if a.split=='test')}",
        "",
        "Silver-label hops (hand-written stand-ins)",
        "------------------------------------------",
        "raw_da -> translated_en -> summarized_en -> labeled_da",
        "oracle_da is a human manchet written against the gold 5W1H card.",
        "",
    ]

    lines.append("Manchet coverage (first sentence vs WHO/WHAT/WHEN/WHERE)")
    lines.append("--------------------------------------------------------")
    for article in ARTICLES:
        silver = score_manchet(article, article.summary_da, "summary_da")
        oracle = score_manchet(article, article.oracle_da, "oracle_da")
        lines.append(
            f"{article.id}  silver={silver.coverage:.2f} miss={list(silver.misses) or '-'}  "
            f"oracle={oracle.coverage:.2f} miss={list(oracle.misses) or '-'}"
        )
    lines.append("")

    lines.append("Slot recall and quote survival on the Danish silver label")
    lines.append("---------------------------------------------------------")
    for article in ARTICLES:
        row = next(item for item in score_article(article) if item.text_role == "summary_da")
        lines.append(
            f"{article.id}  slots={row.slot_recall:.2f} missing={list(row.missing_slots) or '-'}  "
            f"quotes={row.quotes_kept}/{row.quotes_total}  "
            f"connectives={row.connectives_kept}/{row.connectives_total}  "
            f"R1-vs-oracle={row.rouge1_vs_oracle:.2f}"
        )
    lines.append("")

    lines.append("Planted errors: overlap can stay high while a slot dies")
    lines.append("------------------------------------------------------")
    for article in ARTICLES:
        for item in planted_blind_spots(article):
            lines.append(
                f"{item['article_id']}  {item['kind']}: "
                f"R1 {item['planted_rouge1_vs_silver']:.2f} vs silver  "
                f"slot recall {item['silver_slot_recall']:.2f}->{item['planted_slot_recall']:.2f}  "
                f"missing={item['planted_missing_slots'] or '-'}  "
                f"({item['note']})"
            )
    lines.append("")

    lines.append("Length inflation Danish body -> English body")
    lines.append("-------------------------------------------")
    for article in ARTICLES:
        words = pair_lengths(article, LengthNotion.WORDS)
        pieces = pair_lengths(article, LengthNotion.ROUGH_SUBWORD)
        lines.append(
            f"{article.id}  words {words.danish}->{words.english} "
            f"(x{words.ratio:.2f})  subwords {pieces.danish}->{pieces.english} "
            f"(x{pieces.ratio:.2f})"
        )
    lines.append("")

    lines.append("Packing windows on the Danish body")
    lines.append("----------------------------------")
    for article in ARTICLES:
        bits = []
        for name in ("manchet-tight", "manchet-lead", "t5-summary-cap", "forward-hop"):
            policy = PRESETS[name]
            windows = pack_text(article.body_da, policy)
            bits.append(f"{name}={len(windows)}")
        lines.append(f"{article.id}  " + "  ".join(bits))
    lines.append("")
    lines.append("See docs/07-workbook.md for the exercise list.")
    return "\n".join(lines) + "\n"


def build_html_report() -> str:
    text_rows = []
    for article in ARTICLES:
        silver = next(item for item in score_article(article) if item.text_role == "summary_da")
        manchet = score_manchet(article, article.summary_da, "summary_da")
        text_rows.append(
            "<tr>"
            f"<td>{html.escape(article.id)}</td>"
            f"<td>{html.escape(article.split)}</td>"
            f"<td>{silver.slot_recall:.2f}</td>"
            f"<td>{html.escape(', '.join(silver.missing_slots) or '—')}</td>"
            f"<td>{manchet.coverage:.2f}</td>"
            f"<td>{html.escape(', '.join(manchet.misses) or '—')}</td>"
            f"<td>{silver.quotes_kept}/{silver.quotes_total}</td>"
            f"<td>{silver.rouge1_vs_oracle:.2f}</td>"
            "</tr>"
        )

    planted_rows = []
    for article in ARTICLES:
        for item in planted_blind_spots(article):
            planted_rows.append(
                "<tr>"
                f"<td>{html.escape(str(item['article_id']))}</td>"
                f"<td>{html.escape(str(item['kind']))}</td>"
                f"<td>{item['planted_rouge1_vs_silver']:.2f}</td>"
                f"<td>{item['silver_slot_recall']:.2f} → {item['planted_slot_recall']:.2f}</td>"
                f"<td>{html.escape(str(item['planted_missing_slots']) or '—')}</td>"
                f"<td>{html.escape(str(item['note']))}</td>"
                "</tr>"
            )

    briefs = []
    for article in ARTICLES:
        briefs.append(
            "<article class='brief'>"
            f"<h3>{html.escape(article.id)} — {html.escape(article.headline_da)}</h3>"
            f"<p class='lede'><strong>Manchet:</strong> {html.escape(article.lead_da)}</p>"
            f"<p><strong>Silver DA:</strong> {html.escape(article.summary_da)}</p>"
            f"<p><strong>Oracle DA:</strong> {html.escape(article.oracle_da)}</p>"
            "</article>"
        )

    return f"""<!DOCTYPE html>
<html lang="da">
<head>
  <meta charset="utf-8">
  <title>Sejerø Tidende — manchet desk</title>
  <style>
    body {{ font-family: Georgia, serif; margin: 2rem auto; max-width: 960px; color: #222; }}
    h1, h2, h3 {{ font-family: Palatino, Georgia, serif; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; font-size: 0.95rem; }}
    th, td {{ border: 1px solid #ccc; padding: 0.4rem 0.5rem; text-align: left; vertical-align: top; }}
    th {{ background: #f3efe6; }}
    .brief {{ border-top: 1px solid #ddd; padding: 0.8rem 0; }}
    .lede {{ font-style: italic; }}
    .note {{ color: #444; }}
  </style>
</head>
<body>
  <h1>Sejerø Tidende</h1>
  <p class="note">Personal manchet / 5W1H / quote desk for the 2023 silver-label hops. Fiction only.</p>
  <h2>Silver labels vs gold cards</h2>
  <table>
    <thead>
      <tr>
        <th>id</th><th>split</th><th>slot recall</th><th>missing slots</th>
        <th>manchet</th><th>lede misses</th><th>quotes</th><th>R1 vs oracle</th>
      </tr>
    </thead>
    <tbody>
      {''.join(text_rows)}
    </tbody>
  </table>
  <h2>Planted errors</h2>
  <table>
    <thead>
      <tr>
        <th>id</th><th>kind</th><th>R1 vs silver</th><th>slot recall</th>
        <th>missing</th><th>note</th>
      </tr>
    </thead>
    <tbody>
      {''.join(planted_rows)}
    </tbody>
  </table>
  <h2>Briefs</h2>
  {''.join(briefs)}
</body>
</html>
"""


def write_reports() -> dict[str, Path]:
    ensure_output_dirs()
    text = build_text_report()
    page = build_html_report()
    paths = {
        "txt": GENERATED_DOCS / "desk-notes.txt",
        "html_docs": GENERATED_DOCS / "desk-notes.html",
        "html_examples": REPORT_DIR / "index.html",
    }
    paths["txt"].write_text(text, encoding="utf-8")
    paths["html_docs"].write_text(page, encoding="utf-8")
    paths["html_examples"].write_text(page, encoding="utf-8")
    return paths
