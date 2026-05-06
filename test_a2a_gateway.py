#!/usr/bin/env python3
"""
A2A Gateway 功能验证脚本
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent_network.a2a_gateway import (
    A2AGatewayService,
    NetworkAgent,
    get_a2a_gateway
)
from src.agent_network.role import AgentInfo, AgentRole
import asyncio


async def test_a2a_gateway():
    """测试 A2A Gateway 功能"""
    print("=" * 60)
    print("Testing A2A Gateway Service")
    print("=" * 60)

    # 1. 测试服务创建
    print("\n1. Testing service creation...")
    gateway = A2AGatewayService()
    assert gateway is not None
    print("   ✓ A2A Gateway service created successfully")

    # 2. 测试 Agent 注册
    print("\n2. Testing agent registration...")
    agent_info = AgentInfo(
        agent_id="test-agent-1",
        name="Test Agent",
        role=AgentRole.WORKER
    )
    result = await gateway.register_agent(agent_info, "instance-1")
    assert result is True
    print(f"   ✓ Agent '{agent_info.name}' registered successfully")

    # 3. 测试获取注册的 Agent
    print("\n3. Testing get registered agent...")
    registered = gateway.get_agent_by_id("test-agent-1")
    assert registered is not None
    assert registered.name == "Test Agent"
    assert registered.role == AgentRole.WORKER
    print(f"   ✓ Retrieved agent: {registered.name} (Role: {registered.role.value})")

    # 4. 测试注册多个 Agent
    print("\n4. Testing multiple agent registration...")
    agents = [
        AgentInfo(agent_id="coordinator-1", name="Main Coordinator", role=AgentRole.COORDINATOR),
        AgentInfo(agent_id="researcher-1", name="Research Agent", role=AgentRole.RESEARCHER),
        AgentInfo(agent_id="writer-1", name="Writer Agent", role=AgentRole.WRITER),
    ]
    for agent in agents:
        await gateway.register_agent(agent, f"instance-{agent.agent_id}")
    print(f"   ✓ Registered {len(agents)} more agents")

    # 5. 测试按角色获取 Agent
    print("\n5. Testing get agents by role...")
    coordinators = gateway.get_agents_by_role(AgentRole.COORDINATOR)
    workers = gateway.get_agents_by_role(AgentRole.WORKER)
    print(f"   ✓ Found {len(coordinators)} coordinator(s)")
    print(f"   ✓ Found {len(workers)} worker(s)")

    # 6. 测试获取所有 Agent
    print("\n6. Testing get all agents...")
    all_agents = gateway.get_agents()
    print(f"   ✓ Total agents: {len(all_agents)}")
    for agent in all_agents:
        print(f"     - {agent.name} ({agent.role.value})")

    # 7. 测试 Agent 注销
    print("\n7. Testing agent unregistration...")
    result = await gateway.unregister_agent("test-agent-1")
    assert result is True
    remaining = gateway.get_agents()
    assert len(remaining) == 3
    print(f"   ✓ Agent unregistered, remaining: {len(remaining)}")

    # 8. 测试 NetworkAgent 数据类
    print("\n8. Testing NetworkAgent dataclass...")
    net_agent = NetworkAgent(
        agent_id="net-agent-1",
        name="Network Agent",
        role=AgentRole.COORDINATOR,
        instance_id="instance-1",
        is_local=False
    )
    assert net_agent.agent_id == "net-agent-1"
    assert net_agent.is_local is False
    print("   ✓ NetworkAgent dataclass works correctly")

    # 9. 测试单例模式
    print("\n9. Testing singleton pattern...")
    gateway1 = get_a2a_gateway()
    gateway2 = get_a2a_gateway()
    assert gateway1 is gateway2
    print("   ✓ Global singleton works correctly")

    print("\n" + "=" * 60)
    print("All A2A Gateway tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(test_a2a_gateway())
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
