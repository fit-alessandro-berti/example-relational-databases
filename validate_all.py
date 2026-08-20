#!/usr/bin/env python3
"""Audit generated artifacts without regenerating them."""

import json
import sqlite3
from pathlib import Path

from benchmark import SCENARIOS


ROOT = Path(__file__).resolve().parent
required = {
    "source.sqlite", "schema.sql", "generate_data.py", "source_documentation.md",
    "business_glossary.md", "challenge_manifest.json", "ground_truth.ocel2.sqlite",
    "validation_report.json",
}

failed = False
for slug, scenario in SCENARIOS.items():
    folder = ROOT / scenario.folder
    missing = sorted(name for name in required if not (folder / name).is_file())
    report_path = folder / "validation_report.json"
    status = "MISSING"
    if not missing:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        status = report.get("status", "UNKNOWN")
        with sqlite3.connect(folder / "ground_truth.ocel2.sqlite") as conn:
            integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        with sqlite3.connect(folder / "source.sqlite") as conn:
            source_integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok" or source_integrity != "ok":
            status = "FAIL"
    if missing or status != "PASS":
        failed = True
    print(f"{slug}: {status}" + (f" missing={','.join(missing)}" if missing else ""))

raise SystemExit(1 if failed else 0)

