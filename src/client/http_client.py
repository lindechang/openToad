import requests
from typing import Any, Dict, Optional


class HttpClient:
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()

    def _build_url(self, endpoint: str) -> str:
        return f"{self.base_url}{endpoint}"

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        url = self._build_url(endpoint)
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json() if response.content else None

    def post(self, endpoint: str, data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Any:
        url = self._build_url(endpoint)
        response = self.session.post(url, json=data, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json() if response.content else None
