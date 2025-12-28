"""
Example: integrate NDA enforcement into your app startup.

- Pin NDA version & document hash per build.
- Enforce at startup.
- Record acceptance after user clicks "I Agree".
- Revoke access immediately on breach signals.

This example is CLI-based, but the calls map 1:1 to your PySide6/Tk UI.
"""
from pathlib import Path
from nda_enforcement.config import NDAConfig, default_app_data_dir
from nda_enforcement.crypto import sha256_file
from nda_enforcement.hooks import on_app_start, report_breach
from nda_enforcement.acceptance_flow import record_acceptance

# ---- Build constants (bake these into each build) ----
BUILD_ID = "beta-1.0.0+2025-12-27"
NDA_VERSION = "NDA-HARDENED-2025-12-27"
NDA_DOC_PATH = Path("NDA_Hardened_Final_Tightened.pdf")  # ship alongside the build
# For safety, compute hash at build/package time and hardcode it,
# or compute at runtime if you ship the NDA file in a stable path.
NDA_SHA256 = sha256_file(NDA_DOC_PATH)

cfg = NDAConfig(
    build_id=BUILD_ID,
    nda_version=NDA_VERSION,
    nda_doc_sha256=NDA_SHA256,
    app_data_dir=default_app_data_dir(),
)

def main():
    tester_id = input("Tester ID: ").strip() or "UNKNOWN"
    allowed, msg = on_app_start(cfg, tester_id)
    print("ENFORCEMENT:", msg)

    if not allowed:
        print("You must accept the NDA to proceed.")
        # In-app flow: display NDA, require checkbox + "I Agree".
        agree = input('Type "I AGREE" to accept: ').strip().upper() == "I AGREE"
        if not agree:
            print("Not accepted. Exiting.")
            return

        name = input("Tester name: ").strip()
        email = input("Tester email: ").strip()
        record_acceptance(cfg, tester_name=name, tester_email=email, tester_id=tester_id, acceptance_type="InApp")
        allowed, msg = on_app_start(cfg, tester_id)
        print("ENFORCEMENT:", msg)
        if not allowed:
            print("Still blocked; exiting.")
            return

    print("Access granted. (Your app starts here.)")

    # Example breach trigger
    # report_breach(cfg, tester_id, "Detected leaked watermark on public forum post: <url>")

if __name__ == "__main__":
    main()
