"""
nda_enforcement.acceptance_flow

A minimal helper to record acceptance from:
- in-app clickwrap
- DocuSign completion
- email reply confirmation (not ideal, but sometimes used)

You still need to show the NDA text/PDF in your app and capture "I Agree".
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from .models import AcceptanceRecord
from .storage import NDAStore
from .config import NDAConfig

def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def record_acceptance(
    config: NDAConfig,
    tester_name: str,
    tester_email: str,
    tester_id: str,
    acceptance_type: str = "InApp",
    ip_address: Optional[str] = None,
    device_fingerprint: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    store = NDAStore(config.app_data_dir)
    rec = AcceptanceRecord(
        tester_name=tester_name,
        tester_email=tester_email,
        tester_id=tester_id,
        nda_version=config.nda_version,
        build_id=config.build_id,
        nda_doc_sha256=config.nda_doc_sha256,
        acceptance_type=acceptance_type,
        accepted_at_utc=_now_iso(),
        ip_address=ip_address,
        device_fingerprint=device_fingerprint,
        extra=extra,
    )
    store.save_acceptance(rec)
