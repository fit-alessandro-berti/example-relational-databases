#!/usr/bin/env python3
"""Regenerate every source database, oracle, report, and case view."""

from pathlib import Path

from benchmark import build_all


if __name__ == "__main__":
    reports = build_all(Path(__file__).resolve().parent)
    for report in reports:
        print(f"{report['scenario']}: {report['status']} — {report['oracle_event_count']} events, {report['source_row_count']} source rows")

