from __future__ import annotations
from enum import Enum, auto
from PyQt6.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox, QFormLayout,
                             QLineEdit, QMessageBox, QVBoxLayout)


class PasswordMode(Enum):
    OPEN = auto()
    CREATE = auto()
    CHANGE = auto()


class PasswordDialog(QDialog):

    def __init__(self,
                 mode: PasswordMode = PasswordMode.OPEN,
                 parent=None) -> None:
        super().__init__(parent)
        self.mode = mode
        self.setWindowTitle("Password")
        self.setModal(True)
        self.setMinimumWidth(400)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()

        if self.mode == PasswordMode.OPEN:
            self.password_edit = QLineEdit()
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            form.addRow("Password:", self.password_edit)

        elif self.mode == PasswordMode.CREATE:
            self.password_edit = QLineEdit()
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_edit = QLineEdit()
            self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
            form.addRow("Password:", self.password_edit)
            form.addRow("Confirm:", self.confirm_edit)

        elif self.mode == PasswordMode.CHANGE:
            self.old_password_edit = QLineEdit()
            self.old_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_edit = QLineEdit()
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_edit = QLineEdit()
            self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
            form.addRow("Current:", self.old_password_edit)
            form.addRow("New:", self.password_edit)
            form.addRow("Confirm:", self.confirm_edit)

        layout.addLayout(form)
        
        self.show_password = QCheckBox("Show password")
        self.show_password.toggled.connect(self._toggle_password_visibility)
        layout.addWidget(self.show_password)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                   | QDialogButtonBox.StandardButton.Cancel)

        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.password_edit.setFocus()

    def _toggle_password_visibility(self, checked: bool) -> None:
        mode = (QLineEdit.EchoMode.Normal
                if checked else QLineEdit.EchoMode.Password)
        for widget in self.findChildren(QLineEdit):
            widget.setEchoMode(mode)

    def _validate(self) -> None:
        if self.mode == PasswordMode.OPEN:
            if not self.password_edit.text():
                QMessageBox.warning(self, "Missing Password",
                                    "Please enter a password.")
                return

        elif self.mode == PasswordMode.CREATE:
            if not self.password_edit.text():
                QMessageBox.warning(self, "Missing Password",
                                    "Please enter a password.")
                return

            if self.password_edit.text() != self.confirm_edit.text():
                QMessageBox.warning(self, "Password Mismatch",
                                    "Passwords do not match.")
                return

        elif self.mode == PasswordMode.CHANGE:
            if (not self.old_password_edit.text()
                    or not self.password_edit.text()
                    or not self.confirm_edit.text()):
                QMessageBox.warning(self, "Missing Password",
                                    "Please complete every field.")
                return

            if (self.password_edit.text() != self.confirm_edit.text()):
                QMessageBox.warning(self, "Password Mismatch",
                                    "New passwords do not match.")
                return

        self.accept()

    def password(self) -> str:
        return self.password_edit.text()

    def old_password(self) -> str:
        if hasattr(self, "old_password_edit"):
            return self.old_password_edit.text()
        return ""