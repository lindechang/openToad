from pathlib import Path
from ..base import Tool, ToolResult, ToolDefinition, ToolParameter


class FilesystemTool:
    definition = ToolDefinition(
        name="filesystem",
        description="Read, write, or list files",
        parameters={
            "action": ToolParameter(type="string", description="Action: read, write, list", required=True),
            "path": ToolParameter(type="string", description="File path", required=True),
            "content": ToolParameter(type="string", description="Content to write", required=False)
        }
    )
    
    async def execute(self, params: dict) -> ToolResult:
        action = params["action"]
        path = Path(params["path"])
        
        try:
            if action == "read":
                if not path.exists():
                    return ToolResult(success=False, output="", error="File not found")
                content = path.read_text(encoding="utf-8")
                return ToolResult(success=True, output=content)
            elif action == "write":
                path.write_text(params.get("content", ""), encoding="utf-8")
                return ToolResult(success=True, output="File written")
            elif action == "list":
                if not path.is_dir():
                    return ToolResult(success=False, output="", error="Not a directory")
                files = "\n".join(p.name for p in path.iterdir())
                return ToolResult(success=True, output=files)
            else:
                return ToolResult(success=False, output="", error="Unknown action")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
