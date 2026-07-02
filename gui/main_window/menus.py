from PyQt6.QtGui import QAction


class MenuBuilder:
    """Creates and wires all application menus."""

    def __init__(self, window):
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
        w.settings_action = QAction("&Settings...", w)
        w.settings_action.setShortcut("Ctrl+Alt+S")
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
        w.select_all_action = QAction("Select &All", w)
        w.select_all_action.setShortcut("Ctrl+A")
        w.find_action = QAction("&Find...", w)
        w.find_action.setShortcut("Ctrl+F")
        w.replace_action = QAction("&Replace...", w)
        w.replace_action.setShortcut("Ctrl+H")

        # Help
        w.about_action = QAction("&About", w)

    # Menus
    def _create_menus(self) -> None:
        w = self.window
        menu_bar = w.menuBar()
        # File
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(w.new_action)
        file_menu.addAction(w.open_action)
        file_menu.addSeparator()
        file_menu.addAction(w.save_action)
        file_menu.addAction(w.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(w.settings_action)
        file_menu.addSeparator()
        file_menu.addAction(w.exit_action)
        # Edit
        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(w.undo_action)
        edit_menu.addAction(w.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(w.cut_action)
        edit_menu.addAction(w.copy_action)
        edit_menu.addAction(w.paste_action)
        edit_menu.addSeparator()
        edit_menu.addAction(w.select_all_action)
        edit_menu.addSeparator()
        edit_menu.addAction(w.find_action)
        edit_menu.addAction(w.replace_action)
        # Help
        help_menu = menu_bar.addMenu("&Help")
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
        w.settings_action.triggered.connect(h.show_settings_dialog)
        w.exit_action.triggered.connect(w.close)
        # Editor
        w.undo_action.triggered.connect(w.editor.undo)
        w.redo_action.triggered.connect(w.editor.redo)
        w.cut_action.triggered.connect(w.editor.cut)
        w.copy_action.triggered.connect(w.editor.copy)
        w.paste_action.triggered.connect(w.editor.paste)
        w.select_all_action.triggered.connect(w.editor.selectAll)

        # Search
        w.find_action.triggered.connect(h.show_find_dialog)
        w.replace_action.triggered.connect(h.show_replace_dialog)

        # Help
        w.about_action.triggered.connect(h.show_about)
