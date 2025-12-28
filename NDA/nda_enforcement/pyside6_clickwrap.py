"""
nda_enforcement.pyside6_clickwrap

Ready-to-drop PySide6 clickwrap dialog that:
- Displays the NDA PDF inside the app (QtPdf/QPdfView)
- Requires checkbox acceptance + user info
- Records acceptance via `record_acceptance()`

Usage (at app start):
    allowed, msg = on_app_start(cfg, tester_id)
    if not allowed:
        ok = run_nda_clickwrap(cfg, tester_id, nda_pdf_path="NDA_Hardened_Final_Tightened.pdf")
        if not ok:
            sys.exit(1)

Requires: PySide6 (with QtPdf + QtPdfWidgets available).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from PySide6 import QtCore, QtGui, QtWidgets

try:
    from PySide6.QtPdf import QPdfDocument
    from PySide6.QtPdfWidgets import QPdfView
    _HAS_QTPDF = True
except Exception:
    QPdfDocument = None  # type: ignore
    QPdfView = None      # type: ignore
    _HAS_QTPDF = False

from .acceptance_flow import record_acceptance
from .config import NDAConfig


@dataclass
class ClickwrapResult:
    accepted: bool
    message: str


class NDAClickwrapDialog(QtWidgets.QDialog):
    def __init__(
        self,
        cfg: NDAConfig,
        tester_id: str,
        nda_pdf_path: str | Path,
        parent: Optional[QtWidgets.QWidget] = None,
        window_title: str = "Beta NDA – Acceptance Required",
    ) -> None:
        super().__init__(parent)
        self.cfg = cfg
        self.tester_id = tester_id.strip() or "UNKNOWN"
        self.nda_pdf_path = Path(nda_pdf_path)

        self.setWindowTitle(window_title)
        self.setModal(True)
        self.resize(980, 720)

        root = QtWidgets.QVBoxLayout(self)

        # Header
        header = QtWidgets.QLabel(
            f"<b>Advanced Tape Restorer – Beta NDA</b><br>"
            f"Required NDA version: <code>{QtCore.Qt.escape(cfg.nda_version) if hasattr(QtCore.Qt,'escape') else cfg.nda_version}</code><br>"
            f"Build: <code>{cfg.build_id}</code>"
        )
        header.setWordWrap(True)
        root.addWidget(header)

        # Splitter: PDF viewer + right panel
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        root.addWidget(splitter, 1)

        # Left: PDF viewer (or fallback)
        left = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left)
        splitter.addWidget(left)

        if _HAS_QTPDF and self.nda_pdf_path.exists():
            self.pdf_doc = QPdfDocument(self)
            status = self.pdf_doc.load(str(self.nda_pdf_path))
            self.pdf_view = QPdfView()
            self.pdf_view.setDocument(self.pdf_doc)
            # reasonable defaults
            self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
            self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitInView)
            left_layout.addWidget(self.pdf_view, 1)

            if status != QPdfDocument.Status.Ready:
                warn = QtWidgets.QLabel(
                    "<b>Warning:</b> Could not load the NDA PDF inside the app. "
                    "You can still open it externally using the button on the right."
                )
                warn.setWordWrap(True)
                left_layout.addWidget(warn)
        else:
            self.pdf_doc = None
            self.pdf_view = None
            msg = (
                "Embedded PDF viewing is not available in this PySide6 build "
                "(QtPdf/QtPdfWidgets missing) or the NDA file was not found.\n\n"
                "Use the 'Open NDA PDF' button to view it in your default PDF viewer."
            )
            placeholder = QtWidgets.QTextEdit()
            placeholder.setReadOnly(True)
            placeholder.setPlainText(msg)
            left_layout.addWidget(placeholder, 1)

        # Right: identity + acceptance controls
        right = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        # Identity box
        form = QtWidgets.QFormLayout()
        right_layout.addLayout(form)

        self.name_edit = QtWidgets.QLineEdit()
        self.email_edit = QtWidgets.QLineEdit()
        self.email_edit.setPlaceholderText("name@example.com")

        self.tester_id_edit = QtWidgets.QLineEdit(self.tester_id)
        self.tester_id_edit.setReadOnly(True)

        form.addRow("Tester name *", self.name_edit)
        form.addRow("Tester email *", self.email_edit)
        form.addRow("Tester ID", self.tester_id_edit)

        # Buttons
        btn_row = QtWidgets.QHBoxLayout()
        right_layout.addLayout(btn_row)

        self.open_btn = QtWidgets.QPushButton("Open NDA PDF")
        self.open_btn.clicked.connect(self._open_external_pdf)
        btn_row.addWidget(self.open_btn)

        self.copy_ver_btn = QtWidgets.QPushButton("Copy version info")
        self.copy_ver_btn.clicked.connect(self._copy_version_info)
        btn_row.addWidget(self.copy_ver_btn)

        btn_row.addStretch(1)

        # Acceptance checkbox + small print
        self.accept_chk = QtWidgets.QCheckBox("I have read and agree to the NDA terms.")
        self.accept_chk.stateChanged.connect(self._update_accept_enabled)
        right_layout.addWidget(self.accept_chk)

        small = QtWidgets.QLabel(
            "By clicking <b>Accept</b>, you are providing a legally binding electronic signature "
            "and your acceptance will be recorded for this specific build and NDA version."
        )
        small.setWordWrap(True)
        right_layout.addWidget(small)

        right_layout.addStretch(1)

        # Footer buttons
        footer = QtWidgets.QHBoxLayout()
        right_layout.addLayout(footer)

        self.cancel_btn = QtWidgets.QPushButton("Decline")
        self.cancel_btn.clicked.connect(self.reject)
        footer.addWidget(self.cancel_btn)

        self.accept_btn = QtWidgets.QPushButton("Accept")
        self.accept_btn.setDefault(True)
        self.accept_btn.clicked.connect(self._accept)
        footer.addWidget(self.accept_btn)

        self.accept_btn.setEnabled(False)

        # live validation
        self.name_edit.textChanged.connect(self._update_accept_enabled)
        self.email_edit.textChanged.connect(self._update_accept_enabled)

        # keyboard escape should decline
        self.setWindowFlag(QtCore.Qt.WindowType.WindowContextHelpButtonHint, False)

    def _copy_version_info(self) -> None:
        text = (
            f"NDA version: {self.cfg.nda_version}\n"
            f"Build: {self.cfg.build_id}\n"
            f"NDA hash: {self.cfg.nda_doc_sha256}\n"
            f"NDA path: {self.nda_pdf_path}"
        )
        QtGui.QGuiApplication.clipboard().setText(text)
        QtWidgets.QMessageBox.information(self, "Copied", "Version info copied to clipboard.")

    def _open_external_pdf(self) -> None:
        if not self.nda_pdf_path.exists():
            QtWidgets.QMessageBox.warning(self, "Not found", f"NDA file not found:\n{self.nda_pdf_path}")
            return
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(self.nda_pdf_path)))

    def _valid_email(self, s: str) -> bool:
        s = s.strip()
        return ("@" in s) and ("." in s.split("@")[-1]) and (len(s) >= 6)

    def _update_accept_enabled(self) -> None:
        name_ok = len(self.name_edit.text().strip()) >= 2
        email_ok = self._valid_email(self.email_edit.text())
        chk_ok = self.accept_chk.isChecked()
        self.accept_btn.setEnabled(bool(name_ok and email_ok and chk_ok))

    def _accept(self) -> None:
        # final validation
        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        if len(name) < 2 or not self._valid_email(email) or not self.accept_chk.isChecked():
            QtWidgets.QMessageBox.warning(self, "Missing info", "Please enter name, email, and check the agreement box.")
            return

        # Record acceptance for THIS build/version/hash
        record_acceptance(
            self.cfg,
            tester_name=name,
            tester_email=email,
            tester_id=self.tester_id,
            acceptance_type="InApp",
            # You can optionally supply ip_address/device_fingerprint/extra here.
            extra={
                "ui": "PySide6Clickwrap",
                "nda_path": str(self.nda_pdf_path),
            },
        )
        self.accepted_name = name
        self.accepted_email = email
        self.accepted = True
        self.accept()

def run_nda_clickwrap(
    cfg: NDAConfig,
    tester_id: str,
    nda_pdf_path: str | Path,
    parent: Optional[QtWidgets.QWidget] = None,
) -> bool:
    """
    Convenience wrapper. Assumes a QApplication already exists.
    Returns True if accepted, False if declined.
    """
    dlg = NDAClickwrapDialog(cfg=cfg, tester_id=tester_id, nda_pdf_path=nda_pdf_path, parent=parent)
    return dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted
