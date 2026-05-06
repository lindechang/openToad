# tests/agent_network/test_discovery.py
import pytest
from src.agent_network.discovery import LocalAgentRegistry
from src.agent_network.role import AgentInfo, AgentRole


def test_local_agent_registry_register():
    """测试注册 Agent"""
    registry = LocalAgentRegistry()
    agent = AgentInfo(
        agent_id="agent-1",
        name="Test Agent",
        role=AgentRole.WORKER
    )
    registry.register(agent)
    
    assert registry.get_by_id("agent-1") is not None
    assert registry.get_by_id("agent-1").status == "online"


def test_local_agent_registry_get_by_role():
    """测试按角色获取 Agent"""
    registry = LocalAgentRegistry()
    registry.register(AgentInfo(
        agent_id="worker-1",
        name="Worker 1",
        role=AgentRole.WORKER
    ))
    registry.register(AgentInfo(
        agent_id="researcher-1",
        name="Researcher 1",
        role=AgentRole.RESEARCHER
    ))
    
    workers = registry.get_by_role("worker")
    researchers = registry.get_by_role("researcher")
    
    assert len(workers) == 1
    assert len(researchers) == 1


def test_local_agent_registry_unregister():
    """测试注销 Agent"""
    registry = LocalAgentRegistry()
    agent = AgentInfo(
        agent_id="agent-1",
        name="Test Agent",
        role=AgentRole.WORKER
    )
    registry.register(agent)
    registry.unregister("agent-1")
    
    assert registry.get_by_id("agent-1").status == "offline"
