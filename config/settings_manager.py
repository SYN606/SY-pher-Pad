from __future__ import annotations

from PyQt6.QtCore import QSettings, QSize, QPoint
from PyQt6.QtGui import QFont


class AppSettings:
    """Manages platform-native configuration layouts across runtime application sessions."""

    @classmethod
    def get_settings(cls) -> QSettings:
        """Returns a platform-native, globally aware instance of QSettings."""
        # Simple instantiation reads the keys configured globally in main.py
        return QSettings()

    @classmethod
    def save_window_state(cls, geometry: bytes, window_size: QSize,
                          pos: QPoint) -> None:
        """Saves physical window boundaries and size metrics."""
        settings = cls.get_settings()
        settings.setValue("window/geometry", geometry)
        settings.setValue("window/size", window_size)
        settings.setValue("window/position", pos)

    @classmethod
    def load_window_state(cls) -> tuple[bytes | None, QSize, QPoint | None]:
        """Loads historical window boundaries, falling back to clean defaults."""
        settings = cls.get_settings()
        geometry = settings.value("window/geometry", None)
        size = settings.value("window/size", QSize(800, 600))
        pos = settings.value("window/position", None)
        return geometry, size, pos

    @classmethod
    def save_editor_font(cls, font: QFont) -> None:
        """Saves current text editor font properties."""
        settings = cls.get_settings()
        settings.setValue("editor/font_family", font.family())
        settings.setValue("editor/font_size", font.pointSize())

    @classmethod
    def load_editor_font(cls) -> QFont:
        """Loads saved font configuration, falling back to clean defaults."""
        settings = cls.get_settings()
        family = settings.value("editor/font_family", "Consolas")
        size = settings.value("editor/font_size", 12, type=int)
        return QFont(family, size)
