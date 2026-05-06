# src/agent_network/orchestrator.py
from typing import List, Optional, Callable, Dict
from datetime import datetime
import uuid
import logging
from .role import AgentInfo, AgentRole
from .task import Task, TaskStatus, TaskResult
from .discovery import LocalAgentRegistry

logger = logging.getLogger(__name__)


class TaskOrchestrator:
    """任务协调器"""
    def __init__(self, registry: LocalAgentRegistry):
        self.registry = registry
        self._tasks: Dict[str, Task] = {}
        self._callbacks: Dict[str, Callable] = {}
    
    def create_task(self, description: str, role: Optional[AgentRole] = None) -> Task:
        """创建主任务"""
        task = Task(
            task_id=str(uuid.uuid4()),
            description=description,
            status=TaskStatus.PENDING
        )
        self._tasks[task.task_id] = task
        logger.info(f"Created task: {task.task_id}")
        return task
    
    def split_task(self, parent_task_id: str, subtask_descriptions: List[str]) -> List[Task]:
        """将任务拆分成子任务"""
        parent = self._tasks.get(parent_task_id)
        if not parent:
            raise ValueError(f"Parent task {parent_task_id} not found")
        
        subtasks = []
        for desc in subtask_descriptions:
            subtask = Task(
                task_id=str(uuid.uuid4()),
                description=desc,
                parent_task_id=parent_task_id,
                status=TaskStatus.PENDING
            )
            self._tasks[subtask.task_id] = subtask
            parent.subtask_ids.append(subtask.task_id)
            subtasks.append(subtask)
        
        logger.info(f"Split task {parent_task_id} into {len(subtasks)} subtasks")
        return subtasks
    
    def assign_task(self, task_id: str, agent_id: str) -> None:
        """分配任务给 Agent"""
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        agent = self.registry.get_by_id(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        task.assigned_agent_id = agent_id
        task.status = TaskStatus.IN_PROGRESS
        task.updated_at = datetime.utcnow()
        logger.info(f"Assigned task {task_id} to agent {agent_id}")
    
    def find_agent_for_task(self, task: Task) -> Optional[AgentInfo]:
        """根据任务找到合适的 Agent（MVP 简化版：按角色匹配）"""
        role_preference = {
            "search": AgentRole.RESEARCHER,
            "write": AgentRole.WRITER,
            "review": AgentRole.REVIEWER,
        }
        
        for keyword, role in role_preference.items():
            if keyword in task.description.lower():
                agents = self.registry.get_by_role(role.value)
                if agents:
                    return agents[0]
        
        workers = self.registry.get_by_role(AgentRole.WORKER.value)
        return workers[0] if workers else None
    
    def update_task_result(self, result: TaskResult) -> None:
        """更新任务结果"""
        task = self._tasks.get(result.task_id)
        if not task:
            return
        
        if result.success:
            task.status = TaskStatus.COMPLETED
            task.result = result.output
        else:
            task.status = TaskStatus.FAILED
            task.error = result.error
        
        task.completed_at = result.completed_at
        task.updated_at = datetime.utcnow()
        
        if task.parent_task_id:
            self._check_parent_completion(task.parent_task_id)
        
        if result.task_id in self._callbacks:
            self._callbacks[result.task_id](result)
        
        logger.info(f"Task {result.task_id} {task.status}")
    
    def _check_parent_completion(self, parent_task_id: str) -> None:
        """检查父任务是否所有子任务都完成"""
        parent = self._tasks.get(parent_task_id)
        if not parent:
            return
        
        all_completed = True
        all_failed = True
        results = []
        
        for subtask_id in parent.subtask_ids:
            subtask = self._tasks.get(subtask_id)
            if not subtask:
                continue
            
            if subtask.status != TaskStatus.COMPLETED:
                all_completed = False
            if subtask.status != TaskStatus.FAILED:
                all_failed = False
            
            if subtask.result:
                results.append(f"## {subtask.description}\n{subtask.result}")
        
        if all_completed:
            parent.status = TaskStatus.COMPLETED
            parent.result = "\n\n".join(results)
            parent.completed_at = datetime.utcnow()
            logger.info(f"Parent task {parent_task_id} completed, results aggregated")
        elif all_failed:
            parent.status = TaskStatus.FAILED
            parent.error = "All subtasks failed"
            logger.info(f"Parent task {parent_task_id} failed")
    
    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        return list(self._tasks.values())
    
    def on_task_complete(self, task_id: str, callback: Callable) -> None:
        self._callbacks[task_id] = callback
