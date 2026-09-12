from __future__ import annotations

import os
import tempfile
from pathlib import Path

from crypt_core.aes_gcm import encrypt, decrypt
from crypt_core.key_derivation import derive_key_scrypt, generate_salt
from crypt_core import utils


class SecureDocument:
    """Manages secure text persistence by packaging cipher layers behind passphrases."""

    def __init__(self) -> None:
        self.file_path: Path | None = None
        self.current_password: str | None = None

    def new(self) -> None:
        """Resets the internal document reference tracking state."""
        self.file_path = None
        self.current_password = None

    def _atomic_write(self, data: bytes) -> None:
        """Writes bytes to target path atomically via a temporary file and flush/sync."""
        if not self.file_path:
            raise ValueError("No file path assigned to the document.")

        target_dir = self.file_path.parent
        target_dir.mkdir(parents=True, exist_ok=True)

        temp_file = tempfile.NamedTemporaryFile(dir=target_dir, delete=False, prefix=".syp_")
        temp_name = temp_file.name
        try:
            temp_file.write(data)
            temp_file.flush()
            os.fsync(temp_file.fileno())
            temp_file.close()
            os.replace(temp_name, self.file_path)
        except Exception:
            if os.path.exists(temp_name):
                os.remove(temp_name)
            raise

    def save_encrypted(self, text: str, password: str | None = None) -> None:
        """Derives structural symmetric crypt keys to write salted data directly to disk."""
        if not self.file_path:
            raise ValueError("No file path assigned to the document.")

        active_password = password or self.current_password
        if not active_password:
            raise ValueError("No password available to encrypt the document.")

        plaintext_bytes = text.encode("utf-8")
        password_bytes = active_password.encode("utf-8")
        salt = generate_salt(16)
        key = derive_key_scrypt(password_bytes, salt)
        iv, ciphertext = encrypt(plaintext_bytes, key)
        packed_data_str = utils.package(iv, salt, ciphertext, utils.KDF_SCRYPT)

        self._atomic_write(packed_data_str.encode("utf-8"))
        self.current_password = active_password

    def load_decrypted(self, password: str) -> str:
        """Parses salt metadata definitions from targeted paths to return decoded documents."""
        if not self.file_path or not self.file_path.exists():
            raise FileNotFoundError("Target file does not exist.")

        packed_data_str = self.file_path.read_bytes().decode("utf-8")
        _, kdf_type, iv, salt, ciphertext = utils.unpack(packed_data_str)
        password_bytes = password.encode("utf-8")

        if kdf_type == utils.KDF_SCRYPT:
            key = derive_key_scrypt(password_bytes, salt)
        elif kdf_type == utils.KDF_PBKDF2:
            from crypt_core.key_derivation import derive_key_pbkdf2
            key = derive_key_pbkdf2(password_bytes, salt)
        else:
            raise ValueError(f"Unsupported KDF format version: {kdf_type}")

        plaintext_bytes = decrypt(iv, ciphertext, key)
        self.current_password = password
        return plaintext_bytes.decode("utf-8")

    def change_password(self, old_password: str, new_password: str, current_text: str | None = None) -> None:
        """Decrypts the core target file and re-encrypts its payload under a new passphrase."""
        if not self.file_path or not self.file_path.exists():
            raise FileNotFoundError(
                "No active file layout detected on disk to change credentials."
            )

        if current_text is not None:
            plaintext = current_text
        else:
            plaintext = self.load_decrypted(old_password)

        self.save_encrypted(plaintext, new_password)
