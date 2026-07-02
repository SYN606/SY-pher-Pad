from __future__ import annotations

from enum import Enum, auto
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)


class PasswordMode(Enum):
    """Differentiates authentication security contexts for specialized widget generation."""
    OPEN = auto()
    CREATE = auto()
    CHANGE = auto()


class PasswordDialog(QDialog):
    """A blocking application modal built to intercept, verify, and validate pass phrases."""

    def __init__(self,
                 mode: PasswordMode = PasswordMode.OPEN,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.mode = mode
        self.setWindowTitle("Password")
        self.setModal(True)
        self.setMinimumWidth(400)

        self.password_edit = QLineEdit()
        self.confirm_edit = QLineEdit()
        self.old_password_edit = QLineEdit()
        self.show_password = QCheckBox("Show password")

        self._build_ui()

    def _build_ui(self) -> None:
        """Generates conditional secure authentication layouts matching active tracking targets."""
        layout = QVBoxLayout(self)
        form = QFormLayout()

        if self.mode == PasswordMode.OPEN:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            form.addRow("Password:", self.password_edit)

        elif self.mode == PasswordMode.CREATE:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
            form.addRow("Password:", self.password_edit)
            form.addRow("Confirm:", self.confirm_edit)

        elif self.mode == PasswordMode.CHANGE:
            self.old_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
            form.addRow("Current:", self.old_password_edit)
            form.addRow("New:", self.password_edit)
            form.addRow("Confirm:", self.confirm_edit)

        layout.addLayout(form)

        self.show_password.toggled.connect(self._toggle_password_visibility)
        layout.addWidget(self.show_password)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                   | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if self.mode == PasswordMode.CHANGE:
            self.old_password_edit.setFocus()
        else:
            self.password_edit.setFocus()

    def _toggle_password_visibility(self, checked: bool) -> None:
        """Toggles masking behavior across target password display field collections."""
        mode = QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        for widget in self.findChildren(QLineEdit):
            widget.setEchoMode(mode)

    def _validate(self) -> None:
        """Enforces matching and entry validations prior to dismissing modal frames."""
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
            if self.password_edit.text() != self.confirm_edit.text():
                QMessageBox.warning(self, "Password Mismatch",
                                    "New passwords do not match.")
                return

        self.accept()

    def password(self) -> str:
        """Exposes the primary pass string payload extracted safely from internal widgets."""
        return self.password_edit.text()

    def old_password(self) -> str:
        """Exposes historical record string entries collected during updating operations."""
        return self.old_password_edit.text()
