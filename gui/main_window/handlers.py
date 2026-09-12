from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtGui import QTextCursor, QTextDocument
from PyQt6.QtWidgets import QInputDialog, QMessageBox

from config.settings_manager import AppSettings
from gui.dialogs.find_dialog import FindDialog
from gui.dialogs.password_dialog import PasswordDialog, PasswordMode
from gui.dialogs.settings_dialog import SettingsDialog

if TYPE_CHECKING:
    from gui.main_window.window import MainWindow


class WindowHandlers:
    """Handles all business logic, persistence workflows, and interface events for the MainWindow."""

    def __init__(self, window: MainWindow) -> None:
        self.window = window
        self._last_search_term = ""
        self._last_search_flags = QTextDocument.FindFlag(0)

    def _get_password_from_dialog(self, mode: PasswordMode, title: str | None = None) -> str | None:
        """Prompts the user with a password modal dialog based on the context mode."""
        dialog = PasswordDialog(mode=mode, parent=self.window)
        if title:
            dialog.setWindowTitle(title)
        elif mode == PasswordMode.OPEN:
            dialog.setWindowTitle("Open Encrypted Document")
        elif mode == PasswordMode.CREATE:
            dialog.setWindowTitle("Create Document Security Key")

        if dialog.exec() == PasswordDialog.DialogCode.Accepted:
            return dialog.password()
        return None

    def maybe_save(self) -> bool:
        """Checks for unsaved changes before destructive actions.

        Returns True if safe to proceed, False if cancelled by user.
        """
        doc = self.window.editor.document()
        if doc is None or not doc.isModified():
            return True

        filename = self.window.document.file_path.name if self.window.document.file_path else "Untitled"
        reply = QMessageBox.question(
            self.window,
            "SY-pherPad",
            f"Do you want to save changes to {filename}?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )

        if reply == QMessageBox.StandardButton.Save:
            return self.save_document()
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:  # Cancel
            return False

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
            self.window.find_dialog.replace_requested.connect(self._handle_replace)
            self.window.find_dialog.replace_all_requested.connect(self._handle_replace_all)
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
        self._last_search_term = text
        self._last_search_flags = flags

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
            self.window.status_bar.showMessage(f"No matches found for: '{text}'", 3000)
        return found

    def find_next(self) -> None:
        """Searches forward for the next occurrence of the active search query."""
        if self._last_search_term:
            flags = self._last_search_flags & ~QTextDocument.FindFlag.FindBackward
            self._handle_find(self._last_search_term, flags)
        else:
            self.show_find_dialog()

    def find_prev(self) -> None:
        """Searches backward for the previous occurrence of the active search query."""
        if self._last_search_term:
            flags = self._last_search_flags | QTextDocument.FindFlag.FindBackward
            self._handle_find(self._last_search_term, flags)
        else:
            self.show_find_dialog()

    def _handle_replace(self, search_text: str, replace_text: str,
                        flags: QTextDocument.FindFlag) -> None:
        """Replaces the active matching text selection before hopping to the next choice."""
        cursor = self.window.editor.textCursor()
        if cursor.selectedText() == search_text:
            cursor.insertText(replace_text)
        self._handle_find(search_text, flags)

    def _handle_replace_all(self, search_text: str, replace_text: str,
                            flags: QTextDocument.FindFlag) -> None:
        """Iterates through the document to replace all occurrences within an atomic edit block."""
        cursor = self.window.editor.textCursor()
        document = self.window.editor.document()
        assert document is not None

        base_flags = flags
        if base_flags & QTextDocument.FindFlag.FindBackward:
            base_flags ^= QTextDocument.FindFlag.FindBackward

        count = 0
        cursor.beginEditBlock()
        try:
            self.window.editor.moveCursor(QTextCursor.MoveOperation.Start)
            search_cursor = document.find(search_text, self.window.editor.textCursor(), base_flags)
            while not search_cursor.isNull():
                search_cursor.insertText(replace_text)
                count += 1
                search_cursor = document.find(search_text, search_cursor, base_flags)
        finally:
            cursor.endEditBlock()

        self.window.status_bar.showMessage(f"Successfully replaced {count} occurrence(s).", 3000)

    def new_document(self) -> None:
        """Cleans the workspace for a new document after ensuring unsaved changes are handled."""
        if not self.maybe_save():
            return

        self.window.editor.clear()
        self.window.document.new()
        doc = self.window.editor.document()
        assert doc is not None
        doc.setModified(False)
        self.window._update_title()
        self.window.status_bar.showMessage("New document", 3000)

    def open_document(self) -> None:
        """Spawns file selector dialog and processes document decryption."""
        if not self.maybe_save():
            return

        path = self.window.file_manager.open_file(
            default_dir=self.window.document.file_path.parent if self.window.document.file_path else None
        )
        if path is None:
            return

        self.open_file_path(path)

    def open_file_path(self, path: Path | str) -> bool:
        """Loads and decrypts a .dnote file directly from a given filesystem path."""
        target_path = Path(path).resolve()
        if not target_path.exists() or not target_path.is_file():
            QMessageBox.critical(self.window, "Open Failed", f"File does not exist:\n{target_path}")
            return False

        password = self._get_password_from_dialog(
            PasswordMode.OPEN,
            title=f"Open - {target_path.name}",
        )
        if not password:
            self.window.status_bar.showMessage("Open operation cancelled", 3000)
            return False

        try:
            self.window.document.file_path = target_path
            decrypted_text = self.window.document.load_decrypted(password)
            self.window.editor.setPlainText(decrypted_text)
            doc = self.window.editor.document()
            assert doc is not None
            doc.setModified(False)
            self.window._update_title()
            self.window.status_bar.showMessage(f"Opened {target_path.name}", 3000)
            return True

        except Exception as e:
            self.window.document.file_path = None
            self.window._update_title()
            QMessageBox.critical(
                self.window,
                "Open Failed",
                f"Could not decrypt {target_path.name}:\n{str(e)}",
            )
            return False

    def save_document(self) -> bool:
        """Saves current document in-place using current session key, or prompts Save As if untitled."""
        if self.window.document.file_path is None:
            return self.save_document_as()

        # If existing file but password is unknown in current session, ask user to verify
        if not self.window.document.current_password:
            password = self._get_password_from_dialog(
                PasswordMode.OPEN,
                title=f"Enter Password to Save - {self.window.document.file_path.name}",
            )
            if not password:
                self.window.status_bar.showMessage("Save operation cancelled", 3000)
                return False
            self.window.document.current_password = password

        try:
            plain_text = self.window.editor.toPlainText()
            self.window.document.save_encrypted(plain_text)
            doc = self.window.editor.document()
            assert doc is not None
            doc.setModified(False)
            self.window._update_title()
            self.window.status_bar.showMessage(f"Saved {self.window.document.file_path.name}", 3000)
            return True

        except Exception as e:
            QMessageBox.critical(self.window, "Save Failed", str(e))
            return False

    def save_document_as(self) -> bool:
        """Prompts for target file location and creates a new encrypted file."""
        current_path = self.window.document.file_path
        path = self.window.file_manager.save_file_as(current=current_path)
        if path is None:
            return False

        # If document has no password yet (new file), ask to create one
        password = self.window.document.current_password
        if not password:
            password = self._get_password_from_dialog(
                PasswordMode.CREATE,
                title=f"Set Security Key - {path.name}",
            )
            if not password:
                self.window.status_bar.showMessage("Save operation cancelled", 3000)
                return False

        try:
            self.window.document.file_path = Path(path)
            plain_text = self.window.editor.toPlainText()
            self.window.document.save_encrypted(plain_text, password)
            doc = self.window.editor.document()
            assert doc is not None
            doc.setModified(False)
            self.window._update_title()
            self.window.status_bar.showMessage(f"Saved as {path.name}", 3000)
            return True

        except Exception as e:
            QMessageBox.critical(self.window, "Save Failed", str(e))
            return False

    def insert_date_time(self) -> None:
        """Classic Notepad feature: inserts current date and time at cursor (F5)."""
        now = datetime.now().strftime("%I:%M %p %d-%m-%Y")
        self.window.editor.insertPlainText(now)

    def show_goto_dialog(self) -> None:
        """Prompts user for a line number and jumps cursor to that line (Ctrl+G)."""
        doc = self.window.editor.document()
        if doc is None:
            return
        total_lines = doc.blockCount()
        current_line = self.window.editor.textCursor().blockNumber() + 1

        line_num, ok = QInputDialog.getInt(
            self.window,
            "Go to Line",
            f"Line number (1 - {total_lines}):",
            current_line,
            1,
            total_lines,
            1,
        )
        if ok:
            block = doc.findBlockByLineNumber(line_num - 1)
            cursor = QTextCursor(block)
            self.window.editor.setTextCursor(cursor)

    def toggle_word_wrap(self, checked: bool) -> None:
        """Toggles word wrapping in the text editor."""
        self.window.editor.set_word_wrap(checked)
        AppSettings.save_word_wrap(checked)

    def toggle_status_bar(self, checked: bool) -> None:
        """Toggles visibility of the status bar."""
        self.window.status_bar.setVisible(checked)
        AppSettings.save_status_bar_visible(checked)

    def show_about(self) -> None:
        """Triggers the application information dialog."""
        QMessageBox.about(
            self.window,
            "About SY-pherPad",
            (
                "<h2>SY-pherPad</h2>"
                "<p><b>Version:</b> 1.1.0</p>"
                "<p>AES-256-GCM Encrypted Notepad for Windows.</p>"
                "<p><b>Developer:</b> SYN 606</p>"
                "<p><b>Source Code:</b><br>"
                '<a href="https://github.com/SYN606/SY-pher-Pad">GitHub Repository</a></p>'
                "<hr>"
                "<p>SY-pherPad provides lightweight, tamper-proof note taking "
                "with authenticated encryption and scrypt key derivation.</p>"
            ),
        )
