from pathlib import Path
from PyQt6.QtGui import QAction, QTextCursor, QTextDocument
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from editor.document import SecureDocument
from editor.editor_widget import EditorWidget
from editor.file_manager import FileManager
from gui.password_dialog import PasswordDialog, PasswordMode
from gui.find_dialog import FindDialog
from gui.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()

        self.document = SecureDocument()
        self.file_manager = FileManager(self)
        self.find_dialog: FindDialog | None = None

        self._setup_window()
        self._create_editor()
        self._create_actions()
        self._create_menu()
        self._connect_actions()
        self._update_title()

    def _setup_window(self) -> None:
        self.setWindowTitle("SY-pherPad")
        self.resize(1000, 700)

        status_bar = self.statusBar()
        assert status_bar is not None
        self.status_bar = status_bar

        self.status_bar.showMessage("Ready")

    def _create_editor(self) -> None:
        self.editor = EditorWidget()
        self.setCentralWidget(self.editor)

        document = self.editor.document()
        assert document is not None

        document.modificationChanged.connect(lambda _: self._update_title())

    def _create_actions(self) -> None:
        self.new_action = QAction("&New", self)
        self.new_action.setShortcut("Ctrl+N")

        self.open_action = QAction("&Open...", self)
        self.open_action.setShortcut("Ctrl+O")

        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut("Ctrl+S")

        self.save_as_action = QAction("Save &As...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")

        # --- Settings Action ---
        self.settings_action = QAction("&Settings...", self)
        self.settings_action.setShortcut("Ctrl+Alt+S")

        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut("Alt+F4")

        self.undo_action = QAction("&Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")

        self.redo_action = QAction("&Redo", self)
        self.redo_action.setShortcut("Ctrl+Y")

        self.cut_action = QAction("Cu&t", self)
        self.cut_action.setShortcut("Ctrl+X")

        self.copy_action = QAction("&Copy", self)
        self.copy_action.setShortcut("Ctrl+C")

        self.paste_action = QAction("&Paste", self)
        self.paste_action.setShortcut("Ctrl+V")

        self.select_all_action = QAction("Select &All", self)
        self.select_all_action.setShortcut("Ctrl+A")

        # --- Find and Replace Actions ---
        self.find_action = QAction("&Find...", self)
        self.find_action.setShortcut("Ctrl+F")

        self.replace_action = QAction("&Replace...", self)
        self.replace_action.setShortcut("Ctrl+H")

        self.about_action = QAction("&About", self)

    def _create_menu(self) -> None:
        menu_bar = self.menuBar()
        assert menu_bar is not None

        file_menu = menu_bar.addMenu("&File")
        assert file_menu is not None

        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.settings_action) 
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = menu_bar.addMenu("&Edit")
        assert edit_menu is not None

        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_action)
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.select_all_action)
        edit_menu.addSeparator()

        edit_menu.addAction(self.find_action)
        edit_menu.addAction(self.replace_action)

        help_menu = menu_bar.addMenu("&Help")
        assert help_menu is not None

        help_menu.addAction(self.about_action)

    def _connect_actions(self) -> None:
        self.new_action.triggered.connect(self.new_document)
        self.open_action.triggered.connect(self.open_document)
        self.save_action.triggered.connect(self.save_document)
        self.save_as_action.triggered.connect(self.save_document_as)
        self.settings_action.triggered.connect(
            self.show_settings_dialog) 
        self.exit_action.triggered.connect(self.close)

        self.undo_action.triggered.connect(self.editor.undo)
        self.redo_action.triggered.connect(self.editor.redo)
        self.cut_action.triggered.connect(self.editor.cut)
        self.copy_action.triggered.connect(self.editor.copy)
        self.paste_action.triggered.connect(self.editor.paste)
        self.select_all_action.triggered.connect(self.editor.selectAll)

        self.find_action.triggered.connect(self.show_find_dialog)
        self.replace_action.triggered.connect(self.show_replace_dialog)

        self.about_action.triggered.connect(self.show_about)

    def _update_title(self) -> None:
        path = getattr(self.document, "file_path", None)
        if path is None:
            title = "Untitled"
        else:
            title = Path(path).name

        document = self.editor.document()
        assert document is not None

        if document.isModified():
            title = f"*{title}"
        self.setWindowTitle(f"{title} - SY-pherPad")

    def _get_password_from_dialog(self, mode: PasswordMode) -> str | None:
        """Instantiates your custom PasswordDialog using the designated operational Mode."""
        dialog = PasswordDialog(mode=mode, parent=self)
        if mode == PasswordMode.OPEN:
            dialog.setWindowTitle("Open Encrypted Document")
        elif mode == PasswordMode.CREATE:
            dialog.setWindowTitle("Create Document Security Key")

        if dialog.exec() == PasswordDialog.DialogCode.Accepted:
            return dialog.password()
        return None

    def show_settings_dialog(self) -> None:
        dialog = SettingsDialog(self.document, self)
        dialog.exec()

    def _init_find_dialog(self) -> FindDialog:
        if self.find_dialog is None:
            self.find_dialog = FindDialog(self)
            self.find_dialog.find_requested.connect(self._handle_find)
            self.find_dialog.replace_requested.connect(self._handle_replace)
            self.find_dialog.replace_all_requested.connect(
                self._handle_replace_all)
        return self.find_dialog

    def show_find_dialog(self) -> None:
        dialog = self._init_find_dialog()
        dialog.tabs.setCurrentIndex(0)  # Jump to plain "Find" tab
        dialog.show()
        dialog.activateWindow()
        dialog.find_input.setFocus()

    def show_replace_dialog(self) -> None:
        dialog = self._init_find_dialog()
        dialog.tabs.setCurrentIndex(1)  # Jump to "Replace" tab
        dialog.show()
        dialog.activateWindow()
        dialog.replace_find_input.setFocus()

    def _handle_find(self, text: str, flags: QTextDocument.FindFlag) -> bool:
        """Searches the Editor text interface. Returns True if hit found."""
        cursor = self.editor.textCursor()

        if flags & QTextDocument.FindFlag.FindBackward:
            start_pos = cursor.selectionStart()
        else:
            start_pos = cursor.selectionEnd()

        found = self.editor.find(text, flags)

        if not found and self.find_dialog and self.find_dialog.wrap_around.isChecked(
        ):
            if flags & QTextDocument.FindFlag.FindBackward:
                self.editor.moveCursor(QTextCursor.MoveOperation.End)
            else:
                self.editor.moveCursor(QTextCursor.MoveOperation.Start)
            found = self.editor.find(text, flags)

        if not found:
            self.status_bar.showMessage(f"No matches found for: '{text}'",
                                        3000)
        return found

    def _handle_replace(self, search_text: str, replace_text: str,
                        flags: QTextDocument.FindFlag) -> None:
        cursor = self.editor.textCursor()

        if cursor.selectedText() == search_text:
            cursor.insertText(replace_text)

        self._handle_find(search_text, flags)

    def _handle_replace_all(self, search_text: str, replace_text: str,
                            flags: QTextDocument.FindFlag) -> None:
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)
        count = 0

        cursor = self.editor.textCursor()
        document = self.editor.document()
        assert document is not None

        base_flags = flags
        if base_flags & QTextDocument.FindFlag.FindBackward:
            base_flags ^= QTextDocument.FindFlag.FindBackward

        cursor = document.find(search_text, cursor, base_flags)

        while not cursor.isNull():
            cursor.insertText(replace_text)
            count += 1
            cursor = document.find(search_text, cursor, base_flags)

        self.status_bar.showMessage(
            f"Successfully replaced {count} occurrence(s).", 3000)

    # --- Document Handlers ---

    def new_document(self) -> None:
        self.editor.clear()
        if hasattr(self.document, "new"):
            self.document.new()

        document = self.editor.document()
        assert document is not None

        document.setModified(False)
        self._update_title()
        self.status_bar.showMessage("New document", 3000)

    def open_document(self) -> None:
        path = self.file_manager.open_file()
        if path is None:
            return

        password = self._get_password_from_dialog(PasswordMode.OPEN)
        if not password:
            self.status_bar.showMessage("Open operation cancelled", 3000)
            return

        try:
            self.document.file_path = Path(path)
            decrypted_text = self.document.load_decrypted(password)

            self.editor.setPlainText(decrypted_text)

            document = self.editor.document()
            assert document is not None
            document.setModified(False)

            self._update_title()
            self.status_bar.showMessage(f"Opened {path.name}", 3000)

        except Exception as e:
            self.document.file_path = None
            self._update_title()
            QMessageBox.critical(self, "Open Failed",
                                 f"Could not decrypt file content:\n{str(e)}")

    def save_document(self) -> None:
        if self.document.file_path is None:
            self.save_document_as()
            return

        password = self._get_password_from_dialog(PasswordMode.CREATE)
        if not password:
            self.status_bar.showMessage("Save operation cancelled", 3000)
            return

        try:
            plain_text = self.editor.toPlainText()
            self.document.save_encrypted(plain_text, password)

            document = self.editor.document()
            assert document is not None
            document.setModified(False)

            self._update_title()
            self.status_bar.showMessage("Saved securely", 3000)

        except Exception as e:
            QMessageBox.critical(self, "Save Failed", str(e))

    def save_document_as(self) -> None:
        path = self.file_manager.save_file_as()
        if path is None:
            return

        self.document.file_path = Path(path)
        self.save_document()

    def show_about(self) -> None:
        QMessageBox.about(self, "About SY-pherPad",
                          ("<h2>SY-pherPad</h2>"
                           "<p>Secure encrypted notepad.</p>"
                           "<p>Developed by SYN 606.</p>"
                           "<p>Version 1.0</p>"))
