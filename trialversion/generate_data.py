#!/usr/bin/env python3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmark import build_scenario

if __name__ == "__main__":
    report = build_scenario("trialversion", Path(__file__).resolve().parent)
    print(f"trialversion: {report['status']} — {report['oracle_event_count']} events")

