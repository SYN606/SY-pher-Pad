from __future__ import annotations

from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QTextOption, QWheelEvent
from PyQt6.QtWidgets import QPlainTextEdit


class EditorWidget(QPlainTextEdit):
    """An optimized plain text editor workspace featuring contextual zoom modifications."""

    zoomChanged = pyqtSignal(int)
    fileDropped = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setPlaceholderText("Start typing...")
        self.setUndoRedoEnabled(True)
        self.setTabStopDistance(40)
        self.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.setAcceptDrops(True)

        doc = self.document()
        assert doc is not None
        doc.setModified(False)

        self._zoom = 0
        self._min_zoom = -8
        self._max_zoom = 20

    def get_zoom_percentage(self) -> int:
        """Returns zoom as an integer percentage."""
        return 100 + (self._zoom * 10)

    def _emit_zoom(self) -> None:
        self.zoomChanged.emit(self.get_zoom_percentage())

    def zoom_in(self) -> None:
        """Increases text scale."""
        if self._zoom < self._max_zoom:
            self.zoomIn(1)
            self._zoom += 1
            self._emit_zoom()

    def zoom_out(self) -> None:
        """Decreases text scale."""
        if self._zoom > self._min_zoom:
            self.zoomOut(1)
            self._zoom -= 1
            self._emit_zoom()

    def reset_zoom(self) -> None:
        """Restores default text scale (100%)."""
        if self._zoom > 0:
            self.zoomOut(self._zoom)
        elif self._zoom < 0:
            self.zoomIn(abs(self._zoom))
        self._zoom = 0
        self._emit_zoom()

    def set_word_wrap(self, enable: bool) -> None:
        """Toggles between word wrapped and horizontal-scrolling modes."""
        if enable:
            self.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
            self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        else:
            self.setWordWrapMode(QTextOption.WrapMode.NoWrap)
            self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

    def wheelEvent(self, e: QWheelEvent | None) -> None:
        """Intercepts system wheel ticks while holding Control modifiers to trigger view scalings."""
        if e is None:
            return

        if e.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = e.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            elif delta < 0:
                self.zoom_out()
            e.accept()
            return

        super().wheelEvent(e)

    def dragEnterEvent(self, e: QDragEnterEvent | None) -> None:
        """Accepts file drag actions into the editor window."""
        if e is not None and e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            super().dragEnterEvent(e)

    def dropEvent(self, e: QDropEvent | None) -> None:
        """Handles dropped document files by emitting their paths."""
        if e is not None and e.mimeData().hasUrls():
            urls = e.mimeData().urls()
            if urls:
                local_path = urls[0].toLocalFile()
                if local_path and Path(local_path).is_file():
                    e.acceptProposedAction()
                    self.fileDropped.emit(local_path)
                    return
        super().dropEvent(e)

