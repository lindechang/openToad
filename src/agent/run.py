import json
import re
from typing import Optional
from ..providers import LLMProvider, Message, ChatOptions
from ..tools import global_tools
from .types import AgentConfig, AgentState, ToolCall
from .prompt import build_system_prompt


class Agent:
    def __init__(self, provider: LLMProvider, config: AgentConfig):
        self.provider = provider
        self.config = config
    
    async def run(self, user_input: str) -> str:
        state = AgentState(
            messages=[
                Message(role="system", content=build_system_prompt()),
                Message(role="user", content=user_input)
            ]
        )
        
        for _ in range(self.config.max_iterations):
            response = self.provider.chat(ChatOptions(
                model=self.config.model,
                messages=state.messages,
                temperature=self.config.temperature
            ))
            
            state.messages.append(Message(role="assistant", content=response.content))
            
            tool_call = self._parse_tool_call(response.content)
            if not tool_call:
                return response.content
            
            tool = global_tools.get(tool_call.name)
            if not tool:
                state.messages.append(Message(
                    role="user", 
                    content=f"Tool {tool_call.name} not found"
                ))
                continue
            
            result = await tool.execute(tool_call.arguments)
            
            state.messages.append(Message(
                role="user",
                content=f"Observation: {result.output}" if result.success else f"Error: {result.error}"
            ))
        
        return "Max iterations reached"
    
    def _parse_tool_call(self, content: str) -> Optional[ToolCall]:
        match = re.search(r"```json\n(.*?)\n```", content, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                return ToolCall(name=data["name"], arguments=data.get("arguments", {}))
            except (json.JSONDecodeError, KeyError):
                pass
        return None
