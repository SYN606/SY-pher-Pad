from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFontComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from config.settings_manager import AppSettings
from config.file_association import register_file_association, is_file_associated
from editor.document import SecureDocument
from gui.dialogs.password_dialog import PasswordDialog, PasswordMode

if TYPE_CHECKING:
    from gui.main_window.window import MainWindow


class SettingsDialog(QDialog):

    def __init__(
        self,
        document: SecureDocument,
        window: MainWindow,
        initial_tab: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.document = document
        self.main_window = window

        self.setWindowTitle("Settings - SY-pherPad")
        self.resize(500, 420)
        self.setModal(True)

        self._build_ui()
        self._load_font_settings()

        # Open the requested tab
        self.tabs.setCurrentIndex(initial_tab)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        self.tabs = QTabWidget()

        # ==============================================================
        # Font Tab
        # ==============================================================

        font_tab = QWidget()
        font_layout = QVBoxLayout(font_tab)

        appearance = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance)

        self.font_family = QFontComboBox()

        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)

        self.bold = QCheckBox("Bold")
        self.italic = QCheckBox("Italic")

        self.preview = QLabel("The quick brown fox jumps over the lazy dog.")
        self.preview.setMinimumHeight(60)
        self.preview.setWordWrap(True)

        appearance_layout.addRow("Font", self.font_family)
        appearance_layout.addRow("Size", self.font_size)
        appearance_layout.addRow("", self.bold)
        appearance_layout.addRow("", self.italic)
        appearance_layout.addRow("Preview", self.preview)

        font_layout.addWidget(appearance)
        font_layout.addStretch()

        self.tabs.addTab(font_tab, "Font")

        # ==============================================================
        # Security & System Tab
        # ==============================================================

        security_tab = QWidget()
        security_layout = QVBoxLayout(security_tab)

        security_group = QGroupBox("Security")
        group_layout = QVBoxLayout(security_group)

        self.btn_change_password = QPushButton("Change Document Password...")
        self.btn_change_password.clicked.connect(self._on_change_password)

        if self.document.file_path is None:
            self.btn_change_password.setEnabled(False)
            self.btn_change_password.setToolTip(
                "Save the document before changing its password.")

        group_layout.addWidget(self.btn_change_password)
        security_layout.addWidget(security_group)

        # File Association Group
        assoc_group = QGroupBox("System Integration")
        assoc_layout = QVBoxLayout(assoc_group)

        assoc_info = QLabel("Register SY-pherPad to open .dnote files on right-click or double-click.")
        assoc_info.setWordWrap(True)
        assoc_layout.addWidget(assoc_info)

        self.btn_associate = QPushButton("Associate .dnote files with SY-pherPad")
        self.btn_associate.clicked.connect(self._on_associate_files)
        if is_file_associated():
            self.btn_associate.setText("✓ .dnote files are already associated")
            self.btn_associate.setEnabled(False)

        assoc_layout.addWidget(self.btn_associate)
        security_layout.addWidget(assoc_group)
        security_layout.addStretch()

        self.tabs.addTab(security_tab, "Security & System")

        main_layout.addWidget(self.tabs)

        # ==============================================================
        # Buttons
        # ==============================================================

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Apply
                                   | QDialogButtonBox.StandardButton.Ok
                                   | QDialogButtonBox.StandardButton.Cancel)

        apply_button = buttons.button(QDialogButtonBox.StandardButton.Apply)

        assert apply_button is not None

        apply_button.clicked.connect(self.apply_font_settings)

        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        main_layout.addWidget(buttons)

        # Live Preview

        self.font_family.currentFontChanged.connect(self._update_preview)

        self.font_size.valueChanged.connect(self._update_preview)

        self.bold.toggled.connect(self._update_preview)

        self.italic.toggled.connect(self._update_preview)

    # ------------------------------------------------------------------
    # Font Settings
    # ------------------------------------------------------------------

    def _load_font_settings(self) -> None:
        font = AppSettings.load_editor_font()
        self.font_family.setCurrentFont(font)
        self.font_size.setValue(font.pointSize())
        self.bold.setChecked(font.bold())
        self.italic.setChecked(font.italic())
        self._update_preview()

    def _current_font(self) -> QFont:
        font = self.font_family.currentFont()
        font.setPointSize(self.font_size.value())
        font.setBold(self.bold.isChecked())
        font.setItalic(self.italic.isChecked())
        return font

    def _update_preview(self) -> None:
        self.preview.setFont(self._current_font())

    def apply_font_settings(self) -> None:
        font = self._current_font()
        self.main_window.editor.setFont(font)
        AppSettings.save_editor_font(font)

    def _accept(self) -> None:
        self.apply_font_settings()
        self.accept()

    # ------------------------------------------------------------------
    # System Integration
    # ------------------------------------------------------------------

    def _on_associate_files(self) -> None:
        success = register_file_association()
        if success:
            self.btn_associate.setText("✓ .dnote files associated successfully!")
            self.btn_associate.setEnabled(False)
            QMessageBox.information(
                self,
                "File Association",
                "SY-pherPad is now registered for .dnote files.\n"
                "You can now double-click or right-click any .dnote file to open it in SY-pherPad.",
            )
        else:
            QMessageBox.warning(
                self,
                "File Association Failed",
                "Could not register file association in Windows Registry.",
            )

    # ------------------------------------------------------------------
    # Password
    # ------------------------------------------------------------------

    def _on_change_password(self) -> None:
        if (self.document.file_path is None
                or not self.document.file_path.exists()):
            QMessageBox.warning(
                self,
                "Action Impossible",
                "Save the document before changing its password.",
            )
            return

        dialog = PasswordDialog(
            mode=PasswordMode.CHANGE,
            parent=self,
        )
        dialog.setWindowTitle("Change Document Password")

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            current_text = self.main_window.editor.toPlainText()
            self.document.change_password(
                dialog.old_password(),
                dialog.password(),
                current_text=current_text,
            )
            doc = self.main_window.editor.document()
            if doc is not None:
                doc.setModified(False)
            self.main_window._update_title()

            QMessageBox.information(
                self,
                "Success",
                "Document password updated successfully.",
            )

        except ValueError:
            QMessageBox.critical(
                self,
                "Authentication Failed",
                "The current password is incorrect.",
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to change password:\n{e}",
            )

