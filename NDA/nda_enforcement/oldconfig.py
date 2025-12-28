"""
nda_enforcement.config

Central configuration for NDA version enforcement, acceptance storage, and revocation policy.
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os

@dataclass(frozen=True)
class NDAConfig:
    # Per-build NDA enforcement
    build_id: str                 # e.g., "beta-1.0.3+2025-12-27"
    nda_version: str              # e.g., "NDA-HARDENED-2025-12-27"
    nda_doc_sha256: str           # sha256 of the NDA PDF or text presented to testers

    # Storage
    app_data_dir: Path            # where acceptance records and logs live

    # Policy
    require_acceptance: bool = True
    allow_offline_grace_seconds: int = 0  # set >0 only if you want temporary offline grace
    revoke_on_breach: bool = True


def default_app_data_dir(app_name: str = "AdvancedTapeRestorer") -> Path:
    """
    Cross-platform-ish default location. You can override in your app.
    """
    base = os.getenv("APPDATA") or os.getenv("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return Path(base) / app_name / "nda"
