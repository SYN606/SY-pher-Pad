from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QCloseEvent
from PyQt6.QtWidgets import QLabel, QMainWindow

from config.settings_manager import AppSettings
from editor.document import SecureDocument
from editor.editor_widget import EditorWidget
from editor.file_manager import FileManager
from .handlers import WindowHandlers
from .menus import MenuBuilder

if TYPE_CHECKING:
    from gui.dialogs.find_dialog import FindDialog


class MainWindow(QMainWindow):
    # Action type declarations
    new_action: QAction
    open_action: QAction
    save_action: QAction
    save_as_action: QAction
    exit_action: QAction

    undo_action: QAction
    redo_action: QAction
    cut_action: QAction
    copy_action: QAction
    paste_action: QAction
    delete_action: QAction
    select_all_action: QAction
    find_action: QAction
    find_next_action: QAction
    find_prev_action: QAction
    replace_action: QAction
    goto_action: QAction
    time_date_action: QAction

    word_wrap_action: QAction
    zoom_in_action: QAction
    zoom_out_action: QAction
    zoom_reset_action: QAction
    status_bar_action: QAction

    font_settings_action: QAction
    security_settings_action: QAction
    about_action: QAction

    def __init__(self) -> None:
        super().__init__()

        # Core components
        self.document = SecureDocument()
        self.file_manager = FileManager(self)

        # UI state
        self.find_dialog: FindDialog | None = None

        # Window setup
        self._setup_window()
        self._create_editor()

        # Business logic
        self.handlers = WindowHandlers(self)

        # Menus & Actions
        MenuBuilder(self).build()
        self._sync_menu_states()
        self._update_title()
        self._update_cursor_status()

    def _setup_window(self) -> None:
        """Configure the main application window and restore saved state."""
        self.setWindowTitle("SY-pherPad")

        # Restore window geometry & state
        geometry, size, pos = AppSettings.load_window_state()
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(size)
            if pos:
                self.move(pos)

        # Status Bar setup with Notepad-style live sections
        status_bar = self.statusBar()
        assert status_bar is not None
        self.status_bar = status_bar

        self.cursor_pos_label = QLabel("Ln 1, Col 1")
        self.cursor_pos_label.setMinimumWidth(100)
        self.cursor_pos_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.char_count_label = QLabel("0 chars")
        self.char_count_label.setMinimumWidth(100)
        self.char_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(60)
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.encoding_label = QLabel("UTF-8")
        self.encoding_label.setMinimumWidth(60)
        self.encoding_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_bar.addPermanentWidget(self.cursor_pos_label)
        self.status_bar.addPermanentWidget(self.char_count_label)
        self.status_bar.addPermanentWidget(self.zoom_label)
        self.status_bar.addPermanentWidget(self.encoding_label)

        status_bar_visible = AppSettings.load_status_bar_visible()
        self.status_bar.setVisible(status_bar_visible)
        self.status_bar.showMessage("Ready", 3000)

    def _create_editor(self) -> None:
        """Create, configure, and bind the central text editor."""
        self.editor = EditorWidget()
        self.setCentralWidget(self.editor)

        # Restore saved font
        font = AppSettings.load_editor_font()
        self.editor.setFont(font)

        # Restore word wrap
        word_wrap = AppSettings.load_word_wrap()
        self.editor.set_word_wrap(word_wrap)

        doc = self.editor.document()
        assert doc is not None
        doc.modificationChanged.connect(self._update_title)

        # Live status updates
        self.editor.cursorPositionChanged.connect(self._update_cursor_status)
        self.editor.textChanged.connect(self._update_cursor_status)
        self.editor.zoomChanged.connect(self._update_zoom_status)
        self.editor.fileDropped.connect(lambda path: self.handlers.open_file_path(path))

    def _sync_menu_states(self) -> None:
        """Synchronizes action checked states with active configuration."""
        word_wrap = AppSettings.load_word_wrap()
        self.word_wrap_action.setChecked(word_wrap)

        status_bar_visible = AppSettings.load_status_bar_visible()
        self.status_bar_action.setChecked(status_bar_visible)

    def _update_cursor_status(self) -> None:
        """Updates cursor coordinate and character counts on the status bar."""
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursor_pos_label.setText(f"Ln {line}, Col {col}")

        doc = self.editor.document()
        if doc is not None:
            chars = max(0, doc.characterCount() - 1)
            if cursor.hasSelection():
                sel_chars = len(cursor.selectedText())
                self.char_count_label.setText(f"{sel_chars} of {chars} chars")
            else:
                self.char_count_label.setText(f"{chars} chars")

    def _update_zoom_status(self, percentage: int) -> None:
        """Updates the zoom indicator on the status bar."""
        self.zoom_label.setText(f"{percentage}%")

    def _update_title(self) -> None:
        if self.document.file_path is None:
            title = "Untitled"
        else:
            title = Path(self.document.file_path).name
        doc = self.editor.document()
        assert doc is not None
        if doc.isModified():
            title = f"*{title}"
        self.setWindowTitle(f"{title} - SY-pherPad")

    def closeEvent(self, event: QCloseEvent | None) -> None:
        """Ensures unsaved modifications are confirmed and window layout is saved."""
        if not self.handlers.maybe_save():
            if event:
                event.ignore()
            return

        # Save window state for next launch
        AppSettings.save_window_state(self.saveGeometry(), self.size(), self.pos())
        if event:
            event.accept()