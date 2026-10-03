# SY-pherPad

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-v1.1.0-purple.svg)](https://github.com/SYN606/SY-pher-Pad/releases/tag/v1.1.0)
[![Issues](https://img.shields.io/github/issues/SYN606/SY-pher-Pad/issues)](https://github.com/SYN606/SY-pher-Pad/issues)
[![Stars](https://img.shields.io/github/stars/SYN606/SY-pher-Pad?style=social)](https://github.com/SYN606/SY-pher-Pad/stargazers)
| [![Developer](https://img.shields.io/badge/developer-SYN%20606-red.svg)](https://github.com/SYN606)

**SY-pherPad** is a secure, encrypted desktop notepad application built with Python and PyQt6. It leverages robust **AES-256-GCM** authenticated encryption to protect your sensitive text documents seamlessly behind password-based security keys.

The core cryptographic architecture relies on modern key derivation functions, unique initialization vectors per write session, and a custom, self-describing structured file container (`.dnote`).

---

## Features

* **Authenticated Encryption (AEAD):** Implements hardware-accelerated AES-256-GCM ensuring both confidentiality and tamper-proof data integrity. File metadata headers are intrinsically bound to the ciphertext as Associated Authenticated Data (AAD).
* **Strong Key Derivation:** Supports adaptive password hashing via `scrypt` (default) and `PBKDF2-HMAC-SHA256` using secure, cryptographically random 16-byte salts.
* **Atomic Save Operations:** Saves are performed atomically (writing to temp files before replacing), ensuring your documents are never corrupted in the event of a system crash or power loss.
* **Native GUI Interface:** A clean, modern desktop editing environment managed via PyQt6.
* **Find and Replace Subsystem:** Advanced, non-blocking modeless search utility supporting wrap-around mapping, case-sensitivity switches, and global bulk text replacements.
* **Dynamic Key Management:** Built-in settings interface allowing full document re-encryption when modifying or rotating document passphrases.
* **Self-Describing Formats:** Saves directly into a custom packaged `.dnote` Base64 binary format embedded with metadata tags describing the KDF engine and encryption version used, ensuring forwards and backwards compatibility.

---

## Installation & Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/SYN606/SY-pher-Pad.git
    cd SY-pher-Pad
    ```

2. (Optional but recommended) Create and activate a virtual environment using `uv`:

    ```bash
    uv venv
    
    # On Linux/macOS:
    source .venv/bin/activate
    
    # On Windows:
    .venv\Scripts\activate
    ```

3. Install dependencies:

    ```bash
    uv sync
    ```

---

## Usage

**Launch the application:**

Start the secure GUI editor by running:

```bash
uv run main.py
# or simply: python main.py
```

Once opened, you can type your secret notes, hit `Ctrl+S`, and you will be prompted to set a secure password. The resulting `.dnote` file can safely be backed up to the cloud or sent over unsecured channels!

---

## Contributing

Contributions, issues, and feature requests are welcome!  
Please open an issue to discuss what you’d like to improve.

---

## Credits

- Inspired by cryptography best practices and secure password-based encryption.
- Contributors: [SYN606](https://github.com/SYN606)

---
