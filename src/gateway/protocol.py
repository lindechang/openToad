from enum import Enum
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


class MessageType(str, Enum):
    AUTH = "auth"
    AUTH_ACK = "auth_ack"
    MESSAGE = "message"
    RESPONSE = "response"
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    A2A = "a2a"


@dataclass
class WSMessage:
    type: str
    payload: Dict[str, Any]
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "WSMessage":
        return cls(
            type=data.get("type", ""),
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp")
        )


def create_auth_response(success: bool, instance_id: str = "", error: str = "") -> WSMessage:
    return WSMessage(
        type=MessageType.AUTH_ACK.value,
        payload={
            "success": success,
            "instance_id": instance_id,
            "error": error
        }
    )


def create_response(content: str, done: bool = False) -> WSMessage:
    return WSMessage(
        type=MessageType.RESPONSE.value,
        payload={
            "content": content,
            "done": done
        }
    )


def create_pong() -> WSMessage:
    return WSMessage(
        type=MessageType.PONG.value,
        payload={}
    )


def create_error(code: str, message: str) -> WSMessage:
    return WSMessage(
        type=MessageType.ERROR.value,
        payload={
            "code": code,
            "message": message
        }
    )


def create_a2a_message(a2a_payload: dict) -> WSMessage:
    return WSMessage(
        type=MessageType.A2A.value,
        payload=a2a_payload
    )
