# OpenToad Agent-to-Agent (A2A) 协作系统设计

## 概述

将 OpenToad 从单个 AI 助手扩展为支持多 Agent 协作的系统，支持：
- **本地多 Agent 协作**：同一设备上多个 Agent 协同工作
- **网络分布式 Agent**：跨设备通过网络协作
- **任务分配 + 结果汇总**：主 Agent 拆分任务，分发给其他 Agent，最后汇总

同时为未来需求预留扩展点：
- 深度协作协议（任务协商、共享工作区）
- 内生信任体系（身份、凭证、信誉）
- 多模态经济交互（支付、结算）

## 架构设计

### 目录结构

```
src/
├── agent/                      # 现有：单个 Agent 推理核心
│   ├── __init__.py
│   ├── run.py
│   ├── types.py
│   └── prompt.py
├── agent_network/              # 【新增】Agent 网络协作层 ⭐
│   ├── __init__.py
│   ├── discovery.py            # Agent 发现（本地 + 网络）
│   ├── protocol.py             # A2A 协作协议
│   ├── task.py                 # 任务定义、拆分、分配
│   ├── workspace.py            # 共享工作区（为未来预留）
│   ├── role.py                 # 角色与能力系统
│   └── orchestrator.py         # 任务协调器
├── gateway/                    # 现有：扩展支持 A2A 消息
│   ├── __init__.py
│   ├── protocol.py             # 扩展消息类型
│   ├── server.py               # 扩展 A2A 消息处理
│   ├── ai_handler.py
│   └── config.py
├── client/                     # 现有：扩展支持 A2A 通讯
│   ├── __init__.py
│   ├── config.py
│   ├── http_client.py
│   ├── instance.py
│   ├── heartbeat.py
│   ├── commander.py
│   └── service.py
├── identity/                   # 【预留】为未来身份体系
└── economy/                    # 【预留】为未来经济交互

apps/desktop/src/
├── ui/
│   ├── __init__.py
│   ├── agent_network_panel.py  # 【新增】Agent 网络 UI
│   ├── main_window.py          # 集成 Agent Network 面板
│   └── ...
```

## 核心模块设计

### 1. 角色与能力系统 (role.py)

定义 Agent 的角色和能力，支持预定义角色和动态能力注册。

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Callable
from datetime import datetime

class AgentRole(str, Enum):
    """预定义角色"""
    COORDINATOR = "coordinator"  # 协调者：拆分任务、汇总结果
    WORKER = "worker"            # 工作者：执行通用任务
    RESEARCHER = "researcher"    # 研究员：搜索、收集信息
    WRITER = "writer"            # 作者：写作、文档
    REVIEWER = "reviewer"        # 审核者：质量检查
    CUSTOM = "custom"            # 自定义角色

@dataclass
class AgentCapability:
    """Agent 能力"""
    name: str                    # 能力名称，如 "web_search", "code_write"
    description: str             # 能力描述
    role: AgentRole              # 所属角色
    enabled: bool = True

@dataclass
class AgentInfo:
    """Agent 信息"""
    agent_id: str                # 唯一标识
    name: str                    # 显示名称
    role: AgentRole              # 角色
    capabilities: List[AgentCapability] = field(default_factory=list)
    is_local: bool = True        # 是否本地 Agent
    network_address: Optional[str] = None  # 网络地址（远程 Agent）
    status: str = "offline"      # online, offline, busy
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_seen: Optional[datetime] = None
```

### 2. 任务系统 (task.py)

定义任务结构、状态管理、子任务关系。

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from datetime import datetime

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    """任务"""
    task_id: str
    description: str                    # 任务描述
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent_id: Optional[str] = None  # 分配的 Agent
    parent_task_id: Optional[str] = None     # 父任务 ID
    subtask_ids: List[str] = field(default_factory=list)  # 子任务 IDs
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)  # 附加数据
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.utcnow)
```

### 3. 共享工作区 (workspace.py) - 为未来预留

为"共享工作记忆"需求预留的设计。

```python
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from datetime import datetime

@dataclass
class WorkspaceNote:
    """工作区笔记"""
    note_id: str
    author_agent_id: str
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

@dataclass
class WorkspaceFile:
    """工作区文件"""
    file_id: str
    name: str
    content_type: str
    content: bytes  # 或存储路径
    uploaded_by: str
    uploaded_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Workspace:
    """共享工作区"""
    workspace_id: str
    task_id: str
    participant_agent_ids: List[str] = field(default_factory=list)
    notes: List[WorkspaceNote] = field(default_factory=list)
    files: List[WorkspaceFile] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
```

### 4. Agent 发现 (discovery.py)

管理本地和网络 Agent 的发现、注册、状态追踪。

```python
from typing import List, Optional, Dict
from dataclasses import dataclass
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
            agent.agent_id = agent.agent_id or str(uuid.uuid4())
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
            return [a for a in self._agents.values() if a.role.value == role and a.status == "online"]

class NetworkAgentDiscovery:
    """网络 Agent 发现（通过 Gateway）"""
    def __init__(self, gateway_url: str):
        self.gateway_url = gateway_url
    
    def discover(self) -> List[AgentInfo]:
        # 通过 Gateway 发现网络上的 Agent
        # 实现细节...
        pass
```

### 5. 任务协调器 (orchestrator.py)

核心协调逻辑：拆分任务、分配任务、收集结果、汇总。

```python
from typing import List, Optional, Callable
from .role import AgentInfo, AgentRole
from .task import Task, TaskStatus, TaskResult
from .discovery import LocalAgentRegistry
import uuid
import logging

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
        logger.info(f"Assigned task {task_id} to agent {agent_id}")
    
    def find_agent_for_task(self, task: Task) -> Optional[AgentInfo]:
        """根据任务找到合适的 Agent（MVP 简化版：按角色匹配）"""
        # MVP：简单按角色匹配
        # 未来：基于能力、负载、信誉等智能匹配
        role_preference = {
            "search": AgentRole.RESEARCHER,
            "write": AgentRole.WRITER,
            "review": AgentRole.REVIEWER,
        }
        
        # 简单关键词匹配
        for keyword, role in role_preference.items():
            if keyword in task.description.lower():
                agents = self.registry.get_by_role(role.value)
                if agents:
                    return agents[0]
        
        # 默认用 Worker
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
        
        # 检查父任务是否所有子任务都完成
        if task.parent_task_id:
            self._check_parent_completion(task.parent_task_id)
        
        # 触发回调
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
            # 汇总结果
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
```

### 6. 协作协议 (protocol.py)

定义 A2A 通讯的消息格式。

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from datetime import datetime
import json

class A2AMessageType(str, Enum):
    """A2A 消息类型"""
    # 发现
    DISCOVERY_REQUEST = "discovery_request"
    DISCOVERY_RESPONSE = "discovery_response"
    # 任务
    TASK_ASSIGN = "task_assign"
    TASK_ACCEPT = "task_accept"
    TASK_REJECT = "task_reject"
    TASK_STATUS = "task_status"
    TASK_RESULT = "task_result"
    # 工作区（为未来预留）
    WORKSPACE_SYNC = "workspace_sync"

@dataclass
class A2AMessage:
    """A2A 消息"""
    message_id: str
    type: A2AMessageType
    from_agent_id: str
    to_agent_id: Optional[str] = None  # None 表示广播
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    
    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "type": self.type.value,
            "from_agent_id": self.from_agent_id,
            "to_agent_id": self.to_agent_id,
            "payload": self.payload,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "A2AMessage":
        return cls(
            message_id=data["message_id"],
            type=A2AMessageType(data["type"]),
            from_agent_id=data["from_agent_id"],
            to_agent_id=data.get("to_agent_id"),
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp")
        )
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> "A2AMessage":
        return cls.from_dict(json.loads(json_str))

# 便捷方法创建消息
import uuid

def create_discovery_request(from_agent_id: str) -> A2AMessage:
    return A2AMessage(
        message_id=str(uuid.uuid4()),
        type=A2AMessageType.DISCOVERY_REQUEST,
        from_agent_id=from_agent_id
    )

def create_discovery_response(from_agent_id: str, agents: List[dict]) -> A2AMessage:
    return A2AMessage(
        message_id=str(uuid.uuid4()),
        type=A2AMessageType.DISCOVERY_RESPONSE,
        from_agent_id=from_agent_id,
        payload={"agents": agents}
    )

def create_task_assign(from_agent_id: str, to_agent_id: str, task: dict) -> A2AMessage:
    return A2AMessage(
        message_id=str(uuid.uuid4()),
        type=A2AMessageType.TASK_ASSIGN,
        from_agent_id=from_agent_id,
        to_agent_id=to_agent_id,
        payload={"task": task}
    )

def create_task_result(from_agent_id: str, to_agent_id: str, task_id: str, 
                      success: bool, output: Optional[str] = None, 
                      error: Optional[str] = None) -> A2AMessage:
    return A2AMessage(
        message_id=str(uuid.uuid4()),
        type=A2AMessageType.TASK_RESULT,
        from_agent_id=from_agent_id,
        to_agent_id=to_agent_id,
        payload={
            "task_id": task_id,
            "success": success,
            "output": output,
            "error": error
        }
    )
```

## Gateway 扩展

扩展现有 Gateway 支持 A2A 消息路由。

### 修改 gateway/protocol.py

```python
from enum import Enum
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

class MessageType(str, Enum):
    # 现有
    AUTH = "auth"
    AUTH_ACK = "auth_ack"
    MESSAGE = "message"
    RESPONSE = "response"
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    # 【新增】A2A 协作
    A2A = "a2a"  # A2A 消息容器

# ... 其余现有代码保持不变 ...

def create_a2a_message(a2a_payload: dict) -> WSMessage:
    return WSMessage(
        type=MessageType.A2A.value,
        payload=a2a_payload
    )
```

## 桌面应用 UI 扩展

### 新增：agent_network_panel.py

```python
# apps/desktop/src/ui/agent_network_panel.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QLabel, QListWidget, QListWidgetItem, QSplitter,
                              QTextEdit, QGroupBox, QFormLayout, QComboBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import Optional

# 这里放 UI 实现
```

### 修改：main_window.py

集成 Agent Network 面板到侧边栏。

## 为未来预留的扩展点

### 1. 深度协作协议扩展

- `workspace.py` 已为共享工作记忆预留
- 协议预留 `WORKSPACE_SYNC` 消息类型
- 未来可添加任务协商、冲突解决机制

### 2. 内生信任体系预留

预留 `src/identity/` 目录：
- `did.py` - DID 身份管理
- `credentials.py` - 可验证凭证
- `reputation.py` - 信誉系统

### 3. 多模态经济交互预留

预留 `src/eonomy/` 目录：
- `payment.py` - 支付接口
- `settlement.py` - 结算逻辑
- `sla.py` - 服务等级协议

## 实现优先级

### Phase 1: MVP（本次）
- [ ] 角色与能力系统
- [ ] 任务系统（创建、拆分、分配）
- [ ] 本地 Agent 发现与注册
- [ ] 任务协调器（分配、收集、汇总）
- [ ] 基础 A2A 协议
- [ ] 桌面 UI（Agent 列表、任务状态）

### Phase 2: 网络协作
- [ ] 扩展 Gateway 支持 A2A 消息路由
- [ ] 网络 Agent 发现
- [ ] 跨设备任务分配

### Phase 3: 未来需求
- [ ] 共享工作区
- [ ] 身份与凭证
- [ ] 经济交互

## 总结

本设计在现有 OpenToad 架构基础上，轻量级扩展支持 A2A 协作，同时为三个核心未来需求预留扩展点：
1. **深度协作协议** → 通过 `workspace.py` 和协议预留
2. **内生信任体系** → 通过 `src/identity/` 目录预留
3. **多模态经济交互** → 通过 `src/economy/` 目录预留
