import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.providers import create_provider
from src.agent import Agent, AgentConfig
from src.tools import register_default_tools, global_tools
from src.providers.types import ChatOptions, Message
import asyncio

class AgentWrapper:
    def __init__(self, provider: str, api_key: str, model: str, stream: bool = True):
        register_default_tools()
        
        self.stream_enabled = stream
        self.provider = create_provider(provider, api_key)
        self.agent = Agent(self.provider, AgentConfig(model=model, stream=stream))
    
    async def chat(self, message: str) -> str:
        return await self.agent.run(message)
    
    def chat_sync(self, message: str) -> str:
        return asyncio.run(self.chat(message))
    
    def chat_stream(self, message: str, callback) -> str:
        return asyncio.run(self._chat_stream_async(message, callback))
    
    async def _chat_stream_async(self, message: str, callback) -> str:
        return await self.agent.run(message)
    
    def greet(self) -> str:
        return asyncio.run(self.agent.greet())
