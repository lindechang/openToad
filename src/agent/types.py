from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentConfig:
    model: str
    temperature: float = 0.7
    max_iterations: int = 10


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass
class AgentState:
    messages: list = field(default_factory=list)
    steps: list = field(default_factory=list)
