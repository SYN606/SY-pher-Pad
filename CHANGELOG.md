# SY-pherPad v1.1.0 🚀

A major update bringing seamless in-place saving, native Windows file association, and a complete Notepad-style user experience.

---

### ⚡ What's New & Fixed

* **In-Place File Saving (`Ctrl+S`)**: Fixed the bug where editing and saving created a duplicate file. SY-pherPad now caches the session key and saves directly to the open file without re-prompting.
* **Atomic Persistence**: File saves now stage through a temporary file with `fsync`, preventing data corruption or truncated files during crashes.
* **Right-Click & CLI Opening**: Launching `.dnote` files via command-line, double-click, or right-click **"Open With"** now automatically opens and prompts for decryption.
* **Windows File Association**: Added a one-click button in **Settings -> Security & System** to register `.dnote` files in Windows Explorer (no admin privileges required).
* **Drag-and-Drop**: Drag any `.dnote` file directly into the editor to open and decrypt it.

---

### 📝 Notepad Experience Upgrades

* **Unsaved Changes Safety**: Prompts to *Save / Don't Save / Cancel* before New, Open, or Exit to prevent accidental data loss.
* **Live Status Bar**: Real-time display for cursor position (`Ln X, Col Y`), character counts, zoom level (`100%`), and encoding (`UTF-8`).
* **Word Wrap Toggle**: Switch between word wrapping and horizontal scrolling under `View -> Word Wrap` (persisted across sessions).
* **Classic Shortcuts**:
  * `F5`: Insert current Date & Time
  * `Ctrl+G`: Go to Line
  * `Del`: Delete selected text
  * `F3` / `Shift+F3`: Find Next / Find Previous
  * `Ctrl+0`: Reset zoom to 100%
* **Settings Synchronization**: Window size, position, font styling, and view options now reliably persist across app restarts.
* **Instant Replace All**: Optimized batch replacements with atomic single-step undo (`Ctrl+Z`).

---

### 📦 Assets

* **`SY-pherPad.exe`**: Standalone single-file Windows executable (portable, no install needed).