# Release Notes - SY-pherPad v1.1.0

## What's Changed in v1.1.0

### 🚀 Key Improvements & Bug Fixes
- **In-Place File Saving**: Fixed bug where editing and saving an existing document prompted for password creation or created a new file. Saving (`Ctrl+S`) now directly overwrites the active document in-place using the authenticated session key.
- **Right-Click "Open With" & CLI Arguments**: `main.py` now parses command-line arguments, enabling opening and decrypting `.dnote` files when launched via right-click "Open With" or double-click.
- **Windows File Association**: Added native Windows Registry integration in `config/file_association.py` and a one-click button in Settings to associate `.dnote` files with SY-pherPad under `HKCU` (requires no admin privileges).
- **Atomic File Writing**: Prevented data loss and file corruption on crash by staging saves through atomic temporary file swaps with disk flushing (`os.fsync`).
- **Drag and Drop Support**: Dragging any `.dnote` file into the notepad window immediately opens and prompts for decryption.

### 📝 Notepad-Like Features
- **Unsaved Changes Safety Prompt**: Warns users before New, Open, or Exit if changes have not been saved (*Save / Don't Save / Cancel*).
- **Notepad Live Status Bar**: Displays real-time cursor coordinate (`Ln X, Col Y`), character counts, zoom percentage (`100%`), and encoding (`UTF-8`).
- **Word Wrap Toggle**: Added `View -> Word Wrap` mode toggle that persists across sessions.
- **Classic Notepad Shortcuts**:
  - `F5`: Insert current Date/Time at cursor.
  - `Ctrl+G`: Go to Line number dialog.
  - `Del`: Delete selected text.
  - `F3` / `Shift+F3`: Find Next / Find Previous.
  - `Ctrl+0`: Restore default zoom.
- **Unified Settings Persistence**: Window geometry, size, font family/size/styles, word wrap, and status bar preferences now persist cleanly across sessions.
- **Optimized Replace All**: Wrapped in `QTextCursor` edit blocks for instant replacements and atomic single-step undo.

### 🔒 Security & Robustness
- Added bounds checking and payload validation in container unpacking to prevent crashes on corrupted or malformed files.
- Automated unit test suite with 100% pass rate covering crypto, atomic persistence, and GUI workflows.
