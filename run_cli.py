#!/usr/bin/env python3

from src.providers import create_provider
from src.agent import Agent, AgentConfig
from src.tools import register_default_tools
import sys
import asyncio

register_default_tools()

# 从命令行参数获取配置
provider = sys.argv[1]
model = sys.argv[2]
api_key = sys.argv[3] if len(sys.argv) > 3 else ""

print('\nOpenToad - Self-Sustainable AI Assistant')
print(f'Provider: {provider}, Model: {model}')
print('Type \'exit\' or \'quit\' to stop.\n')

# 初始化 agent
llm = create_provider(provider, api_key)
agent = Agent(llm, AgentConfig(model=model))

# 主循环
while True:
    user_input = input('\n> ')
    if user_input in ('