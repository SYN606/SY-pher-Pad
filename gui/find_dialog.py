from __future__ import annotations
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextDocument
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                             QWidget, QLabel, QLineEdit, QPushButton, 
                             QCheckBox, QRadioButton, QButtonGroup, QFormLayout)


class FindDialog(QDialog):
    find_requested = pyqtSignal(str, QTextDocument.FindFlag)
    replace_requested = pyqtSignal(str, str, QTextDocument.FindFlag)
    replace_all_requested = pyqtSignal(str, str, QTextDocument.FindFlag)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Find and Replace")
        self.setModal(False)  
        self.resize(450, 250)
        self._build_ui()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        # --- Find Tab ---
        find_tab = QWidget()
        find_layout = QFormLayout(find_tab)
        self.find_input = QLineEdit()
        find_layout.addRow("Find what:", self.find_input)
        # --- Replace Tab ---
        replace_tab = QWidget()
        replace_layout = QFormLayout(replace_tab)
        self.replace_find_input = QLineEdit()
        self.replace_input = QLineEdit()
        replace_layout.addRow("Find what:", self.replace_find_input)
        replace_layout.addRow("Replace with:", self.replace_input)
        self.tabs.addTab(find_tab, "Find")
        self.tabs.addTab(replace_tab, "Replace")
        main_layout.addWidget(self.tabs)
        # Synchronize the search terms across both tabs
        self.find_input.textChanged.connect(self.replace_find_input.setText)
        self.replace_find_input.textChanged.connect(self.find_input.setText)

        # 2. Setup Options Layout (Checkboxes)
        options_layout = QHBoxLayout()
        
        flags_layout = QVBoxLayout()
        self.match_case = QCheckBox("Match &case")
        self.whole_words = QCheckBox("Whole &words only")
        self.wrap_around = QCheckBox("Wrap around")
        self.wrap_around.setChecked(True)
        flags_layout.addWidget(self.match_case)
        flags_layout.addWidget(self.whole_words)
        flags_layout.addWidget(self.wrap_around)
        options_layout.addLayout(flags_layout)

        dir_widget = QWidget()
        dir_layout = QVBoxLayout(dir_widget)
        dir_layout.addWidget(QLabel("Direction:"))
        self.radio_down = QRadioButton("Down")
        self.radio_up = QRadioButton("Up")
        self.radio_down.setChecked(True)
        
        self.dir_group = QButtonGroup(self)
        self.dir_group.addButton(self.radio_down)
        self.dir_group.addButton(self.radio_up)
        
        dir_layout.addWidget(self.radio_down)
        dir_layout.addWidget(self.radio_up)
        options_layout.addWidget(dir_widget)
        
        main_layout.addLayout(options_layout)

        buttons_layout = QHBoxLayout()
        
        self.btn_find = QPushButton("Find &Next")
        self.btn_replace = QPushButton("&Replace")
        self.btn_replace_all = QPushButton("Replace &All")
        self.btn_cancel = QPushButton("Cancel")

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

    def _get_flags(self) -> QTextDocument.FindFlag:
        flags = QTextDocument.FindFlag(0)
        
        if self.match_case.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_words.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
        if self.radio_up.isChecked():
            flags |= QTextDocument.FindFlag.FindBackward
        return flags

    def _toggle_button_states(self, index: int) -> None:
        is_replace_mode = (index == 1)
        self.btn_replace.setVisible(is_replace_mode)
        self.btn_replace_all.setVisible(is_replace_mode)

    def _on_find(self) -> None:
        search_term = self.find_input.text()
        if search_term:
            self.find_requested.emit(search_term, self._get_flags())

    def _on_replace(self) -> None:
        search_term = self.replace_find_input.text()
        replace_term = self.replace_input.text()
        if search_term:
            self.replace_requested.emit(search_term, replace_term, self._get_flags())

    def _on_replace_all(self) -> None:
        search_term = self.replace_find_input.text()
        replace_term = self.replace_input.text()
        if search_term:
            self.replace_all_requested.emit(search_term, replace_term, self._get_flags())