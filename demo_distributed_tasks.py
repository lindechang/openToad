#!/usr/bin/env python3
"""
A2A 网络跨设备协作演示
展示如何在分布式环境中分配和管理任务
"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from agent_network import (
    AgentInfo, AgentRole, LocalAgentRegistry,
    TaskOrchestrator, TaskStatus, TaskResult,
    A2AMessageHandler, create_task_assign
)


async def demo_distributed_task_assignment():
    """演示分布式任务分配"""
    print("=" * 70)
    print(" A2A Network - Distributed Task Assignment Demo")
    print("=" * 70)

    # 1. 初始化本地 Agent 注册中心
    print("\n📦 Step 1: Initializing Local Agent Registry")
    registry = LocalAgentRegistry()

    # 2. 注册本地 Agent
    print("\n🤖 Step 2: Registering Local Agents")
    local_agents = [
        AgentInfo(
            agent_id="coordinator-local",
            name="Local Coordinator",
            role=AgentRole.COORDINATOR
        ),
        AgentInfo(
            agent_id="worker-local-1",
            name="Local Worker 1",
            role=AgentRole.WORKER
        ),
        AgentInfo(
            agent_id="researcher-local-1",
            name="Local Researcher",
            role=AgentRole.RESEARCHER
        ),
    ]
    for agent in local_agents:
        registry.register(agent)
        print(f"   ✓ Registered: {agent.name} ({agent.role.value})")

    # 3. 模拟注册远程 Agent
    print("\n🌐 Step 3: Simulating Remote Agents")
    remote_agents = [
        AgentInfo(
            agent_id="worker-remote-1",
            name="Remote Worker 1",
            role=AgentRole.WORKER,
            is_local=False,
            network_address="192.168.1.101:18989"
        ),
        AgentInfo(
            agent_id="writer-remote-1",
            name="Remote Writer",
            role=AgentRole.WRITER,
            is_local=False,
            network_address="192.168.1.102:18989"
        ),
    ]
    # 将远程 Agent 也注册到本地注册中心（模拟发现）
    for agent in remote_agents:
        registry.register(agent)
    print(f"   ✓ Discovered and registered {len(remote_agents)} remote agent(s)")

    # 4. 初始化任务协调器
    print("\n🎯 Step 4: Initializing Task Orchestrator")
    orchestrator = TaskOrchestrator(registry)
    print("   ✓ Task Orchestrator ready")

    # 5. 创建主任务
    print("\n📋 Step 5: Creating Main Task")
    main_task = orchestrator.create_task(
        "Research and write comprehensive report on AI Agents"
    )
    print(f"   ✓ Main task created: {main_task.task_id[:8]}...")
    print(f"   📝 Description: {main_task.description}")

    # 6. 拆分任务
    print("\n✂️ Step 6: Splitting Task into Subtasks")
    subtask_descriptions = [
        "Research AI agent architectures and frameworks",
        "Research multi-agent collaboration patterns",
        "Write introduction section",
        "Write technical implementation section",
        "Write conclusion and future work"
    ]
    subtasks = orchestrator.split_task(main_task.task_id, subtask_descriptions)
    print(f"   ✓ Split into {len(subtasks)} subtasks:")
    for i, subtask in enumerate(subtasks, 1):
        print(f"      {i}. {subtask.description[:40]}...")

    # 7. 模拟任务分配
    print("\n📨 Step 7: Simulating Task Assignment")

    # 创建 A2A 消息处理器
    handler = A2AMessageHandler()

    # 模拟注册虚拟连接
    class MockWebSocket:
        def __init__(self, agent_name):
            self.agent_name = agent_name

        async def send_text(self, data):
            print(f"      📤 Message sent to {self.agent_name}: {data[:50]}...")

    # 分配子任务给不同的 Agent
    assignment_map = {
        0: ("researcher-local-1", "Local Researcher", "192.168.1.100"),
        1: ("worker-remote-1", "Remote Worker 1", "192.168.1.101"),
        2: ("worker-local-1", "Local Worker 1", "192.168.1.100"),
        3: ("writer-remote-1", "Remote Writer", "192.168.1.102"),
        4: ("worker-local-1", "Local Worker 1", "192.168.1.100"),
    }

    for i, subtask in enumerate(subtasks):
        agent_id, agent_name, address = assignment_map.get(i, ("worker-local-1", "Local Worker", "local"))
        is_remote = not address.startswith("192.168.1.100")

        # 创建任务分配消息
        task_assign_msg = create_task_assign(
            from_agent_id="coordinator-local",
            to_agent_id=agent_id,
            task={
                "task_id": subtask.task_id,
                "description": subtask.description,
                "priority": "normal"
            }
        )

        # 分配任务
        orchestrator.assign_task(subtask.task_id, agent_id)

        print(f"\n   📤 Assigning subtask {i+1}:")
        print(f"      🎯 To: {agent_name}")
        print(f"      🏠 Location: {'🌐 Remote' if is_remote else '💻 Local'}")
        print(f"      📡 Address: {address}")

        # 模拟发送 A2A 消息
        if is_remote:
            print(f"      ⏳ Sending via network to {address}:18989...")

    # 8. 模拟执行子任务
    print("\n⚙️ Step 8: Simulating Subtask Execution")

    execution_results = [
        ("researcher-local-1", "Found 15 relevant papers on agent architectures"),
        ("worker-remote-1", "Identified 3 main collaboration patterns: hierarchical, peer-to-peer, and hybrid"),
        ("worker-local-1", "Introduction drafted: AI agents overview"),
        ("writer-remote-1", "Technical section written with implementation details"),
        ("worker-local-1", "Conclusion written: future directions in multi-agent systems"),
    ]

    for agent_id, result_text in execution_results:
        # 找到对应的子任务
        for subtask in subtasks:
            if subtask.assigned_agent_id == agent_id and subtask.status == TaskStatus.IN_PROGRESS:
                task_result = TaskResult(
                    task_id=subtask.task_id,
                    success=True,
                    output=result_text
                )
                orchestrator.update_task_result(task_result)
                print(f"   ✅ {agent_id}: {result_text[:40]}...")
                break

    # 9. 验证主任务汇总
    print("\n📊 Step 9: Verifying Task Aggregation")
    final_task = orchestrator.get_task(main_task.task_id)
    print(f"   📌 Main Task Status: {final_task.status.value}")
    print(f"   ✅ Completed Subtasks: {len([s for s in subtasks if s.status == TaskStatus.COMPLETED])}/{len(subtasks)}")

    if final_task.result:
        print(f"\n   📄 Aggregated Results:")
        print(f"   {'='*60}")
        for line in final_task.result.split('\n\n'):
            print(f"   {line}")
        print(f"   {'='*60}")

    # 10. 展示网络拓扑
    print("\n🌐 Step 10: Network Topology")
    print(f"\n   💻 Local Agents: {len(local_agents)}")
    for agent in local_agents:
        status_icon = "🟢" if agent.status == "online" else "🔴"
        print(f"      {status_icon} {agent.name} ({agent.role.value})")

    print(f"\n   🌐 Remote Agents: {len(remote_agents)}")
    for agent in remote_agents:
        print(f"      🔵 {agent.name} ({agent.role.value}) @ {agent.network_address}")

    print(f"\n   📡 Total Agents in Network: {len(local_agents) + len(remote_agents)}")

    # 11. 统计信息
    print("\n📈 Step 11: Statistics")
    print(f"   📊 Total Tasks: {len(orchestrator.get_all_tasks())}")
    print(f"   ✅ Completed: {len([t for t in orchestrator.get_all_tasks() if t.status == TaskStatus.COMPLETED])}")
    print(f"   ⏳ In Progress: {len([t for t in orchestrator.get_all_tasks() if t.status == TaskStatus.IN_PROGRESS])}")
    print(f"   📝 Pending: {len([t for t in orchestrator.get_all_tasks() if t.status == TaskStatus.PENDING])}")

    print("\n" + "=" * 70)
    print(" 🎉 Distributed Task Assignment Demo Complete!")
    print("=" * 70)

    print("\n💡 Key Takeaways:")
    print("   1. Tasks can be split into smaller subtasks")
    print("   2. Subtasks can be assigned to different agents (local or remote)")
    print("   3. Results are automatically aggregated when all subtasks complete")
    print("   4. A2A protocol enables communication between agents")
    print("   5. Network topology shows both local and remote agents")


if __name__ == "__main__":
    try:
        asyncio.run(demo_distributed_task_assignment())
        print("\n✅ Demo executed successfully!")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
