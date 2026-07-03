from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtGui import QTextCursor, QTextDocument
from PyQt6.QtWidgets import QMessageBox

from gui.dialogs.find_dialog import FindDialog
from gui.dialogs.password_dialog import PasswordDialog, PasswordMode
from gui.dialogs.settings_dialog import SettingsDialog

if TYPE_CHECKING:
    from gui.main_window.window import MainWindow


class WindowHandlers:
    """Handles all business logic and interface events for the MainWindow."""

    def __init__(self, window: MainWindow) -> None:
        self.window = window

    def _get_password_from_dialog(self, mode: PasswordMode) -> str | None:
        """Prompts the user with a password modal dialog based on the context mode."""
        dialog = PasswordDialog(mode=mode, parent=self.window)
        if mode == PasswordMode.OPEN:
            dialog.setWindowTitle("Open Encrypted Document")
        elif mode == PasswordMode.CREATE:
            dialog.setWindowTitle("Create Document Security Key")

        if dialog.exec() == PasswordDialog.DialogCode.Accepted:
            return dialog.password()
        return None

    def show_settings_dialog(self, initial_tab: int = 0) -> None:
        """Opens the Settings dialog and focuses on the requested tab index."""
        dialog = SettingsDialog(
            document=self.window.document,
            window=self.window,
            initial_tab=initial_tab,
            parent=self.window,
        )
        dialog.exec()

    def _init_find_dialog(self) -> FindDialog:
        """Ensures the FindDialog is safely singleton-instantiated and wired up."""
        if self.window.find_dialog is None:
            self.window.find_dialog = FindDialog(self.window)
            self.window.find_dialog.find_requested.connect(self._handle_find)
            self.window.find_dialog.replace_requested.connect(
                self._handle_replace)
            self.window.find_dialog.replace_all_requested.connect(
                self._handle_replace_all)
        return self.window.find_dialog

    def show_find_dialog(self) -> None:
        """Displays the text finding window pane with focus shifted to inputs."""
        dialog = self._init_find_dialog()
        dialog.tabs.setCurrentIndex(0)
        dialog.show()
        dialog.activateWindow()
        dialog.find_input.setFocus()

    def show_replace_dialog(self) -> None:
        """Displays the text replacement window pane with focus shifted to inputs."""
        dialog = self._init_find_dialog()
        dialog.tabs.setCurrentIndex(1)
        dialog.show()
        dialog.activateWindow()
        dialog.replace_find_input.setFocus()

    def _handle_find(self, text: str, flags: QTextDocument.FindFlag) -> bool:
        """Executes a plain text find operation with optional wrapping support."""
        cursor = self.window.editor.textCursor()
        if flags & QTextDocument.FindFlag.FindBackward:
            start_pos = cursor.selectionStart()
        else:
            start_pos = cursor.selectionEnd()

        found = self.window.editor.find(text, flags)
        if (not found and self.window.find_dialog
                and self.window.find_dialog.wrap_around.isChecked()):
            if flags & QTextDocument.FindFlag.FindBackward:
                self.window.editor.moveCursor(QTextCursor.MoveOperation.End)
            else:
                self.window.editor.moveCursor(QTextCursor.MoveOperation.Start)
            found = self.window.editor.find(text, flags)

        if not found:
            self.window.status_bar.showMessage(
                f"No matches found for: '{text}'", 3000)
        return found

    def _handle_replace(self, search_text: str, replace_text: str,
                        flags: QTextDocument.FindFlag) -> None:
        """Replaces the active matching text selection before hopping to the next choice."""
        cursor = self.window.editor.textCursor()
        if cursor.selectedText() == search_text:
            cursor.insertText(replace_text)
        self._handle_find(search_text, flags)

    def _handle_replace_all(self, search_text: str, replace_text: str,
                            flags: QTextDocument.FindFlag) -> None:
        """Iterates through the document completely to rewrite matching search queries."""
        self.window.editor.moveCursor(QTextCursor.MoveOperation.Start)
        count = 0
        cursor = self.window.editor.textCursor()
        document = self.window.editor.document()
        assert document is not None

        base_flags = flags
        if base_flags & QTextDocument.FindFlag.FindBackward:
            base_flags ^= QTextDocument.FindFlag.FindBackward

        cursor = document.find(search_text, cursor, base_flags)
        while not cursor.isNull():
            cursor.insertText(replace_text)
            count += 1
            cursor = document.find(search_text, cursor, base_flags)

        self.window.status_bar.showMessage(
            f"Successfully replaced {count} occurrence(s).", 3000)

    def new_document(self) -> None:
        """Wipes the text window space to process a clean, new plaintext structure securely."""
        self.window.editor.clear()
        if hasattr(self.window.document, "new"):
            self.window.document.new()
        document = self.window.editor.document()
        assert document is not None
        document.setModified(False)
        self.window._update_title()
        self.window.status_bar.showMessage("New document", 3000)

    def open_document(self) -> None:
        """Fires external target loading workflows, decoding cipher layers behind passes."""
        path = self.window.file_manager.open_file()
        if path is None:
            return
        password = self._get_password_from_dialog(PasswordMode.OPEN)
        if not password:
            self.window.status_bar.showMessage("Open operation cancelled",
                                               3000)
            return

        try:
            self.window.document.file_path = Path(path)
            decrypted_text = self.window.document.load_decrypted(password)
            self.window.editor.setPlainText(decrypted_text)
            document = self.window.editor.document()
            assert document is not None
            document.setModified(False)
            self.window._update_title()
            self.window.status_bar.showMessage(f"Opened {Path(path).name}",
                                               3000)

        except Exception as e:
            self.window.document.file_path = None
            self.window._update_title()
            QMessageBox.critical(self.window, "Open Failed",
                                 f"Could not decrypt file content:\n{str(e)}")

    def save_document(self) -> None:
        """Commits existing active text components to secure file targets using key salts."""
        if self.window.document.file_path is None:
            self.save_document_as()
            return
        password = self._get_password_from_dialog(PasswordMode.CREATE)

        if not password:
            self.window.status_bar.showMessage("Save operation cancelled",
                                               3000)
            return

        try:
            plain_text = self.window.editor.toPlainText()
            self.window.document.save_encrypted(plain_text, password)
            document = self.window.editor.document()
            assert document is not None
            document.setModified(False)
            self.window._update_title()
            self.window.status_bar.showMessage("Saved securely", 3000)

        except Exception as e:
            QMessageBox.critical(self.window, "Save Failed", str(e))

    def save_document_as(self) -> None:
        """Prompts user directory target parameters before processing encryption saves."""
        path = self.window.file_manager.save_file_as()
        if path is None:
            return
        self.window.document.file_path = Path(path)
        self.save_document()

    def show_about(self) -> None:
        """Triggers the HTML-styled application metadata distribution information box."""
        QMessageBox.about(
            self.window, "About SY-pherPad",
            ("<h2>SY-pherPad</h2>"
             "<p><b>Version:</b> 1.0.1</p>"
             "<p>Secure encrypted notepad.</p>"
             "<p><b>Developer:</b> SYN 606</p>"
             "<p><b>Source Code:</b><br>"
             '<a href="https://github.com/SYN606/SY-pher-Pad">'
             "HERE"
             "</a></p>"
             "<hr>"
             "<p>"
             "SY-pherPad is an open-source encrypted text editor designed "
             "for securely creating, editing, and storing encrypted notes."
             "</p>"))
