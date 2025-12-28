"""
demo_pyside6_clickwrap.py

Run this to see the clickwrap dialog in action.

Prereqs:
- pip install PySide6
- Put the NDA PDF next to this script (or edit NDA_PDF below)
- Ensure nda_enforcement package folder is in the same directory (this repo)

python demo_pyside6_clickwrap.py
"""
from pathlib import Path
import sys

from PySide6 import QtWidgets

from nda_enforcement.config import NDAConfig, default_app_data_dir
from nda_enforcement.crypto import sha256_file
from nda_enforcement.hooks import on_app_start
from nda_enforcement.pyside6_clickwrap import run_nda_clickwrap

BUILD_ID = "beta-1.0.0+2025-12-27"
NDA_VERSION = "NDA-HARDENED-2025-12-27"

NDA_PDF = Path("NDA_Hardened_Final_Tightened.pdf")
if not NDA_PDF.exists():
    # fallback if you stored it somewhere else
    NDA_PDF = Path(__file__).parent / "NDA_Hardened_Final_Tightened.pdf"

cfg = NDAConfig(
    build_id=BUILD_ID,
    nda_version=NDA_VERSION,
    nda_doc_sha256=sha256_file(NDA_PDF),
    app_data_dir=default_app_data_dir(),
)

def main():
    app = QtWidgets.QApplication(sys.argv)

    tester_id = "TESTER-1234"  # you can pass your own tester id here (license key, email hash, etc.)

    allowed, msg = on_app_start(cfg, tester_id)
    print("ENFORCEMENT:", msg)

    if not allowed:
        ok = run_nda_clickwrap(cfg, tester_id, nda_pdf_path=NDA_PDF)
        if not ok:
            print("Declined.")
            return 1

    allowed, msg = on_app_start(cfg, tester_id)
    print("ENFORCEMENT:", msg)
    if not allowed:
        print("Still blocked.")
        return 2

    # Launch your main window
    w = QtWidgets.QMainWindow()
    w.setWindowTitle("Advanced Tape Restorer (Demo)")
    w.resize(900, 600)
    w.show()

    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
