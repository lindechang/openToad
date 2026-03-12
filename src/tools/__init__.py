from .registry import ToolRegistry, global_tools
from .impl.shell import ShellTool
from .impl.filesystem import FilesystemTool
from .base import Tool, ToolResult, ToolDefinition, ToolParameter


def register_default_tools() -> None:
    global_tools.register(ShellTool())
    global_tools.register(FilesystemTool())


__all__ = [
    "ToolRegistry",
    "global_tools",
    "register_default_tools",
    "Tool",
    "ToolResult",
    "ToolDefinition",
    "ToolParameter",
]
