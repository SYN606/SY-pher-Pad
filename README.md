# SY-pherPad

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-v1.0.0-purple.svg)](https://github.com/SYN606/DarkCipher/releases/tag/v1.0.0)
[![Issues](https://img.shields.io/github/issues/SYN606/DarkCipher/issues)](https://github.com/SYN606/DarkCipher/issues)
[![Stars](https://img.shields.io/github/stars/SYN606/DarkCipher?style=social)](https://github.com/SYN606/DarkCipher/stargazers)
| [![Developer](https://img.shields.io/badge/developer-SYN%20606-red.svg)](https://github.com/SYN606)

**SY-pherPad** is a secure, encrypted desktop notepad application built with Python and PyQt6. It leverages robust **AES-256-GCM** authenticated encryption to protect your sensitive text documents seamlessly behind password-based security keys.

The core cryptographic architecture relies on modern key derivation functions, unique initialization vectors per write session, and a custom, self-describing structured file container (`.dnote`).

---

## Features

* **Authenticated Encryption:** Implements hardware-accelerated AES-256-GCM ensuring both confidentiality and tamper-proof data integrity.
* **Strong Key Derivation:** Supports adaptive password hashing via `scrypt` (default) and `PBKDF2-HMAC-SHA256` using secure, cryptographically random salts (16-byte).
* **Native GUI Interface:** A clean, modern desktop editing environment managed via PyQt6.
* **Find and Replace Subsystem:** Advanced, non-blocking modeless search utility supporting Wrap Around mapping, case-sensitivity switches, and global bulk text replacements.
* **Dynamic Key Management:** Built-in settings interface allowing full document re-encryption when modifying or rotating document security keys.
* **Self-Describing Formats:** Saves directly into a custom packaged `.dnote` binary format embedded with metadata tags describing the KDF engine used.

---

## For Development

1. Clone the repository:

    ```bash
    git clone https://github.com/SYN606/SY-pher-Pad.git
    cd DarkCipher
    ```

2. (Optional) Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use
    venv\Scripts\activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

---

## Usage

**Encrypt a text or file:**

This will run the GUI

```python
python main.py
```
---

## Contributing

Contributions, issues and feature requests are welcome!  
Please open an issue to discuss what you’d like to improve.

---

## Credits

- Inspired by cryptography best practices and secure password-based encryption
- Contributors: [SYN606](https://github.com/SYN606)

---
