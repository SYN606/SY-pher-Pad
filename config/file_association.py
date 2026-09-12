from __future__ import annotations

import ctypes
import sys
import winreg
from pathlib import Path

PROGID = "SY-pherPad.dnote"
EXTENSION = ".dnote"
DESCRIPTION = "SY-pherPad Encrypted Document"


def get_launch_command() -> str:
    """Returns the executable command line string for opening files."""
    if getattr(sys, "frozen", False):
        exe_path = sys.executable
        return f'"{exe_path}" "%1"'
    else:
        python_exe = sys.executable
        main_py = Path(__file__).resolve().parent.parent / "main.py"
        return f'"{python_exe}" "{main_py}" "%1"'


def get_icon_path() -> str:
    """Returns path to the application icon."""
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass is not None:
        base = Path(meipass)
    else:
        base = Path(__file__).resolve().parent.parent
    icon_file = base / "icons" / "app_icon.ico"
    return str(icon_file)


def is_file_associated() -> bool:
    """Checks if .dnote is currently registered to SY-pherPad in HKCU."""
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            f"Software\\Classes\\{EXTENSION}",
            0,
            winreg.KEY_READ,
        ) as key:
            val, _ = winreg.QueryValueEx(key, "")
            return val == PROGID
    except OSError:
        return False


def register_file_association() -> bool:
    """Registers .dnote extension under HKCU\\Software\\Classes (no admin rights needed)."""
    try:
        # 1. Map .dnote -> ProgID
        with winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            f"Software\\Classes\\{EXTENSION}",
        ) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, PROGID)

        # 2. Configure ProgID description
        with winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            f"Software\\Classes\\{PROGID}",
        ) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, DESCRIPTION)

        # 3. Configure DefaultIcon
        icon_path = get_icon_path()
        if Path(icon_path).exists():
            with winreg.CreateKey(
                winreg.HKEY_CURRENT_USER,
                f"Software\\Classes\\{PROGID}\\DefaultIcon",
            ) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{icon_path}",0')

        # 4. Configure Shell Open Command
        cmd = get_launch_command()
        with winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            f"Software\\Classes\\{PROGID}\\shell\\open\\command",
        ) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, cmd)

        # 5. Notify Windows Shell of the change
        # SHCNE_ASSOCCHANGED = 0x08000000, SHCNF_IDLIST = 0
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0, None, None)
        return True
    except Exception:
        return False
