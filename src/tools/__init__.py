from .registry import ToolRegistry, global_tools
from .impl.shell import ShellTool
from .impl.filesystem import FilesystemTool
from .impl.extended import (
    WebSearchTool,
    CalculatorTool,
    ReadFileTool,
    WriteFileTool,
    ListDirTool,
    DateTimeTool,
)
from .base import Tool, ToolResult, ToolDefinition, ToolParameter


def register_default_tools() -> None:
    global_tools.register(ShellTool())
    global_tools.register(FilesystemTool())
    global_tools.register(WebSearchTool())
    global_tools.register(CalculatorTool())
    global_tools.register(ReadFileTool())
    global_tools.register(WriteFileTool())
    global_tools.register(ListDirTool())
    global_tools.register(DateTimeTool())


__all__ = [
    "ToolRegistry",
    "global_tools",
    "register_default_tools",
    "Tool",
    "ToolResult",
    "ToolDefinition",
    "ToolParameter",
    "ShellTool",
    "FilesystemTool",
    "WebSearchTool",
    "CalculatorTool",
    "ReadFileTool",
    "WriteFileTool",
    "ListDirTool",
    "DateTimeTool",
]
