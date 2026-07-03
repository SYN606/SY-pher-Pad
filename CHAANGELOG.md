# Release Notes: v1.0.1 (July 2026)

**SY-pherPad v1.0.1** introduces automatic cross-platform state handling, fixes type-checking validation errors, and adds complete single-file build automation for both Windows and Linux.

---

## 🚀 Key Improvements

### 1. Cross-Platform State Retention
* **Native OS Storage:** Upgraded configurations from forced `.ini` tracking to platform-native formats (`QSettings.Format.NativeFormat`).
  * **Windows:** Automatically saves to the Windows Registry (`HKEY_CURRENT_USER\Software\SYN 606\SY-pherPad`).
  * **Linux:** Automatically saves to standard XDG configurations (`~/.config/SYN 606/SY-pherPad.conf`).
* **Global Metadata:** Identity details are now registered globally in `main.py`, removing boilerplate path strings across files.
* **Session Persistence:** Successfully saves and loads window positions, sizes, full layout geometries, and custom editor font families/sizes.

### 2. Standalone Build Automation
* **Linux AppImage:** Created a seamless build pipeline script (`build_appimage.sh`), custom entry point (`AppRun`), and a desktop file (`sy-pherpad.desktop`) to pack the complete Python runtime into a portable `.AppImage`.
* **Windows Target:** Established a unified single-file execution command (`.exe`) optimized for the `uv` toolchain.

---

## 🔧 Fixes & Refactoring

* **Pylance Type Fixes:** Fixed explicit overloaded constructor signature warnings (`reportCallIssue` / `reportArgumentType`) inside the settings manager file.
* **Asset Path Hardening:** Fixed asset-loading logic in `get_resource_path()` to ensure layout graphics resolve correctly inside compressed standalone bundles.
* **Workspace Cleanup:** Modernized `.gitignore` rules to completely isolate temporary build artifact caches (`build/`, `dist/`, `.spec`) while retaining `uv.lock` and `pyproject.toml`.

---

## 📦 Build Targets

| Operating System | Output Format | Package Style |
| :--- | :--- | :--- |
| **Linux** | `SY-pherPad-x86_64.AppImage` | Portable universal standalone container |
| **Windows** | `SY-pherPad.exe` | Zero-dependency standalone binary |