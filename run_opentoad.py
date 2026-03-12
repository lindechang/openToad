#!/usr/bin/env python3

from src.providers import create_provider
from src.agent import Agent, AgentConfig
from src.tools import register_default_tools
import asyncio

register_default_tools()

# 简单的 CLI 界面
print('OpenToad - Self-Sustainable AI Assistant')
print('')
print('Available providers:')
print('1. anthropic')
print('2. openai')
print('3. deepseek')
print('4. ollama')

# 选择提供商
provider_choice = int(input('Enter provider number: '))
providers = ['anthropic', 'openai', 'deepseek', 'ollama']
provider = providers[provider_choice - 1]

# 选择模型
models = {
    'anthropic': 'claude-3-5-sonnet-20241022',
    'openai': 'gpt-4o',
    'deepseek': 'deepseek-chat',
    'ollama': 'llama2'
}
model = models.get(provider, 'default')

# 获取 API key
api_key = ''
if provider != 'ollama':
    api_key = input('Enter API key: ')

print('')
print(f'Provider: {provider}, Model: {model}')
print('Type \'exit\' or \'quit\' to stop.')
print('')

# 初始化 agent
llm = create_provider(provider, api_key)
agent = Agent(llm, AgentConfig(model=model))

# 主循环
while True:
    user_input = input('\n> ')
    if user_input == 'exit' or user_input == 'quit':
        break
    
    # 运行 agent
    response = asyncio.run(agent.run(user_input))
    print(response)
