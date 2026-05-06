# tests/agent_network/test_role.py
import pytest
from src.agent_network.role import (
    AgentRole, AgentCapability, AgentInfo
)
import uuid


def test_agent_role_enum():
    """测试角色枚举"""
    assert AgentRole.COORDINATOR.value == "coordinator"
    assert AgentRole.WORKER.value == "worker"
    assert AgentRole.RESEARCHER.value == "researcher"
    assert AgentRole.WRITER.value == "writer"
    assert AgentRole.REVIEWER.value == "reviewer"
    assert AgentRole.CUSTOM.value == "custom"


def test_agent_capability():
    """测试能力"""
    cap = AgentCapability(
        name="web_search",
        description="Search the web for information",
        role=AgentRole.RESEARCHER
    )
    assert cap.name == "web_search"
    assert cap.role == AgentRole.RESEARCHER
    assert cap.enabled == True


def test_agent_info():
    """测试 Agent 信息"""
    agent = AgentInfo(
        agent_id="test-123",
        name="Test Agent",
        role=AgentRole.WORKER,
        is_local=True
    )
    assert agent.agent_id == "test-123"
    assert agent.role == AgentRole.WORKER
    assert agent.status == "offline"
