"""Authentication service implementation."""
import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

try:
    from src.client.http_client import HttpClient
except ImportError:
    from client.http_client import HttpClient


@dataclass
class UserSession:
    """User session data."""
    user_id: str
    email: str
    encryption_key: str
    token: str
    memory_id: str = None


class AuthService:
    """Authentication service for managing user sessions."""

    SESSION_FILE = Path.home() / ".opentoad" / "session.json"

    def __init__(self, server_url: str):
        self._http = HttpClient(server_url)
        self._session: Optional[UserSession] = None

    @property
    def is_logged_in(self) -> bool:
        """Check if user is currently logged in."""
        return self.session is not None

    @property
    def session(self) -> Optional[UserSession]:
        """Get current session, loading from disk if needed."""
        if self._session is None:
            self._session = self._load_session()
        return self._session

    def login(self, email: str, password: str) -> UserSession:
        """Login with email and password."""
        login_response = self._http.post("/api/auth/login", data={
            "email": email,
            "password": password
        })

        token = login_response["token"]
        headers = {"Authorization": f"Bearer {token}"}
        encryption_response = self._http.post(
            "/api/auth/encryption-key",
            data=None,
            headers=headers
        )

        user_session = UserSession(
            user_id=str(login_response["user"]["id"]),
            email=email,
            encryption_key=encryption_response["encryptionKey"],
            token=token,
            memory_id=login_response["user"].get("memory_id")
        )

        self._save_session(user_session)
        self._session = user_session
        return user_session

    def register(self, email: str, password: str, name: str = "") -> dict:
        """Register a new account."""
        return self._http.post("/api/auth/register", data={
            "email": email,
            "password": password,
            "name": name
        })

    def logout(self) -> None:
        """Logout and clear session."""
        self._session = None
        self._delete_session()
    
    def update_memory_id(self, memory_id: str) -> None:
        """Update the selected memory_id in the session."""
        if self._session:
            self._session.memory_id = memory_id
            self._save_session(self._session)

    def _load_session(self) -> Optional[UserSession]:
        """Load session from disk."""
        if not self.SESSION_FILE.exists():
            return None
        try:
            with open(self.SESSION_FILE, "r") as f:
                data = json.load(f)
            return UserSession(
                user_id=data.get("user_id"),
                email=data.get("email"),
                encryption_key=data.get("encryption_key"),
                token=data.get("token"),
                memory_id=data.get("memory_id")
            )
        except (json.JSONDecodeError, TypeError, KeyError):
            return None

    def _save_session(self, session: UserSession) -> None:
        """Save session to disk."""
        self.SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.SESSION_FILE, "w") as f:
            json.dump(asdict(session), f)

    def _delete_session(self) -> None:
        """Delete session file."""
        if self.SESSION_FILE.exists():
            self.SESSION_FILE.unlink()
