"""
nda_enforcement.models

Data models for acceptance and revocation events.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

@dataclass
class AcceptanceRecord:
    tester_name: str
    tester_email: str
    tester_id: str
    nda_version: str
    build_id: str
    nda_doc_sha256: str
    acceptance_type: str  # "InApp" | "DocuSign" | "Email"
    accepted_at_utc: str  # ISO 8601
    ip_address: Optional[str] = None
    device_fingerprint: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class RevocationRecord:
    tester_id: str
    revoked_at_utc: str
    reason_code: str   # e.g. "NDA_BREACH" | "MISSING_ACCEPTANCE" | "VERSION_MISMATCH"
    reason_detail: str
    build_id: str
    nda_version: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
