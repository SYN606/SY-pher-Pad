from __future__ import annotations

from PyQt6.QtCore import QSettings, QSize, QPoint
from PyQt6.QtGui import QFont


class AppSettings:
    """Manages platform-native configuration layouts across runtime application sessions."""

    ORGANIZATION = "SYN 606"
    APPLICATION = "SY-pherPad"

    @classmethod
    def get_settings(cls) -> QSettings:
        """Returns a platform-native, globally aware instance of QSettings."""
        return QSettings(cls.ORGANIZATION, cls.APPLICATION)

    @classmethod
    def save_window_state(cls, geometry: bytes, window_size: QSize, pos: QPoint) -> None:
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
        size = settings.value("window/size", QSize(1000, 700))
        pos = settings.value("window/position", None)
        return geometry, size, pos

    @classmethod
    def save_editor_font(cls, font: QFont) -> None:
        """Saves current text editor font properties."""
        settings = cls.get_settings()
        settings.setValue("editor/font_family", font.family())
        settings.setValue("editor/font_size", font.pointSize())
        settings.setValue("editor/font_bold", font.bold())
        settings.setValue("editor/font_italic", font.italic())

    @classmethod
    def load_editor_font(cls) -> QFont:
        """Loads saved font configuration, falling back to clean defaults."""
        settings = cls.get_settings()
        family = settings.value("editor/font_family", "Consolas", type=str)
        size = settings.value("editor/font_size", 12, type=int)
        bold = settings.value("editor/font_bold", False, type=bool)
        italic = settings.value("editor/font_italic", False, type=bool)
        font = QFont(family, size)
        font.setBold(bold)
        font.setItalic(italic)
        return font

    @classmethod
    def save_word_wrap(cls, enabled: bool) -> None:
        settings = cls.get_settings()
        settings.setValue("editor/word_wrap", enabled)

    @classmethod
    def load_word_wrap(cls) -> bool:
        settings = cls.get_settings()
        return settings.value("editor/word_wrap", True, type=bool)

    @classmethod
    def save_status_bar_visible(cls, visible: bool) -> None:
        settings = cls.get_settings()
        settings.setValue("view/status_bar", visible)

    @classmethod
    def load_status_bar_visible(cls) -> bool:
        settings = cls.get_settings()
        return settings.value("view/status_bar", True, type=bool)

