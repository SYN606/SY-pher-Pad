from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextOption, QWheelEvent
from PyQt6.QtWidgets import QPlainTextEdit


class EditorWidget(QPlainTextEdit):
    """An optimized plain text editor workspace featuring contextual zoom modifications."""

    def __init__(self) -> None:
        super().__init__()
        self.setPlaceholderText("Start typing...")
        self.setUndoRedoEnabled(True)
        self.setTabStopDistance(40)
        self.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)

        doc = self.document()
        assert doc is not None
        doc.setModified(False)

        self._zoom = 0
        self._min_zoom = -10
        self._max_zoom = 20

    def wheelEvent(self, e: QWheelEvent | None) -> None:
        """Intercepts system wheel ticks while holding Control modifiers to trigger view scalings."""
        if e is None:
            return

        if e.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = e.angleDelta().y()
            if delta > 0 and self._zoom < self._max_zoom:
                self.zoomIn()
                self._zoom += 1
            elif delta < 0 and self._zoom > self._min_zoom:
                self.zoomOut()
                self._zoom -= 1
            e.accept()
            return

        super().wheelEvent(e)
