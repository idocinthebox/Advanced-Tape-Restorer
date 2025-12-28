"""
nda_enforcement.hooks

Hooks you can connect to your app:
- on_app_start: enforce acceptance before allowing access
- report_breach: revoke access immediately if you detect breach
- export_audit: export events.jsonl to a CSV for legal/audit purposes
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional
import csv
from .config import NDAConfig
from .storage import NDAStore
from .policy import enforce_for_tester, revoke_access

def on_app_start(config: NDAConfig, tester_id: str) -> tuple[bool, str]:
    """
    Call this as early as possible. If returns (False, message) you should block the UI
    and route the user to your acceptance flow.
    """
    store = NDAStore(config.app_data_dir)
    res = enforce_for_tester(config, store, tester_id)
    return res.allowed, f"{res.reason_code}: {res.reason_detail}"

def report_breach(config: NDAConfig, tester_id: str, detail: str) -> None:
    """
    Call this when you have evidence of an NDA breach.
    Typical sources: leaked build watermark, public post, unauthorized benchmark, etc.
    """
    store = NDAStore(config.app_data_dir)
    revoke_access(config, store, tester_id, reason_code="NDA_BREACH", reason_detail=detail)

def export_audit_csv(app_data_dir: Path, out_csv: Path) -> None:
    """
    Exports the JSONL event log to CSV for quick review.
    """
    events_path = Path(app_data_dir) / "events.jsonl"
    if not events_path.exists():
        out_csv.write_text("No events found.\n", encoding="utf-8")
        return

    rows = []
    with events_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(__import__("json").loads(line))

    # Collect all keys
    keys = sorted({k for r in rows for k in r.keys()})
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)
