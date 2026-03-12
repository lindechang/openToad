import asyncio
import aiohttp
from ..base import Tool, ToolResult, ToolDefinition, ToolParameter


class WebSearchTool:
    definition = ToolDefinition(
        name="web_search",
        description="Search the web for information",
        parameters={
            "query": ToolParameter(type="string", description="The search query", required=True),
            "num_results": ToolParameter(type="integer", description="Number of results to return", required=False)
        }
    )
    
    async def execute(self, params: dict) -> ToolResult:
        query = params.get("query", "")
        num = params.get("num_results", 5)
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://ddg-api.vercel.app/search"
                params = {"q": query, "num": num}
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        results = []
                        for item in data:
                            results.append(f"- {item.get('title', '')}\n  {item.get('url', '')}\n  {item.get('snippet', '')}")
                        output = "\n\n".join(results) if results else "No results found"
                        return ToolResult(success=True, output=output)
                    return ToolResult(success=False, output="", error=f"API returned {resp.status}")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))


class CalculatorTool:
    definition = ToolDefinition(
        name="calculator",
        description="Perform mathematical calculations",
        parameters={
            "expression": ToolParameter(type="string", description="Mathematical expression to evaluate", required=True)
        }
    )
    
    async def execute(self, params: dict) -> ToolResult:
        expression = params.get("expression", "")
        try:
            allowed_chars = set("0123456789+-*/.()% ")
            if not all(c in allowed_chars for c in expression):
                return ToolResult(success=False, output="", error="Invalid characters in expression")
            result = eval(expression)
            return ToolResult(success=True, output=str(result))
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))


class ReadFileTool:
    definition = ToolDefinition(
        name="read_file",
        description="Read contents of a file",
        parameters={
            "path": ToolParameter(type="string", description="Path to the file", required=True),
            "lines": ToolParameter(type="integer", description="Number of lines to read", required=False),
            "offset": ToolParameter(type="integer", description="Line offset to start reading from", required=False)
        }
    )
    
    async def execute(self, params: dict) -> ToolResult:
        path = params.get("path", "")
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = params.get("lines")
                offset = params.get("offset", 0)
                if lines or offset:
                    all_lines = f.readlines()
                    start = offset
                    end = len(all_lines) if not lines else offset + lines
                    content = "".join(all_lines[start:end])
                else:
                    content = f.read()
            return ToolResult(success=True, output=content)
        except FileNotFoundError:
            return ToolResult(success=False, output="", error=f"File not found: {path}")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))


class WriteFileTool:
    definition = ToolDefinition(
        name="write_file",
        description="Write content to a file",
        parameters={
            "path": ToolParameter(type="string", description="Path to the file", required=True),
            "content": ToolParameter(type="string", description="Content to write", required=True),
            "mode": ToolParameter(type="string", description="Write mode: 'overwrite' or 'append'", required=False)
        }
    )
    
    async def execute(self, params: dict) -> ToolResult:
        path = params.get("path", "")
        content = params.get("content", "")
        mode = params.get("mode", "overwrite")
        try:
            mode_str = "a" if mode == "append" else "w"
            with open(path, mode_str, encoding="utf-8") as f:
                f.write(content)
            return ToolResult(success=True, output=f"Successfully wrote to {path}")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))


class ListDirTool:
    definition = ToolDefinition(
        name="list_dir",
        description="List files in a directory",
        parameters={
            "path": ToolParameter(type="string", description="Directory path", required=False),
            "all": ToolParameter(type="boolean", description="Show hidden files", required=False)
        }
    )
    
    async def execute(self, params: dict) -> ToolResult:
        import os
        path = params.get("path", ".")
        show_all = params.get("all", False)
        try:
            entries = os.listdir(path)
            if not show_all:
                entries = [e for e in entries if not e.startswith(".")]
            entries.sort()
            output = "\n".join(entries)
            return ToolResult(success=True, output=output)
        except FileNotFoundError:
            return ToolResult(success=False, output="", error=f"Directory not found: {path}")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))


class DateTimeTool:
    definition = ToolDefinition(
        name="datetime",
        description="Get current date and time",
        parameters={
            "timezone": ToolParameter(type="string", description="Timezone (e.g., Asia/Shanghai, UTC)", required=False),
            "format": ToolParameter(type="string", description="Output format", required=False)
        }
    )
    
    async def execute(self, params: dict) -> ToolResult:
        from datetime import datetime
        import pytz
        tz_name = params.get("timezone", "UTC")
        fmt = params.get("format", "%Y-%m-%d %H:%M:%S %Z")
        try:
            if tz_name:
                tz = pytz.timezone(tz_name)
                dt = datetime.now(tz)
            else:
                dt = datetime.now()
            return ToolResult(success=True, output=dt.strftime(fmt))
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
