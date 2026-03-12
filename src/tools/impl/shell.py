import asyncio
from ..base import Tool, ToolResult, ToolDefinition, ToolParameter


class ShellTool:
    definition = ToolDefinition(
        name="shell",
        description="Execute shell commands",
        parameters={
            "command": ToolParameter(type="string", description="The shell command to execute", required=True)
        }
    )
    
    async def execute(self, params: dict) -> ToolResult:
        command = params["command"]
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
            output = stdout.decode() or stderr.decode()
            return ToolResult(
                success=proc.returncode == 0,
                output=output
            )
        except asyncio.TimeoutError:
            return ToolResult(success=False, output="", error="Command timed out")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
