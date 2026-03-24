import os
import tempfile
import pytest
from src.crypto import CryptoManager


class TestCryptoManager:
    def test_generate_key(self):
        key = CryptoManager.generate_key()
        assert isinstance(key, str)
        assert len(key) == 44

    def test_derive_key(self):
        salt = b"salt12345678901234"
        password = "testpassword"
        key = CryptoManager.derive_key(password, salt)
        assert isinstance(key, bytes)
        assert len(key) == 44

    def test_derive_key_deterministic(self):
        salt = b"salt12345678901234"
        password = "testpassword"
        key1 = CryptoManager.derive_key(password, salt)
        key2 = CryptoManager.derive_key(password, salt)
        assert key1 == key2

    def test_derive_key_different_salt(self):
        salt1 = b"salt12345678901234"
        salt2 = b"salt12345678901235"
        password = "testpassword"
        key1 = CryptoManager.derive_key(password, salt1)
        key2 = CryptoManager.derive_key(password, salt2)
        assert key1 != key2

    def test_encrypt_decrypt_bytes(self):
        key = CryptoManager.generate_key()
        cm = CryptoManager(key)
        original = b"Hello, World!"
        encrypted = cm.encrypt(original)
        decrypted = cm.decrypt(encrypted)
        assert decrypted == original
        assert encrypted != original

    def test_encrypt_decrypt_string_key(self):
        key = CryptoManager.generate_key()
        cm = CryptoManager(key)
        original = b"Test data with special chars: !@#$%^&*()"
        encrypted = cm.encrypt(original)
        decrypted = cm.decrypt(encrypted)
        assert decrypted == original

    def test_encrypt_decrypt_large_data(self):
        key = CryptoManager.generate_key()
        cm = CryptoManager(key)
        original = b"x" * 10000
        encrypted = cm.encrypt(original)
        decrypted = cm.decrypt(encrypted)
        assert decrypted == original

    def test_encrypt_without_key_raises(self):
        cm = CryptoManager()
        with pytest.raises(ValueError, match="No key set"):
            cm.encrypt(b"data")

    def test_decrypt_without_key_raises(self):
        cm = CryptoManager()
        with pytest.raises(ValueError, match="No key set"):
            cm.decrypt(b"data")

    def test_decrypt_wrong_key_raises(self):
        cm1 = CryptoManager(CryptoManager.generate_key())
        cm2 = CryptoManager(CryptoManager.generate_key())
        encrypted = cm1.encrypt(b"data")
        with pytest.raises(ValueError, match="Decryption failed"):
            cm2.decrypt(encrypted)

    def test_encrypt_file(self):
        key = CryptoManager.generate_key()
        cm = CryptoManager(key)

        with tempfile.NamedTemporaryFile(delete=False) as f:
            input_path = f.name
            f.write(b"Test file content")

        output_path = input_path + ".enc"

        try:
            cm.encrypt_file(input_path, output_path)
            assert os.path.exists(output_path)
            with open(output_path, "rb") as f:
                encrypted = f.read()
            assert encrypted != b"Test file content"
        finally:
            os.unlink(input_path)
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_decrypt_file(self):
        key = CryptoManager.generate_key()
        cm = CryptoManager(key)

        original_content = b"Test file content for decryption"
        with tempfile.NamedTemporaryFile(delete=False) as f:
            input_path = f.name
            f.write(original_content)

        encrypted_path = input_path + ".enc"
        decrypted_path = input_path + ".dec"

        try:
            cm.encrypt_file(input_path, encrypted_path)
            cm.decrypt_file(encrypted_path, decrypted_path)
            with open(decrypted_path, "rb") as f:
                decrypted = f.read()
            assert decrypted == original_content
        finally:
            os.unlink(input_path)
            if os.path.exists(encrypted_path):
                os.unlink(encrypted_path)
            if os.path.exists(decrypted_path):
                os.unlink(decrypted_path)

    def test_init_with_base64_key(self):
        key = CryptoManager.generate_key()
        cm = CryptoManager(key)
        data = b"test"
        assert cm.decrypt(cm.encrypt(data)) == data
