from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QAction  # Added for type hints

from editor.document import SecureDocument
from editor.editor_widget import EditorWidget
from editor.file_manager import FileManager
from .handlers import WindowHandlers
from .menus import MenuBuilder

if TYPE_CHECKING:
    from gui.dialogs.find_dialog import FindDialog


class MainWindow(QMainWindow):
    # Explicitly declare the actions so Pylance knows they exist on this class
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
    select_all_action: QAction
    find_action: QAction
    replace_action: QAction
    
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
        self._update_title()

    def _setup_window(self) -> None:
        """Configure the main application window."""
        self.setWindowTitle("SY-pherPad")
        self.resize(1000, 700)
        status_bar = self.statusBar()
        assert status_bar is not None
        self.status_bar = status_bar
        self.status_bar.showMessage("Ready")

    def _create_editor(self) -> None:
        """Create and configure the central text editor."""
        self.editor = EditorWidget()
        self.setCentralWidget(self.editor)
        document = self.editor.document()
        assert document is not None
        document.modificationChanged.connect(self._update_title)

    def _update_title(self) -> None:
        if self.document.file_path is None:
            title = "Untitled"
        else:
            title = Path(self.document.file_path).name
        document = self.editor.document()
        assert document is not None
        if document.isModified():
            title = f"*{title}"
        self.setWindowTitle(f"{title} - SY-pherPad")