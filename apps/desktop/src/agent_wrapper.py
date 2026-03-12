import sys
import os

# 添加主项目路径到 Python 搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# 从 src 目录导入模块
from src.providers import create_provider
from src.agent import Agent, AgentConfig
from src.tools import register_default_tools, global_tools
from src.providers.types import ChatOptions, Message
import asyncio

class AgentWrapper:
    def __init__(self, provider: str, api_key: str, model: str):
        register_default_tools()
        
        self.provider = create_provider(provider, api_key)
        self.agent = Agent(self.provider, AgentConfig(model=model))
    
    async def chat(self, message: str) -> str:
        return await self.agent.run(message)
    
    def chat_sync(self, message: str) -> str:
        return asyncio.run(self.chat(message))
