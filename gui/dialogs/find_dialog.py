from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QTextDocument
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class FindDialog(QDialog):
    """A non-modal overlay dialog facilitating text search and string replacement tasks."""

    find_requested = pyqtSignal(str, QTextDocument.FindFlag)
    replace_requested = pyqtSignal(str, str, QTextDocument.FindFlag)
    replace_all_requested = pyqtSignal(str, str, QTextDocument.FindFlag)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Find and Replace")
        self.setModal(False)
        self.resize(450, 250)

        self.tabs = QTabWidget()
        self.find_input = QLineEdit()
        self.replace_find_input = QLineEdit()
        self.replace_input = QLineEdit()
        self.match_case = QCheckBox("Match &case")
        self.whole_words = QCheckBox("Whole &words only")
        self.wrap_around = QCheckBox("Wrap around")
        self.radio_down = QRadioButton("Down")
        self.radio_up = QRadioButton("Up")
        self.dir_group = QButtonGroup(self)
        self.btn_find = QPushButton("Find &Next")
        self.btn_replace = QPushButton("&Replace")
        self.btn_replace_all = QPushButton("Replace &All")
        self.btn_cancel = QPushButton("Cancel")

        self._build_ui()

    def _build_ui(self) -> None:
        """Assembles internal widgets into the core structural window view layouts."""
        main_layout = QVBoxLayout(self)

        find_tab = QWidget()
        find_layout = QFormLayout(find_tab)
        find_layout.addRow("Find what:", self.find_input)

        replace_tab = QWidget()
        replace_layout = QFormLayout(replace_tab)
        replace_layout.addRow("Find what:", self.replace_find_input)
        replace_layout.addRow("Replace with:", self.replace_input)

        self.tabs.addTab(find_tab, "Find")
        self.tabs.addTab(replace_tab, "Replace")
        main_layout.addWidget(self.tabs)

        self.find_input.textChanged.connect(self._sync_find_to_replace)
        self.replace_find_input.textChanged.connect(self._sync_replace_to_find)

        options_layout = QHBoxLayout()
        flags_layout = QVBoxLayout()
        self.wrap_around.setChecked(True)
        flags_layout.addWidget(self.match_case)
        flags_layout.addWidget(self.whole_words)
        flags_layout.addWidget(self.wrap_around)
        options_layout.addLayout(flags_layout)

        dir_widget = QWidget()
        dir_layout = QVBoxLayout(dir_widget)
        dir_layout.addWidget(QLabel("Direction:"))
        self.radio_down.setChecked(True)

        self.dir_group.addButton(self.radio_down)
        self.dir_group.addButton(self.radio_up)
        dir_layout.addWidget(self.radio_down)
        dir_layout.addWidget(self.radio_up)
        options_layout.addWidget(dir_widget)

        main_layout.addLayout(options_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.btn_find)
        buttons_layout.addWidget(self.btn_replace)
        buttons_layout.addWidget(self.btn_replace_all)
        buttons_layout.addWidget(self.btn_cancel)
        main_layout.addLayout(buttons_layout)

        self.btn_find.clicked.connect(self._on_find)
        self.btn_replace.clicked.connect(self._on_replace)
        self.btn_replace_all.clicked.connect(self._on_replace_all)
        self.btn_cancel.clicked.connect(self.reject)

        self.tabs.currentChanged.connect(self._toggle_button_states)
        self._toggle_button_states(0)

    def _sync_find_to_replace(self, text: str) -> None:
        """Safely pushes search field string mutations down to the replace panel."""
        self.replace_find_input.blockSignals(True)
        self.replace_find_input.setText(text)
        self.replace_find_input.blockSignals(False)

    def _sync_replace_to_find(self, text: str) -> None:
        """Safely pushes replace query field mutations up into the primary search panel."""
        self.find_input.blockSignals(True)
        self.find_input.setText(text)
        self.find_input.blockSignals(False)

    def _get_flags(self) -> QTextDocument.FindFlag:
        """Evaluates active dialog criteria to generate correct text matching option flags."""
        flags = QTextDocument.FindFlag(0)
        if self.match_case.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_words.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
        if self.radio_up.isChecked():
            flags |= QTextDocument.FindFlag.FindBackward
        return flags

    def _toggle_button_states(self, index: int) -> None:
        """Enables or disables contextual mutation layout options depending on the active tab."""
        is_replace_mode = (index == 1)
        self.btn_replace.setEnabled(is_replace_mode)
        self.btn_replace_all.setEnabled(is_replace_mode)

    def _on_find(self) -> None:
        """Emits search lookup processing requests downstream to contextual handlers."""
        search_term = self.find_input.text()
        if search_term:
            self.find_requested.emit(search_term, self._get_flags())

    def _on_replace(self) -> None:
        """Emits isolated single-instance modification actions downstream to text layers."""
        search_term = self.replace_find_input.text()
        replace_term = self.replace_input.text()
        if search_term:
            self.replace_requested.emit(search_term, replace_term,
                                        self._get_flags())

    def _on_replace_all(self) -> None:
        """Emits absolute comprehensive substitution requests downstream to parsing layers."""
        search_term = self.replace_find_input.text()
        replace_term = self.replace_input.text()
        if search_term:
            self.replace_all_requested.emit(search_term, replace_term,
                                            self._get_flags())
