"""Example scripts run end to end."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def _run(script: str, extra: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(EXAMPLES / script), *(extra or [])],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_compare_splitters() -> None:
    proc = _run("compare_splitters.py", ["--article", "tof-003"])
    assert proc.returncode == 0, proc.stderr
    assert "extra_naive_cuts" in proc.stdout
    assert "kl. 18.30" in proc.stdout


def test_inspect_concat_json() -> None:
    proc = _run("inspect_concat.py", ["--article", "tof-001"])
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["would_truncate_at_128"] is True
    assert payload["n_hop1_panes"] == 2


def test_scan_scars_example() -> None:
    proc = _run("scan_scars.py")
    assert proc.returncode == 0, proc.stderr
    assert "nllb-lang-da" in proc.stdout
