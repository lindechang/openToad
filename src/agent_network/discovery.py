# src/agent_network/discovery.py
from typing import List, Optional, Dict
import threading
import uuid
from .role import AgentInfo


class LocalAgentRegistry:
    """本地 Agent 注册中心"""
    def __init__(self):
        self._agents: Dict[str, AgentInfo] = {}
        self._lock = threading.Lock()
    
    def register(self, agent: AgentInfo) -> None:
        with self._lock:
            if not agent.agent_id:
                agent.agent_id = str(uuid.uuid4())
            agent.status = "online"
            self._agents[agent.agent_id] = agent
    
    def unregister(self, agent_id: str) -> None:
        with self._lock:
            if agent_id in self._agents:
                self._agents[agent_id].status = "offline"
    
    def get_all(self) -> List[AgentInfo]:
        with self._lock:
            return list(self._agents.values())
    
    def get_by_id(self, agent_id: str) -> Optional[AgentInfo]:
        return self._agents.get(agent_id)
    
    def get_by_role(self, role: str) -> List[AgentInfo]:
        with self._lock:
            return [a for a in self._agents.values()
                    if a.role.value == role and a.status == "online"]


class NetworkAgentDiscovery:
    """网络 Agent 发现（通过 Gateway）"""
    def __init__(self, gateway_url: str):
        self.gateway_url = gateway_url
    
    def discover(self) -> List[AgentInfo]:
        # TODO: 通过 Gateway 发现网络上的 Agent
        return []
