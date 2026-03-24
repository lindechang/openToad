import os
import base64
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoManager:
    def __init__(self, key: Optional[str] = None):
        if key is None:
            self._key: Optional[bytes] = None
        elif isinstance(key, str):
            self._key = key.encode() if len(key) == 44 else base64.urlsafe_b64decode(key)
        else:
            self._key = key
        self._fernet = Fernet(self._key) if self._key else None

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password.encode())
        return base64.urlsafe_b64encode(key)

    @staticmethod
    def generate_key() -> str:
        return Fernet.generate_key().decode()

    def encrypt(self, data: bytes) -> bytes:
        if self._fernet is None:
            raise ValueError("No key set. Initialize with a key or set one before encrypting.")
        return self._fernet.encrypt(data)

    def decrypt(self, data: bytes) -> bytes:
        if self._fernet is None:
            raise ValueError("No key set. Initialize with a key or set one before decrypting.")
        try:
            return self._fernet.decrypt(data)
        except InvalidToken as e:
            raise ValueError("Decryption failed: invalid token or wrong key") from e

    def encrypt_file(self, input_path: str, output_path: str) -> None:
        with open(input_path, "rb") as f:
            data = f.read()
        encrypted = self.encrypt(data)
        with open(output_path, "wb") as f:
            f.write(encrypted)

    def decrypt_file(self, input_path: str, output_path: str) -> None:
        with open(input_path, "rb") as f:
            encrypted = f.read()
        decrypted = self.decrypt(encrypted)
        with open(output_path, "wb") as f:
            f.write(decrypted)
