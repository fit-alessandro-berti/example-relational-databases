#!/usr/bin/env python3
"""Audit generated artifacts without regenerating them."""

import csv
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


def csv_is_sorted(path: Path) -> bool:
    previous: tuple[str, str, str] | None = None
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if (reader.fieldnames or [])[:3] != ["case_id", "activity", "timestamp"]:
            return False
        for row in reader:
            current = (row["case_id"], row["timestamp"], row["source_record_id"])
            if previous is not None and current < previous:
                return False
            previous = current
    return True


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
        checks_pass = all(report.get("checks", {}).values())
        views_pass = all(
            (folder / view["csv"]).is_file()
            and (folder / view["sql"]).is_file()
            and view.get("sort_order") == ["case_id", "timestamp", "source_record_id"]
            and csv_is_sorted(folder / view["csv"])
            for view in report.get("case_views", [])
        )
        if integrity != "ok" or source_integrity != "ok" or not checks_pass or not views_pass:
            status = "FAIL"
    if missing or status != "PASS":
        failed = True
    print(f"{slug}: {status}" + (f" missing={','.join(missing)}" if missing else ""))

raise SystemExit(1 if failed else 0)
