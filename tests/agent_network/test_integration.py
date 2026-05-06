# tests/agent_network/test_integration.py
import sys
sys.path.insert(0, '/Users/lindechang/Desktop/BOOK/workSpace/aiPrj/OpenToad')
from src.agent_network import (
    AgentInfo, AgentRole, LocalAgentRegistry,
    TaskOrchestrator, TaskResult
)


def test_full_workflow():
    """测试完整工作流"""
    # Setup
    registry = LocalAgentRegistry()

    coordinator = AgentInfo(
        agent_id="coord-1",
        name="Coordinator",
        role=AgentRole.COORDINATOR
    )
    registry.register(coordinator)

    researcher = AgentInfo(
        agent_id="researcher-1",
        name="Researcher",
        role=AgentRole.RESEARCHER
    )
    registry.register(researcher)

    writer = AgentInfo(
        agent_id="writer-1",
        name="Writer",
        role=AgentRole.WRITER
    )
    registry.register(writer)

    orchestrator = TaskOrchestrator(registry)

    # Create main task
    main_task = orchestrator.create_task(
        "Research and write a report on AI agents"
    )

    # Split into subtasks
    subtasks = orchestrator.split_task(
        main_task.task_id,
        [
            "Research AI agent technologies",
            "Write report based on research"
        ]
    )
    assert len(subtasks) == 2

    # Complete first subtask (research)
    result1 = TaskResult(
        task_id=subtasks[0].task_id,
        success=True,
        output="Found information about multi-agent systems"
    )
    orchestrator.update_task_result(result1)

    # Complete second subtask (write)
    result2 = TaskResult(
        task_id=subtasks[1].task_id,
        success=True,
        output="Report written with findings"
    )
    orchestrator.update_task_result(result2)

    # Verify main task is completed with aggregated results
    final_task = orchestrator.get_task(main_task.task_id)
    assert final_task.status.value == "completed"
    assert "Research AI agent technologies" in final_task.result
    assert "Write report based on research" in final_task.result


def test_agent_discovery_and_task_assignment():
    """测试 Agent 发现和任务分配"""
    registry = LocalAgentRegistry()
    for i in range(3):
        agent = AgentInfo(
            agent_id=f"worker-{i}",
            name=f"Worker {i}",
            role=AgentRole.WORKER
        )
        registry.register(agent)

    orchestrator = TaskOrchestrator(registry)
    assert len(registry.get_all()) == 3
    assert len(registry.get_by_role("worker")) == 3

    task = orchestrator.create_task("A search task")
    task.description = "Search for something"

    agent = orchestrator.find_agent_for_task(task)
    assert agent is not None


if __name__ == "__main__":
    print("Running integration tests...")
    test_full_workflow()
    print("✅ test_full_workflow passed")
    test_agent_discovery_and_task_assignment()
    print("✅ test_agent_discovery_and_task_assignment passed")
    print("\n🎉 All integration tests passed!")
