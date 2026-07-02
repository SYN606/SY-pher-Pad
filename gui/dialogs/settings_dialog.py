from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QMessageBox, QWidget
from gui.dialogs.password_dialog import PasswordDialog, PasswordMode
from editor.document import SecureDocument


class SettingsDialog(QDialog):

    def __init__(self,
                 document: SecureDocument,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.document = document
        self.setWindowTitle("Settings - SY-pherPad")
        self.setModal(True)
        self.resize(350, 150)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self.btn_change_password = QPushButton("Change Document Password...")
        self.btn_change_password.clicked.connect(self._on_change_password)
        layout.addWidget(self.btn_change_password)
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.accept)
        layout.addWidget(self.btn_close)
        if self.document.file_path is None:
            self.btn_change_password.setEnabled(False)
            self.btn_change_password.setToolTip(
                "You must save the file to disk before managing its password.")

    def _on_change_password(self) -> None:
        if not self.document.file_path or not self.document.file_path.exists():
            QMessageBox.warning(self, "Action Impossible",
                                "Active file must be saved on disk first.")
            return

        dialog = PasswordDialog(mode=PasswordMode.CHANGE, parent=self)
        dialog.setWindowTitle("Change Document Password")

        if dialog.exec() == PasswordDialog.DialogCode.Accepted:
            old_pwd = dialog.old_password()
            new_pwd = dialog.password()

            try:
                self.document.change_password(old_pwd, new_pwd)
                QMessageBox.information(
                    self, "Success",
                    "Document password updated and re-encrypted successfully!")
                self.accept()
            except ValueError:
                QMessageBox.critical(
                    self, "Authentication Failed",
                    "The current password you entered is incorrect.")
            except Exception as e:
                QMessageBox.critical(self, "Error",
                                     f"Failed to change password:\n{str(e)}")
