from dataclasses import dataclass
from typing import Protocol, runtime_checkable, Optional, Dict


@dataclass
class ToolParameter:
    type: str
    description: str
    required: bool = False


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: Dict[str, ToolParameter]


@dataclass
class ToolResult:
    success: bool
    output: str
    error: Optional[str] = None


@runtime_checkable
class Tool(Protocol):
    definition: ToolDefinition
    
    async def execute(self, params: dict) -> ToolResult: ...
