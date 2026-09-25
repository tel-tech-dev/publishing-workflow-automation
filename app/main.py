"""Desktop orchestrator for the publishing automation workflow.

This is a cleaned public version of the production PySide2 launcher. It
starts worker modules as independent Python processes and streams their
output into the GUI.
"""
from __future__ import annotations

import sys
from pathlib import Path
from PySide2.QtCore import QProcess
from PySide2.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QLabel, QPushButton, QPlainTextEdit, QMessageBox, QGroupBox,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from common.config import WORKSPACE_DIR

SECTIONS = ["Sport", "Powiat", "Naklo", "Szubin", "Kcynia", "Mrocza", "Sadki", "Rolnicze", "Policja"]


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Publishing Workflow Automation")
        self.resize(1050, 650)
        self.process: QProcess | None = None
        self.issue = QLineEdit()
        self.url = QLineEdit()
        self.section_counts = {name: QLineEdit() for name in SECTIONS}
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        top = QGridLayout()
        top.addWidget(QLabel("Issue number:"), 0, 0)
        top.addWidget(self.issue, 0, 1)
        top.addWidget(QLabel("Article URL (single mode):"), 1, 0)
        top.addWidget(self.url, 1, 1, 1, 5)
        for idx, name in enumerate(SECTIONS):
            row = 2 + idx // 3
            col = (idx % 3) * 2
            top.addWidget(QLabel(name + ":"), row, col)
            top.addWidget(self.section_counts[name], row, col + 1)
        root.addLayout(top)

        workers = QGroupBox("Workflow")
        grid = QGridLayout(workers)
        buttons = [
            ("Batch scrape", lambda: self.run_script("scrapers/article_scraper.py", [self.issue.text().strip()])),
            ("Continuation scrape", self.run_continuation),
            ("Create issue folder", lambda: self.run_script("spreadsheets/create_issue_folder.py", [self.issue.text().strip()])),
            ("Fill spreadsheets", lambda: self.run_script("spreadsheets/fill_schedules.py", [self.issue.text().strip()])),
            ("Collect source photos", lambda: self.run_script("images/collect_source_photos.py", [self.issue.text().strip()])),
            ("Prepare photos", lambda: self.run_script("images/prepare_photos_for_processing.py", [self.issue.text().strip()])),
            ("Restore processed photos", lambda: self.run_script("images/restore_processed_photos.py", [])),
            ("Rename photos", lambda: self.run_script("images/rename_photos.py", [])),
            ("ODT -> RTF", self.run_odt),
            ("RTF check", self.run_rtf_check),
        ]
        for i, (label, callback) in enumerate(buttons):
            button = QPushButton(label)
            button.clicked.connect(callback)
            grid.addWidget(button, i // 3, i % 3)
        root.addWidget(workers)
        root.addWidget(self.log, 1)

    def run_continuation(self) -> None:
        args = [self.issue.text().strip()] + [self.section_counts[name].text().strip() for name in SECTIONS]
        self.run_script("scrapers/article_scraper_continuation.py", args)

    def run_odt(self) -> None:
        issue = self.issue.text().strip()
        if not issue:
            QMessageBox.warning(self, "Missing issue", "Enter an issue number first.")
            return
        folder = WORKSPACE_DIR / issue
        self.run_script("documents/odt_to_rtf.py", ["--input-folder", str(folder)])

    def run_rtf_check(self) -> None:
        issue = self.issue.text().strip()
        if not issue:
            QMessageBox.warning(self, "Missing issue", "Enter an issue number first.")
            return
        folder = WORKSPACE_DIR / issue / "final"
        self.run_script("documents/rtf_check.py", [str(folder)])

    def run_script(self, relative_script: str, args: list[str]) -> None:
        if self.process and self.process.state() != QProcess.NotRunning:
            QMessageBox.warning(self, "Busy", "Another worker is already running.")
            return
        if any(arg == "" for arg in args[:1]) and relative_script not in {"images/restore_processed_photos.py", "images/rename_photos.py"}:
            QMessageBox.warning(self, "Missing issue", "Enter an issue number first.")
            return
        script = PROJECT_ROOT / relative_script
        if not script.exists():
            QMessageBox.critical(self, "Missing worker", str(script))
            return
        self.process = QProcess(self)
        self.process.setWorkingDirectory(str(PROJECT_ROOT))
        self.process.readyReadStandardOutput.connect(self._stdout)
        self.process.readyReadStandardError.connect(self._stderr)
        self.process.finished.connect(self._finished)
        self.log.appendPlainText(f"> {relative_script} {' '.join(args)}")
        self.process.start(sys.executable, [str(script), *args])

    def _stdout(self) -> None:
        if self.process:
            self.log.appendPlainText(bytes(self.process.readAllStandardOutput()).decode("utf-8", "replace").rstrip())

    def _stderr(self) -> None:
        if self.process:
            self.log.appendPlainText(bytes(self.process.readAllStandardError()).decode("utf-8", "replace").rstrip())

    def _finished(self) -> None:
        self.log.appendPlainText("Worker finished.\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
