from __future__ import annotations
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog, QWidget


class FileManager:
    DEFAULT_EXTENSION = ".dnote"
    FILE_FILTER = ("SY-pherPad Documents (*.dnote);;"
                   "All Files (*)")

    def __init__(self, parent: QWidget | None = None) -> None:
        self.parent = parent

    def open_file(self) -> Path | None:
        filename, _ = QFileDialog.getOpenFileName(
            self.parent,
            "Open SY-pherPad Document",
            "",
            self.FILE_FILTER,
        )
        if not filename:
            return None
        return Path(filename)

    def save_file(self, current: Path | None = None) -> Path | None:
        if current is not None:
            return current
        return self.save_file_as()

    def save_file_as(self) -> Path | None:
        filename, _ = QFileDialog.getSaveFileName(self.parent,
                                                  "Save SY-pherPad Document",
                                                  "", self.FILE_FILTER)

        if not filename:
            return None

        path = Path(filename)
        if path.suffix.lower() != self.DEFAULT_EXTENSION:
            path = path.with_suffix(self.DEFAULT_EXTENSION)
        return path
