# tests/agent_network/test_a2a_gateway.py
"""
A2A Gateway 服务测试
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from src.agent_network.a2a_gateway import (
    A2AGatewayService,
    NetworkAgent,
    get_a2a_gateway,
    start_a2a_gateway,
    stop_a2a_gateway
)
from src.agent_network.role import AgentInfo, AgentRole


@pytest.mark.asyncio
async def test_a2a_gateway_service_creation():
    """测试 A2A Gateway 服务创建"""
    gateway = A2AGatewayService()
    assert gateway is not None
    assert len(gateway._agent_registry) == 0
    assert len(gateway._a2a_handler.get_online_agents()) == 0


@pytest.mark.asyncio
async def test_register_agent():
    """测试 Agent 注册"""
    gateway = A2AGatewayService()

    agent_info = AgentInfo(
        agent_id="test-agent-1",
        name="Test Agent",
        role=AgentRole.WORKER
    )

    result = await gateway.register_agent(agent_info, "instance-1")
    assert result is True
    assert len(gateway._agent_registry) == 1

    registered = gateway.get_agent_by_id("test-agent-1")
    assert registered is not None
    assert registered.name == "Test Agent"
    assert registered.role == AgentRole.WORKER


@pytest.mark.asyncio
async def test_unregister_agent():
    """测试 Agent 注销"""
    gateway = A2AGatewayService()

    agent_info = AgentInfo(
        agent_id="test-agent-1",
        name="Test Agent",
        role=AgentRole.WORKER
    )

    await gateway.register_agent(agent_info, "instance-1")
    assert len(gateway._agent_registry) == 1

    result = await gateway.unregister_agent("test-agent-1")
    assert result is True
    assert len(gateway._agent_registry) == 0


@pytest.mark.asyncio
async def test_get_agents_by_role():
    """测试按角色获取 Agent"""
    gateway = A2AGatewayService()

    workers = [
        AgentInfo(agent_id="worker-1", name="Worker 1", role=AgentRole.WORKER),
        AgentInfo(agent_id="worker-2", name="Worker 2", role=AgentRole.WORKER),
    ]
    researchers = [
        AgentInfo(agent_id="researcher-1", name="Researcher 1", role=AgentRole.RESEARCHER),
    ]

    for agent in workers + researchers:
        await gateway.register_agent(agent, f"instance-{agent.agent_id}")

    assert len(gateway.get_agents_by_role(AgentRole.WORKER)) == 2
    assert len(gateway.get_agents_by_role(AgentRole.RESEARCHER)) == 1
    assert len(gateway.get_agents()) == 3


@pytest.mark.asyncio
async def test_network_agent_dataclass():
    """测试 NetworkAgent 数据类"""
    agent = NetworkAgent(
        agent_id="net-agent-1",
        name="Network Agent",
        role=AgentRole.COORDINATOR,
        instance_id="instance-1",
        is_local=False
    )

    assert agent.agent_id == "net-agent-1"
    assert agent.role == AgentRole.COORDINATOR
    assert agent.is_local is False
    assert agent.capabilities == []
    assert agent.last_seen is not None


def test_get_a2a_gateway_singleton():
    """测试全局单例"""
    gateway1 = get_a2a_gateway()
    gateway2 = get_a2a_gateway()

    assert gateway1 is gateway2
