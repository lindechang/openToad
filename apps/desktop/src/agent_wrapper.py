import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.providers import create_provider
from src.agent import Agent, AgentConfig
from src.tools import register_default_tools, global_tools
from src.providers.types import ChatOptions, Message
from src.memory import MemoryCore, MemoryStorage
from src.crypto.cipher import CryptoManager
import asyncio

class AgentWrapper:
    def __init__(self, provider: str, api_key: str, model: str, stream: bool = True, session=None):
        register_default_tools()
        
        self.stream_enabled = stream
        self.provider = create_provider(provider, api_key)
        self.agent = Agent(self.provider, AgentConfig(model=model, stream=stream))
        self.model = model
        self._session = session
        self.memory = self._create_memory()
    
    def _create_memory(self) -> MemoryCore:
        from pathlib import Path
        storage = None
        user_id = None
        if self._session:
            user_id = getattr(self._session, 'user_id', None)
        
        if self._session and self._session.encryption_key:
            crypto = CryptoManager(self._session.encryption_key)
            storage = MemoryStorage(crypto=crypto, user_id=user_id)
        return MemoryCore(storage=storage)
    
    def update_session(self, session):
        """更新会话，用于登录后启用加密"""
        self._session = session
        self.memory = self._create_memory()
    
    async def chat(self, message: str) -> str:
        return await self.agent.run(message)
    
    def chat_sync(self, message: str) -> str:
        return asyncio.run(self.chat(message))
    
    def chat_stream(self, message: str, callback) -> str:
        messages = [
            Message(role="user", content=message)
        ]
        
        full_content = []
        
        def on_chunk(text: str):
            full_content.append(text)
            callback(text)
        
        if self.stream_enabled:
            response = self.provider.chat_stream(
                ChatOptions(model=self.model, messages=messages),
                on_chunk
            )
        else:
            response = self.provider.chat(
                ChatOptions(model=self.model, messages=messages)
            )
            callback(response.content)
        
        return "".join(full_content) if full_content else response.content
    
    def greet(self) -> str:
        return asyncio.run(self.agent.greet())
