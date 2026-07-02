from __future__ import annotations

import sys
from pathlib import Path
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from gui.main_window.window import MainWindow


def get_resource_path(relative_path: str) -> str:
    """Resolves an absolute file path context matching PyInstaller setups or raw files."""
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass is not None:
        base_path = Path(meipass)
    else:
        base_path = Path(__file__).resolve().parent
    return str(base_path / relative_path)


def main() -> None:
    """Application entry point initializing core settings and window event loops."""
    app = QApplication(sys.argv)

    # Register global metadata identities for automatic cross-platform QSettings persistence
    QCoreApplication.setOrganizationName("SYN 606")
    QCoreApplication.setApplicationName("SY-pherPad")
    QCoreApplication.setApplicationVersion("1.0")

    # Configure shared window context iconography
    app_icon = QIcon(get_resource_path("icons/app_icon.ico"))
    app.setWindowIcon(app_icon)
    window = MainWindow()
    window.setWindowIcon(app_icon)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
