# nda_enforcement/config.py

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

# ===== Build + NDA Enforcement (Simple Variables) =====

build_id = "beta-1.0.0"   # bump when you ship a new build

nda_version = "NDA-BETA-TESTER-2025-01"

nda_filename = "NDA_Beta_Tester_IDOCInTheBox_Creations_LLC.pdf"

nda_doc_sha256 = "531fae6072132a505c914b99ef845a27671105db12b0a8d068a6bdf0b53fceac"


# ===== App Data Location =====

def default_app_data_dir() -> Path:
    """
    Per-user storage for NDA acceptance records and audit logs.
    """
    return Path.home() / ".idocinthebox"


# ===== NDAConfig Dataclass (For Compatibility) =====

@dataclass(frozen=True)
class NDAConfig:
    """
    Configuration for NDA enforcement. This dataclass is used by all NDA modules.
    The default values are populated from the simple variables above.
    """
    build_id: str
    nda_version: str
    nda_doc_sha256: str
    app_data_dir: Path
    require_acceptance: bool = True
    allow_offline_grace_seconds: int = 0
    revoke_on_breach: bool = True


def get_default_config() -> NDAConfig:
    """
    Creates a default NDAConfig using the simple variables defined above.
    This is the recommended way to get config in your app.
    """
    return NDAConfig(
        build_id=build_id,
        nda_version=nda_version,
        nda_doc_sha256=nda_doc_sha256,
        app_data_dir=default_app_data_dir(),
    )
