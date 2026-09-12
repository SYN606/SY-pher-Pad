from __future__ import annotations

import os
import tempfile
from pathlib import Path
import pytest

from crypt_core import utils
from crypt_core.aes_gcm import encrypt, decrypt
from crypt_core.key_derivation import derive_key_scrypt, generate_salt
from editor.document import SecureDocument
from config.settings_manager import AppSettings


def test_utils_pack_and_unpack():
    salt = generate_salt(16)
    key = derive_key_scrypt(b"testpass123", salt)
    plaintext = b"Hello, secure world!"
    iv, ciphertext = encrypt(plaintext, key)

    blob = utils.package(iv, salt, ciphertext, utils.KDF_SCRYPT)
    assert isinstance(blob, str)

    version, kdf, unpacked_iv, unpacked_salt, unpacked_ciphertext = utils.unpack(blob)
    assert version == utils.VERSION
    assert kdf == utils.KDF_SCRYPT
    assert unpacked_iv == iv
    assert unpacked_salt == salt
    assert unpacked_ciphertext == ciphertext

    decrypted = decrypt(unpacked_iv, unpacked_ciphertext, key)
    assert decrypted == plaintext


def test_utils_unpack_invalid_inputs():
    with pytest.raises(ValueError):
        utils.unpack("")

    with pytest.raises(ValueError):
        utils.unpack("not-base64!!")

    with pytest.raises(ValueError):
        utils.unpack("AQID")  # only 3 bytes, truncated header


def test_secure_document_lifecycle(tmp_path: Path):
    doc_path = tmp_path / "test_note.dnote"
    doc = SecureDocument()
    doc.file_path = doc_path

    # Save with password
    doc.save_encrypted("Initial secret content", password="my_strong_password")
    assert doc_path.exists()
    assert doc.current_password == "my_strong_password"

    # Read back and decrypt
    doc2 = SecureDocument()
    doc2.file_path = doc_path
    loaded_text = doc2.load_decrypted("my_strong_password")
    assert loaded_text == "Initial secret content"
    assert doc2.current_password == "my_strong_password"

    # In-place save without re-entering password
    doc2.save_encrypted("Updated secret content")
    
    # Verify updated content on disk
    doc3 = SecureDocument()
    doc3.file_path = doc_path
    assert doc3.load_decrypted("my_strong_password") == "Updated secret content"

    # Wrong password raises error
    with pytest.raises(ValueError):
        doc3.load_decrypted("wrong_password")

    # Change password
    doc2.change_password(
        old_password="my_strong_password",
        new_password="new_strong_password",
        current_text="Changed password content",
    )
    assert doc2.current_password == "new_strong_password"

    doc4 = SecureDocument()
    doc4.file_path = doc_path
    assert doc4.load_decrypted("new_strong_password") == "Changed password content"
    with pytest.raises(ValueError):
        doc4.load_decrypted("my_strong_password")


def test_atomic_save_safety(tmp_path: Path):
    doc_path = tmp_path / "atomic.dnote"
    doc = SecureDocument()
    doc.file_path = doc_path
    doc.save_encrypted("First save", password="pass")
    first_mtime = doc_path.stat().st_mtime_ns

    doc.save_encrypted("Second save")
    assert doc_path.exists()
    assert doc.load_decrypted("pass") == "Second save"
