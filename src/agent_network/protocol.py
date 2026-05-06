# src/agent_network/protocol.py
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from datetime import datetime
import json
import uuid


class A2AMessageType(str, Enum):
    """A2A 消息类型"""
    DISCOVERY_REQUEST = "discovery_request"
    DISCOVERY_RESPONSE = "discovery_response"
    TASK_ASSIGN = "task_assign"
    TASK_ACCEPT = "task_accept"
    TASK_REJECT = "task_reject"
    TASK_STATUS = "task_status"
    TASK_RESULT = "task_result"
    WORKSPACE_SYNC = "workspace_sync"


@dataclass
class A2AMessage:
    """A2A 消息"""
    message_id: str
    type: A2AMessageType
    from_agent_id: str
    to_agent_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    
    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "type": self.type.value,
            "from_agent_id": self.from_agent_id,
            "to_agent_id": self.to_agent_id,
            "payload": self.payload,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "A2AMessage":
        return cls(
            message_id=data["message_id"],
            type=A2AMessageType(data["type"]),
            from_agent_id=data["from_agent_id"],
            to_agent_id=data.get("to_agent_id"),
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp")
        )
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> "A2AMessage":
        return cls.from_dict(json.loads(json_str))


def create_discovery_request(from_agent_id: str) -> A2AMessage:
    return A2AMessage(
        message_id=str(uuid.uuid4()),
        type=A2AMessageType.DISCOVERY_REQUEST,
        from_agent_id=from_agent_id
    )


def create_discovery_response(from_agent_id: str, agents: List[dict]) -> A2AMessage:
    return A2AMessage(
        message_id=str(uuid.uuid4()),
        type=A2AMessageType.DISCOVERY_RESPONSE,
        from_agent_id=from_agent_id,
        payload={"agents": agents}
    )


def create_task_assign(from_agent_id: str, to_agent_id: str, task: dict) -> A2AMessage:
    return A2AMessage(
        message_id=str(uuid.uuid4()),
        type=A2AMessageType.TASK_ASSIGN,
        from_agent_id=from_agent_id,
        to_agent_id=to_agent_id,
        payload={"task": task}
    )


def create_task_result(from_agent_id: str, to_agent_id: str, task_id: str,
                      success: bool, output: Optional[str] = None,
                      error: Optional[str] = None) -> A2AMessage:
    return A2AMessage(
        message_id=str(uuid.uuid4()),
        type=A2AMessageType.TASK_RESULT,
        from_agent_id=from_agent_id,
        to_agent_id=to_agent_id,
        payload={
            "task_id": task_id,
            "success": success,
            "output": output,
            "error": error
        }
    )
