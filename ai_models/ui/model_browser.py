import os

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QMessageBox,
    QComboBox,
)
from PySide6.QtCore import Qt

from ..model_manager import ModelManager, ModelEntry


class ModelBrowserDialog(QDialog):
    def __init__(self, model_manager: ModelManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Model Browser")
        self.resize(900, 500)

        self.mm = model_manager
        self.current_engine_filter = None

        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Engine filter:"))
        self.engine_combo = QComboBox()
        self.engine_combo.addItem("All", userData=None)

        engines = sorted({m.engine for m in self.mm.list_models()})
        for e in engines:
            self.engine_combo.addItem(e, userData=e)

        self.engine_combo.currentIndexChanged.connect(self._on_engine_changed)
        filter_layout.addWidget(self.engine_combo)
        filter_layout.addStretch(1)
        layout.addLayout(filter_layout)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Engine", "Name", "Version", "License", "Status", "Non-Commercial"]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.btn_download = QPushButton("Download Selected")
        self.btn_download.clicked.connect(self._download_selected)
        self.btn_rescan = QPushButton("Rescan/Refresh")
        self.btn_rescan.clicked.connect(self._populate_table)

        btn_layout.addWidget(self.btn_download)
        btn_layout.addWidget(self.btn_rescan)
        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)

        self._populate_table()

    def _on_engine_changed(self, idx: int):
        engine = self.engine_combo.currentData()
        self.current_engine_filter = engine
        self._populate_table()

    def _get_models_for_view(self) -> list[ModelEntry]:
        return self.mm.list_models(engine=self.current_engine_filter)

    def _populate_table(self):
        models = self._get_models_for_view()
        self.table.setRowCount(len(models))
        for row, m in enumerate(models):
            self._set_row(row, m)
        self.table.resizeColumnsToContents()

    def _set_row(self, row: int, m: ModelEntry):
        all_present = True
        some_present = False
        for mf in m.files:
            abs_path = os.path.join(self.mm.model_root, mf.path)
            if os.path.isfile(abs_path):
                some_present = True
            else:
                all_present = False

        if not m.files:
            status = "N/A (external/manual)"
        elif all_present:
            status = "Installed"
        elif some_present:
            status = "Partial"
        else:
            status = "Not installed"

        items = [
            QTableWidgetItem(m.id),
            QTableWidgetItem(m.engine),
            QTableWidgetItem(m.friendly_name),
            QTableWidgetItem(m.version),
            QTableWidgetItem(m.license),
            QTableWidgetItem(status),
            QTableWidgetItem("Yes" if m.non_commercial else "No"),
        ]

        for col, it in enumerate(items):
            it.setData(Qt.UserRole, m.id)
            if m.non_commercial and self.mm.commercial_mode:
                it.setForeground(Qt.red)
            self.table.setItem(row, col, it)

    def _get_selected_model_ids(self) -> list[str]:
        rows = self.table.selectionModel().selectedRows()
        ids = set()
        for idx in rows:
            it = self.table.item(idx.row(), 0)
            if it:
                ids.add(it.text())
        return list(ids)

    def _download_selected(self):
        ids = self._get_selected_model_ids()
        if not ids:
            QMessageBox.information(
                self, "No selection", "Please select one or more models."
            )
            return

        for model_id in ids:
            try:
                self.mm.ensure_model_available(model_id, auto_download=True)
            except PermissionError as e:
                QMessageBox.warning(self, "License restriction", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Download error", f"{model_id}: {e}")

        self._populate_table()
