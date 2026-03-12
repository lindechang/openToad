from .base import Tool, ToolDefinition


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        self._tools[tool.definition.name] = tool
    
    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)
    
    def list(self) -> list[ToolDefinition]:
        return [t.definition for t in self._tools.values()]
    
    def has(self, name: str) -> bool:
        return name in self._tools


global_tools = ToolRegistry()
