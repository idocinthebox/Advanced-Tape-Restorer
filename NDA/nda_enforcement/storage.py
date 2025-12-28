"""
nda_enforcement.storage

Durable local storage for acceptance and revocation records.
- JSONL (append-only) for event logs
- JSON (latest state) for fast checks
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional, Dict, Any
from .models import AcceptanceRecord, RevocationRecord

def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

class NDAStore:
    def __init__(self, app_data_dir: Path):
        self.app_data_dir = app_data_dir
        _ensure_dir(self.app_data_dir)
        self.state_path = self.app_data_dir / "state.json"
        self.events_path = self.app_data_dir / "events.jsonl"

    def append_event(self, event: Dict[str, Any]) -> None:
        with self.events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, sort_keys=True) + "\n")

    def load_state(self) -> Dict[str, Any]:
        return _read_json(self.state_path) or {"accepted": {}, "revoked": {}}

    def save_state(self, state: Dict[str, Any]) -> None:
        _write_json(self.state_path, state)

    def save_acceptance(self, rec: AcceptanceRecord) -> None:
        state = self.load_state()
        state["accepted"][rec.tester_id] = rec.to_dict()
        self.save_state(state)
        self.append_event({"type": "ACCEPTANCE", **rec.to_dict()})

    def save_revocation(self, rec: RevocationRecord) -> None:
        state = self.load_state()
        state["revoked"][rec.tester_id] = rec.to_dict()
        # optionally remove acceptance to force re-acceptance if you reinstate
        state["accepted"].pop(rec.tester_id, None)
        self.save_state(state)
        self.append_event({"type": "REVOCATION", **rec.to_dict()})

    def get_acceptance(self, tester_id: str) -> Optional[Dict[str, Any]]:
        state = self.load_state()
        return state.get("accepted", {}).get(tester_id)

    def get_revocation(self, tester_id: str) -> Optional[Dict[str, Any]]:
        state = self.load_state()
        return state.get("revoked", {}).get(tester_id)
