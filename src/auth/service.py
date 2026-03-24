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
        encryption_response = self._http.post("/api/auth/encryption-key", data={
            "token": token
        })

        user_session = UserSession(
            user_id=login_response["user_id"],
            email=email,
            encryption_key=encryption_response["encryption_key"],
            token=token
        )

        self._save_session(user_session)
        self._session = user_session
        return user_session

    def logout(self) -> None:
        """Logout and clear session."""
        self._session = None
        self._delete_session()

    def _load_session(self) -> Optional[UserSession]:
        """Load session from disk."""
        if not self.SESSION_FILE.exists():
            return None
        try:
            with open(self.SESSION_FILE, "r") as f:
                data = json.load(f)
            return UserSession(**data)
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
