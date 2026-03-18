from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from src.client.http_client import HttpClient
from src.client.config import ClientConfig

@dataclass
class InstanceInfo:
    id: str
    version: str
    user_id: Optional[int]
    bound_at: Optional[datetime]
    registered_at: datetime
    last_heartbeat_at: datetime
    status: str

class InstanceManager:
    def __init__(self, config: ClientConfig):
        self.config = config
        self.http_client = HttpClient(config.api_base, config.http_timeout)
        self._info: Optional[InstanceInfo] = None

    def register(self) -> Dict[str, Any]:
        data = {
            "instanceId": self.config.instance_id,
            "version": self.config.instance_version
        }
        result = self.http_client.post("/instance/register", data)
        self._info = self._parse_instance(result)
        return result

    def bind_user(self, user_id: int) -> Dict[str, Any]:
        data = {
            "instanceId": self.config.instance_id,
            "userId": user_id
        }
        result = self.http_client.post("/instance/bind", data)
        self._info = self._parse_instance(result)
        return result

    def get_status(self) -> Optional[InstanceInfo]:
        if not self.config.instance_id:
            return None
        result = self.http_client.get("/instance/status", {"instanceId": self.config.instance_id})
        self._info = self._parse_instance(result)
        return self._info

    def _parse_instance(self, data: Dict) -> InstanceInfo:
        return InstanceInfo(
            id=data["id"],
            version=data["version"],
            user_id=data.get("userId"),
            bound_at=self._parse_datetime(data.get("boundAt")),
            registered_at=self._parse_datetime(data["registeredAt"]),
            last_heartbeat_at=self._parse_datetime(data["lastHeartbeatAt"]),
            status=data["status"]
        )

    @staticmethod
    def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
