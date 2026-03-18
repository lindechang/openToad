import json
import re
from typing import Optional, Callable
from ..providers import LLMProvider, Message, ChatOptions
from ..tools import global_tools
from .types import AgentConfig, AgentState, ToolCall
from .prompt import build_system_prompt


class Agent:
    def __init__(self, provider: LLMProvider, config: AgentConfig):
        self.provider = provider
        self.config = config
    
    async def run(self, user_input: str) -> str:
        return await self._run_with_prompt(user_input)
    
    async def greet(self) -> str:
        return await self._run_with_prompt("")
    
    async def _run_with_prompt(self, user_input: str) -> str:
        profile_context = ""
        from ..profile import load_profile
        profile = load_profile()
        if profile.name:
            profile_context = profile.to_prompt_context()
        
        system_prompt = build_system_prompt(profile_context)
        
        if not user_input:
            user_input = "你好，请介绍一下自己"
        
        state = AgentState(
            messages=[
                Message(role="system", content=system_prompt),
                Message(role="user", content=user_input)
            ]
        )
        
        for _ in range(self.config.max_iterations):
            if self.config.stream:
                response = await self._run_stream(state)
            else:
                response = self.provider.chat(ChatOptions(
                    model=self.config.model,
                    messages=state.messages,
                    temperature=self.config.temperature
                ))
                response = response.content
            
            state.messages.append(Message(role="assistant", content=response))
            
            tool_call = self._parse_tool_call(response)
            if not tool_call:
                return response
            
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
    
    async def _run_stream(self, state: AgentState) -> str:
        full_content = []
        
        def on_chunk(text: str):
            full_content.append(text)
            try:
                print(text, end="", flush=True)
            except (UnicodeEncodeError, AttributeError):
                pass
        
        response = self.provider.chat_stream(
            ChatOptions(
                model=self.config.model,
                messages=state.messages,
                temperature=self.config.temperature
            ),
            on_chunk
        )
        try:
            print()
        except UnicodeEncodeError:
            pass
        return "".join(full_content) if full_content else response.content
    
    def _parse_tool_call(self, content: str) -> Optional[ToolCall]:
        match = re.search(r"```json\n(.*?)\n```", content, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                return ToolCall(name=data["name"], arguments=data.get("arguments", {}))
            except (json.JSONDecodeError, KeyError):
                pass
        return None
