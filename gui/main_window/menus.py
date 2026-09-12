from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtGui import QAction

if TYPE_CHECKING:
    from gui.main_window.window import MainWindow


class MenuBuilder:
    """Creates and wires all application menus."""

    def __init__(self, window: MainWindow) -> None:
        self.window = window

    def build(self) -> None:
        self._create_actions()
        self._create_menus()
        self._connect_actions()

    # Actions
    def _create_actions(self) -> None:
        w = self.window

        # File
        w.new_action = QAction("&New", w)
        w.new_action.setShortcut("Ctrl+N")
        w.open_action = QAction("&Open...", w)
        w.open_action.setShortcut("Ctrl+O")
        w.save_action = QAction("&Save", w)
        w.save_action.setShortcut("Ctrl+S")
        w.save_as_action = QAction("Save &As...", w)
        w.save_as_action.setShortcut("Ctrl+Shift+S")
        w.exit_action = QAction("E&xit", w)
        w.exit_action.setShortcut("Alt+F4")

        # Edit
        w.undo_action = QAction("&Undo", w)
        w.undo_action.setShortcut("Ctrl+Z")
        w.redo_action = QAction("&Redo", w)
        w.redo_action.setShortcut("Ctrl+Y")
        w.cut_action = QAction("Cu&t", w)
        w.cut_action.setShortcut("Ctrl+X")
        w.copy_action = QAction("&Copy", w)
        w.copy_action.setShortcut("Ctrl+C")
        w.paste_action = QAction("&Paste", w)
        w.paste_action.setShortcut("Ctrl+V")
        w.delete_action = QAction("&Delete", w)
        w.delete_action.setShortcut("Del")
        w.select_all_action = QAction("Select &All", w)
        w.select_all_action.setShortcut("Ctrl+A")
        w.find_action = QAction("&Find...", w)
        w.find_action.setShortcut("Ctrl+F")
        w.find_next_action = QAction("Find &Next", w)
        w.find_next_action.setShortcut("F3")
        w.find_prev_action = QAction("Find Pre&vious", w)
        w.find_prev_action.setShortcut("Shift+F3")
        w.replace_action = QAction("&Replace...", w)
        w.replace_action.setShortcut("Ctrl+H")
        w.goto_action = QAction("&Go To...", w)
        w.goto_action.setShortcut("Ctrl+G")
        w.time_date_action = QAction("Time/&Date", w)
        w.time_date_action.setShortcut("F5")

        # View
        w.word_wrap_action = QAction("&Word Wrap", w)
        w.word_wrap_action.setCheckable(True)
        w.zoom_in_action = QAction("Zoom &In", w)
        w.zoom_in_action.setShortcut("Ctrl+=")
        w.zoom_out_action = QAction("Zoom &Out", w)
        w.zoom_out_action.setShortcut("Ctrl+-")
        w.zoom_reset_action = QAction("Restore &Default Zoom", w)
        w.zoom_reset_action.setShortcut("Ctrl+0")
        w.status_bar_action = QAction("&Status Bar", w)
        w.status_bar_action.setCheckable(True)

        # Settings
        w.font_settings_action = QAction("&Font Settings...", w)
        w.font_settings_action.setShortcut("Ctrl+,")
        w.security_settings_action = QAction("&Security & System...", w)

        # Help
        w.about_action = QAction("&About SY-pherPad", w)

    # Menus
    def _create_menus(self) -> None:
        w = self.window
        menu_bar = w.menuBar()
        assert menu_bar is not None

        # File
        file_menu = menu_bar.addMenu("&File")
        assert file_menu is not None
        file_menu.addAction(w.new_action)
        file_menu.addAction(w.open_action)
        file_menu.addAction(w.save_action)
        file_menu.addAction(w.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(w.exit_action)

        # Edit
        edit_menu = menu_bar.addMenu("&Edit")
        assert edit_menu is not None
        edit_menu.addAction(w.undo_action)
        edit_menu.addAction(w.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(w.cut_action)
        edit_menu.addAction(w.copy_action)
        edit_menu.addAction(w.paste_action)
        edit_menu.addAction(w.delete_action)
        edit_menu.addSeparator()
        edit_menu.addAction(w.find_action)
        edit_menu.addAction(w.find_next_action)
        edit_menu.addAction(w.find_prev_action)
        edit_menu.addAction(w.replace_action)
        edit_menu.addAction(w.goto_action)
        edit_menu.addSeparator()
        edit_menu.addAction(w.select_all_action)
        edit_menu.addAction(w.time_date_action)

        # View
        view_menu = menu_bar.addMenu("&View")
        assert view_menu is not None
        view_menu.addAction(w.word_wrap_action)

        zoom_menu = view_menu.addMenu("&Zoom")
        assert zoom_menu is not None
        zoom_menu.addAction(w.zoom_in_action)
        zoom_menu.addAction(w.zoom_out_action)
        zoom_menu.addAction(w.zoom_reset_action)

        view_menu.addAction(w.status_bar_action)

        # Settings
        settings_menu = menu_bar.addMenu("&Settings")
        assert settings_menu is not None
        settings_menu.addAction(w.font_settings_action)
        settings_menu.addAction(w.security_settings_action)

        # Help
        help_menu = menu_bar.addMenu("&Help")
        assert help_menu is not None
        help_menu.addAction(w.about_action)

    # Connections
    def _connect_actions(self) -> None:
        w = self.window
        h = w.handlers

        # File
        w.new_action.triggered.connect(h.new_document)
        w.open_action.triggered.connect(h.open_document)
        w.save_action.triggered.connect(h.save_document)
        w.save_as_action.triggered.connect(h.save_document_as)
        w.exit_action.triggered.connect(w.close)

        # Edit
        w.undo_action.triggered.connect(w.editor.undo)
        w.redo_action.triggered.connect(w.editor.redo)
        w.cut_action.triggered.connect(w.editor.cut)
        w.copy_action.triggered.connect(w.editor.copy)
        w.paste_action.triggered.connect(w.editor.paste)
        w.delete_action.triggered.connect(lambda: w.editor.textCursor().removeSelectedText())
        w.select_all_action.triggered.connect(w.editor.selectAll)
        w.find_action.triggered.connect(h.show_find_dialog)
        w.find_next_action.triggered.connect(h.find_next)
        w.find_prev_action.triggered.connect(h.find_prev)
        w.replace_action.triggered.connect(h.show_replace_dialog)
        w.goto_action.triggered.connect(h.show_goto_dialog)
        w.time_date_action.triggered.connect(h.insert_date_time)

        # View
        w.word_wrap_action.toggled.connect(h.toggle_word_wrap)
        w.zoom_in_action.triggered.connect(w.editor.zoom_in)
        w.zoom_out_action.triggered.connect(w.editor.zoom_out)
        w.zoom_reset_action.triggered.connect(w.editor.reset_zoom)
        w.status_bar_action.toggled.connect(h.toggle_status_bar)

        # Settings
        w.font_settings_action.triggered.connect(
            lambda: h.show_settings_dialog(initial_tab=0))
        w.security_settings_action.triggered.connect(
            lambda: h.show_settings_dialog(initial_tab=1))

        # Help
        w.about_action.triggered.connect(h.show_about)

