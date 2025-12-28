"""
nda_enforcement.policy

Business rules for NDA enforcement.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
from .config import NDAConfig
from .storage import NDAStore
from .models import RevocationRecord
from datetime import datetime, timezone

@dataclass
class EnforcementResult:
    allowed: bool
    reason_code: str
    reason_detail: str

def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def enforce_for_tester(config: NDAConfig, store: NDAStore, tester_id: str) -> EnforcementResult:
    # Revocation always wins
    rev = store.get_revocation(tester_id)
    if rev:
        return EnforcementResult(False, "ACCESS_REVOKED", f"Access revoked: {rev.get('reason_code')} - {rev.get('reason_detail')}")

    if not config.require_acceptance:
        return EnforcementResult(True, "OK", "Acceptance not required by config.")

    acc = store.get_acceptance(tester_id)
    if not acc:
        return EnforcementResult(False, "MISSING_ACCEPTANCE", "No acceptance record found for this tester.")

    # Per-build pinning: build_id, nda_version, nda_doc_sha256 must match.
    if acc.get("build_id") != config.build_id:
        return EnforcementResult(False, "BUILD_MISMATCH", f"Accepted build_id={acc.get('build_id')} but running build_id={config.build_id}.")
    if acc.get("nda_version") != config.nda_version:
        return EnforcementResult(False, "VERSION_MISMATCH", f"Accepted nda_version={acc.get('nda_version')} but required nda_version={config.nda_version}.")
    if acc.get("nda_doc_sha256") != config.nda_doc_sha256:
        return EnforcementResult(False, "DOC_HASH_MISMATCH", "The accepted NDA document hash differs from the required document hash.")
    return EnforcementResult(True, "OK", "Acceptance verified for this build and NDA version.")

def revoke_access(config: NDAConfig, store: NDAStore, tester_id: str, reason_code: str, reason_detail: str) -> None:
    rec = RevocationRecord(
        tester_id=tester_id,
        revoked_at_utc=_now_iso(),
        reason_code=reason_code,
        reason_detail=reason_detail,
        build_id=config.build_id,
        nda_version=config.nda_version,
    )
    store.save_revocation(rec)
