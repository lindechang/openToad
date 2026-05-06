# src/agent_network/__init__.py
from .role import (
    AgentRole, AgentCapability, AgentInfo
)
from .task import (
    TaskStatus, Task, TaskResult
)
from .discovery import (
    LocalAgentRegistry, NetworkAgentDiscovery
)
from .orchestrator import TaskOrchestrator
from .protocol import (
    A2AMessageType, A2AMessage,
    create_discovery_request, create_discovery_response,
    create_task_assign, create_task_result
)
from .a2a_handler import A2AMessageHandler
from .workspace import (
    Workspace, WorkspaceNote, WorkspaceFile,
    WorkspaceActivity, WorkspaceManager
)
from .evolution import (
    EvolutionType, EvolutionState, Metric, Evolution,
    MetricsCollector, Optimizer, EvolutionRegistry,
    EvolutionEngine, get_evolution_engine, init_evolution_system
)

__all__ = [
    # Role
    'AgentRole', 'AgentCapability', 'AgentInfo',
    # Task
    'TaskStatus', 'Task', 'TaskResult',
    # Discovery
    'LocalAgentRegistry', 'NetworkAgentDiscovery',
    # Orchestrator
    'TaskOrchestrator',
    # Protocol
    'A2AMessageType', 'A2AMessage',
    'create_discovery_request', 'create_discovery_response',
    'create_task_assign', 'create_task_result',
    # A2A Handler
    'A2AMessageHandler',
    # Workspace
    'Workspace', 'WorkspaceNote', 'WorkspaceFile',
    'WorkspaceActivity', 'WorkspaceManager',
    # Evolution
    'EvolutionType', 'EvolutionState', 'Metric', 'Evolution',
    'MetricsCollector', 'Optimizer', 'EvolutionRegistry',
    'EvolutionEngine', 'get_evolution_engine', 'init_evolution_system'
]
