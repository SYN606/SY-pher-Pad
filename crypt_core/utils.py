import base64
from pathlib import Path
import binascii

VERSION = 2
KDF_PBKDF2 = 1
KDF_SCRYPT = 2


def create_header(version: int, kdf: int, iv: bytes, salt: bytes) -> bytes:
    """Creates the unencrypted header which is used as AAD in V2."""
    return (version.to_bytes(1, "big") + kdf.to_bytes(1, "big") +
            len(iv).to_bytes(1, "big") + iv + len(salt).to_bytes(1, "big") +
            salt)


def package(header: bytes, ciphertext: bytes) -> str:
    """Pack encrypted components into Base64 blob."""
    blob = header + ciphertext
    return base64.b64encode(blob).decode("utf-8")


def unpack(blob: str) -> tuple[int, int, bytes, bytes, bytes, bytes]:
    """Unpack Base64 blob with strict bounds and format validation."""
    if not blob or not isinstance(blob, str):
        raise ValueError("Invalid document data: file is empty or not text.")

    try:
        raw = base64.b64decode(blob.strip().encode("utf-8"))
    except binascii.Error as e:
        raise ValueError(f"File is corrupted or not a valid SY-pherPad document: {e}") from e

    # Minimum valid length: version (1) + kdf (1) + iv_len (1) + iv (12) + salt_len (1) + salt (16) + tag (16) = 48 bytes
    if len(raw) < 20:
        raise ValueError("File is corrupted or truncated (insufficient header size).")

    version = raw[0]
    kdf = raw[1]

    iv_len = raw[2]
    offset = 3
    if offset + iv_len >= len(raw):
        raise ValueError("File is corrupted (invalid IV offset).")
    iv = raw[offset:offset + iv_len]
    offset += iv_len

    salt_len = raw[offset]
    offset += 1
    if offset + salt_len > len(raw):
        raise ValueError("File is corrupted (invalid salt offset).")
    salt = raw[offset:offset + salt_len]
    offset += salt_len
    
    header = raw[:offset]
    ciphertext = raw[offset:]
    
    # AES-GCM tag is 16 bytes, so ciphertext must be at least 16 bytes
    if len(ciphertext) < 16:
        raise ValueError("File is corrupted (missing authentication tag or ciphertext).")

    return version, kdf, iv, salt, ciphertext, header


def save_file(path: str, data: bytes):
    Path(path).write_bytes(data)


def load_file(path: str) -> bytes:
    return Path(path).read_bytes()
