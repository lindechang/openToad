from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class ToolParameter:
    type: str
    description: str
    required: bool = False


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, ToolParameter]


@dataclass
class ToolResult:
    success: bool
    output: str
    error: str | None = None


@runtime_checkable
class Tool(Protocol):
    definition: ToolDefinition
    
    async def execute(self, params: dict) -> ToolResult: ...
