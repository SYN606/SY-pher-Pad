from __future__ import annotations

import os
from pathlib import Path
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from gui.main_window.window import MainWindow
from editor.document import SecureDocument


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_mainwindow_initialization(qapp):
    window = MainWindow()
    assert window.windowTitle().endswith("SY-pherPad")
    assert window.editor is not None
    assert window.status_bar is not None
    assert window.cursor_pos_label.text() == "Ln 1, Col 1"
    window.close()


def test_mainwindow_save_and_reopen_in_place(qapp, tmp_path: Path):
    note_path = tmp_path / "inplace_test.dnote"

    window = MainWindow()
    window.document.file_path = note_path
    window.document.current_password = "session_secret_pass"
    window.editor.setPlainText("First line of notes\nSecond line of notes")
    window.editor.document().setModified(True)

    # In-place save
    saved = window.handlers.save_document()
    assert saved is True
    assert note_path.exists()
    assert not window.editor.document().isModified()
    assert window.document.file_path == note_path

    # Edit and in-place save again - MUST NOT change file path or prompt
    window.editor.appendPlainText("Modified line 3")
    assert window.editor.document().isModified()

    saved_again = window.handlers.save_document()
    assert saved_again is True
    assert not window.editor.document().isModified()

    # Verify content persisted
    doc = SecureDocument()
    doc.file_path = note_path
    assert doc.load_decrypted("session_secret_pass") == "First line of notes\nSecond line of notes\nModified line 3"
    
    window.editor.document().setModified(False)
    window.close()


def test_editor_features(qapp):
    window = MainWindow()
    # Test Word wrap toggle
    window.handlers.toggle_word_wrap(False)
    assert window.editor.lineWrapMode() == window.editor.LineWrapMode.NoWrap
    window.handlers.toggle_word_wrap(True)
    assert window.editor.lineWrapMode() == window.editor.LineWrapMode.WidgetWidth

    # Test Date/Time insertion
    initial_text = window.editor.toPlainText()
    window.handlers.insert_date_time()
    assert len(window.editor.toPlainText()) > len(initial_text)

    # Test Zoom
    initial_zoom = window.editor.get_zoom_percentage()
    window.editor.zoom_in()
    assert window.editor.get_zoom_percentage() > initial_zoom
    window.editor.reset_zoom()
    assert window.editor.get_zoom_percentage() == 100

    window.editor.document().setModified(False)
    window.close()


def test_open_file_path_logic(qapp, tmp_path: Path, monkeypatch):
    note_path = tmp_path / "cli_open.dnote"
    doc = SecureDocument()
    doc.file_path = note_path
    doc.save_encrypted("CLI opened document content", password="secret")

    window = MainWindow()

    # Mock dialog returning correct password
    monkeypatch.setattr(window.handlers, "_get_password_from_dialog", lambda mode, title=None: "secret")

    success = window.handlers.open_file_path(note_path)
    assert success is True
    assert window.editor.toPlainText() == "CLI opened document content"
    assert window.document.file_path == note_path
    assert window.document.current_password == "secret"
    assert not window.editor.document().isModified()

    window.close()


