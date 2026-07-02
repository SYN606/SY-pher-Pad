import sys
from pathlib import Path
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow


def get_resource_path(relative_path: str) -> str:
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass is not None:
        base_path = Path(meipass)
    else:
        base_path = Path(__file__).resolve().parent
    return str(base_path / relative_path)


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("SY-pherPad")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("SYN 606")
    # Application icon
    app.setWindowIcon(QIcon(get_resource_path("icons/app_icon.ico")))
    window = MainWindow()
    # Window icon (optional but recommended)
    window.setWindowIcon(QIcon(get_resource_path("icons/app_icon.ico")))
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
