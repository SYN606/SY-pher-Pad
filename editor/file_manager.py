from __future__ import annotations

from pathlib import Path
from PyQt6.QtWidgets import QFileDialog, QWidget


class FileManager:
    """Standardizes application native interface operations wrapping system dialog pipelines."""

    DEFAULT_EXTENSION = ".dnote"
    FILE_FILTER = "SY-pherPad Documents (*.dnote);;All Files (*)"

    def __init__(self, parent: QWidget | None = None) -> None:
        self.parent = parent

    def open_file(self) -> Path | None:
        """Spawns an interactive window overlay optimized to fetch target record files."""
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
        """Bypasses manual validation forks if pre-configured persistence hooks evaluate safely."""
        if current is not None:
            return current
        return self.save_file_as()

    def save_file_as(self) -> Path | None:
        """Determines export structural target details, enforcing explicit file extensions."""
        filename, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Save SY-pherPad Document",
            "",
            self.FILE_FILTER,
        )
        if not filename:
            return None

        path = Path(filename)
        if path.suffix.lower() != self.DEFAULT_EXTENSION:
            path = path.with_suffix(self.DEFAULT_EXTENSION)
        return path
