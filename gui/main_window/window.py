from pathlib import Path

from PyQt6.QtWidgets import QMainWindow

from editor.document import SecureDocument
from editor.editor_widget import EditorWidget
from editor.file_manager import FileManager

from .handlers import WindowHandlers
from .menus import MenuBuilder


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()

        # Core components
        self.document = SecureDocument()
        self.file_manager = FileManager(self)

        # UI state
        self.find_dialog = None

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
        """Update the window title according to the current document."""

        if self.document.file_path is None:
            title = "Untitled"
        else:
            title = Path(self.document.file_path).name

        document = self.editor.document()
        assert document is not None

        if document.isModified():
            title = f"*{title}"

        self.setWindowTitle(f"{title} - SY-pherPad")
