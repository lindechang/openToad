# tests/agent_network/test_task.py
import pytest
from src.agent_network.task import (
    TaskStatus, Task, TaskResult
)
from datetime import datetime


def test_task_status_enum():
    """测试任务状态枚举"""
    assert TaskStatus.PENDING.value == "pending"
    assert TaskStatus.IN_PROGRESS.value == "in_progress"
    assert TaskStatus.COMPLETED.value == "completed"
    assert TaskStatus.FAILED.value == "failed"
    assert TaskStatus.CANCELLED.value == "cancelled"


def test_task_creation():
    """测试任务创建"""
    task = Task(
        task_id="task-123",
        description="Test task description"
    )
    assert task.task_id == "task-123"
    assert task.description == "Test task description"
    assert task.status == TaskStatus.PENDING
    assert len(task.subtask_ids) == 0


def test_task_with_subtasks():
    """测试带子任务的任务"""
    parent = Task(
        task_id="parent-1",
        description="Parent task"
    )
    subtask1 = Task(
        task_id="sub-1",
        description="Subtask 1",
        parent_task_id="parent-1"
    )
    subtask2 = Task(
        task_id="sub-2",
        description="Subtask 2",
        parent_task_id="parent-1"
    )
    parent.subtask_ids = ["sub-1", "sub-2"]
    
    assert len(parent.subtask_ids) == 2
    assert subtask1.parent_task_id == "parent-1"


def test_task_result():
    """测试任务结果"""
    result = TaskResult(
        task_id="task-123",
        success=True,
        output="Task completed successfully"
    )
    assert result.task_id == "task-123"
    assert result.success == True
    assert result.output == "Task completed successfully"
