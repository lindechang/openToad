# src/agent_network/role.py
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


class AgentRole(str, Enum):
    """预定义角色"""
    COORDINATOR = "coordinator"
    WORKER = "worker"
    RESEARCHER = "researcher"
    WRITER = "writer"
    REVIEWER = "reviewer"
    CUSTOM = "custom"


@dataclass
class AgentCapability:
    """Agent 能力"""
    name: str
    description: str
    role: AgentRole
    enabled: bool = True


@dataclass
class AgentInfo:
    """Agent 信息"""
    agent_id: str
    name: str
    role: AgentRole
    capabilities: List[AgentCapability] = field(default_factory=list)
    is_local: bool = True
    network_address: Optional[str] = None
    status: str = "offline"
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_seen: Optional[datetime] = None
