"""Tests for auth service."""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.auth.service import AuthService, UserSession


class TestUserSession(unittest.TestCase):
    """Tests for UserSession dataclass."""

    def test_create_session(self):
        session = UserSession(
            user_id="user123",
            email="test@example.com",
            encryption_key="key123",
            token="token456"
        )
        self.assertEqual(session.user_id, "user123")
        self.assertEqual(session.email, "test@example.com")
        self.assertEqual(session.encryption_key, "key123")
        self.assertEqual(session.token, "token456")


class TestAuthService(unittest.TestCase):
    """Tests for AuthService."""

    def setUp(self):
        self.mock_http_patcher = patch('src.auth.service.HttpClient')
        self.mock_http_class = self.mock_http_patcher.start()
        self.mock_http = MagicMock()
        self.mock_http_class.return_value = self.mock_http
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_session_file = AuthService.SESSION_FILE
        AuthService.SESSION_FILE = Path(self.temp_dir.name) / "session.json"

    def tearDown(self):
        self.mock_http_patcher.stop()
        self.temp_dir.cleanup()
        AuthService.SESSION_FILE = self.original_session_file

    def test_is_logged_in_false_when_no_session(self):
        service = AuthService("https://api.example.com")
        self.assertFalse(service.is_logged_in)

    def test_login_success(self):
        self.mock_http.post.side_effect = [
            {"user_id": "user123", "token": "token456"},
            {"encryption_key": "key123"}
        ]

        service = AuthService("https://api.example.com")
        session = service.login("test@example.com", "password123")

        self.assertEqual(session.user_id, "user123")
        self.assertEqual(session.email, "test@example.com")
        self.assertEqual(session.encryption_key, "key123")
        self.assertEqual(session.token, "token456")
        self.assertTrue(service.is_logged_in)

    def test_login_calls_api_endpoints(self):
        self.mock_http.post.side_effect = [
            {"user_id": "user123", "token": "token456"},
            {"encryption_key": "key123"}
        ]

        service = AuthService("https://api.example.com")
        service.login("test@example.com", "password123")

        self.assertEqual(self.mock_http.post.call_count, 2)
        self.mock_http.post.assert_any_call("/api/auth/login", data={
            "email": "test@example.com",
            "password": "password123"
        })
        self.mock_http.post.assert_any_call("/api/auth/encryption-key", data={
            "token": "token456"
        })

    def test_logout_clears_session(self):
        self.mock_http.post.side_effect = [
            {"user_id": "user123", "token": "token456"},
            {"encryption_key": "key123"}
        ]

        service = AuthService("https://api.example.com")
        service.login("test@example.com", "password123")
        self.assertTrue(service.is_logged_in)

        service.logout()
        self.assertFalse(service.is_logged_in)

    def test_session_persisted_to_file(self):
        self.mock_http.post.side_effect = [
            {"user_id": "user123", "token": "token456"},
            {"encryption_key": "key123"}
        ]

        service = AuthService("https://api.example.com")
        service.login("test@example.com", "password123")

        with open(AuthService.SESSION_FILE, "r") as f:
            data = json.load(f)

        self.assertEqual(data["user_id"], "user123")
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["encryption_key"], "key123")
        self.assertEqual(data["token"], "token456")

    def test_session_loaded_from_file(self):
        session_data = {
            "user_id": "user456",
            "email": "loaded@example.com",
            "encryption_key": "loaded_key",
            "token": "loaded_token"
        }
        with open(AuthService.SESSION_FILE, "w") as f:
            json.dump(session_data, f)

        service = AuthService("https://api.example.com")
        self.assertTrue(service.is_logged_in)
        session = service.session
        self.assertEqual(session.user_id, "user456")
        self.assertEqual(session.email, "loaded@example.com")


if __name__ == '__main__':
    unittest.main()
