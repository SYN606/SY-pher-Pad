from pathlib import Path
from crypt_core.aes_gcm import encrypt, decrypt
from crypt_core.key_derivation import derive_key_scrypt, generate_salt
from crypt_core import utils


class SecureDocument:

    def __init__(self) -> None:
        self.file_path: Path | None = None

    def new(self) -> None:
        self.file_path = None

    def save_encrypted(self, text: str, password: str) -> None:
        if not self.file_path:
            raise ValueError("No file path assigned to the document.")

        plaintext_bytes = text.encode("utf-8")
        password_bytes = password.encode("utf-8")
        salt = generate_salt(16)
        key = derive_key_scrypt(password_bytes, salt)
        iv, ciphertext = encrypt(plaintext_bytes, key)
        packed_data_str = utils.package(iv, salt, ciphertext, utils.KDF_SCRYPT)
        self.file_path.write_bytes(packed_data_str.encode("utf-8"))

    def load_decrypted(self, password: str) -> str:
        if not self.file_path or not self.file_path.exists():
            raise FileNotFoundError("Target file does not exist.")

        packed_data_str = self.file_path.read_bytes().decode("utf-8")
        version, kdf_type, iv, salt, ciphertext = utils.unpack(packed_data_str)
        password_bytes = password.encode("utf-8")
        if kdf_type == utils.KDF_SCRYPT:
            key = derive_key_scrypt(password_bytes, salt)
        elif kdf_type == utils.KDF_PBKDF2:
            from crypt_core.key_derivation import derive_key_pbkdf2
            key = derive_key_pbkdf2(password_bytes, salt)
        else:
            raise ValueError(f"Unsupported KDF format version: {kdf_type}")
        plaintext_bytes = decrypt(iv, ciphertext, key)
        return plaintext_bytes.decode("utf-8")

    def change_password(self, old_password: str, new_password: str) -> None:
        if not self.file_path or not self.file_path.exists():
            raise FileNotFoundError(
                "No active file layout detected on disk to change credentials."
            )

        current_plaintext = self.load_decrypted(old_password)
        plaintext_bytes = current_plaintext.encode("utf-8")
        new_password_bytes = new_password.encode("utf-8")
        new_salt = generate_salt(16)
        new_key = derive_key_scrypt(new_password_bytes, new_salt)
        iv, ciphertext = encrypt(plaintext_bytes, new_key)
        packed_data_str = utils.package(iv, new_salt, ciphertext,
                                        utils.KDF_SCRYPT)
        self.file_path.write_bytes(packed_data_str.encode("utf-8"))
