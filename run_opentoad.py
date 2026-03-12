#!/usr/bin/env python3

from src.providers import create_provider
from src.agent import Agent, AgentConfig
from src.tools import register_default_tools
import asyncio
import json
import os

register_default_tools()

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# 加载配置
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    return {}

# 保存配置
def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        print("\nConfiguration saved successfully!")
    except Exception as e:
        print(f"Error saving config: {e}")

# 简单的 CLI 界面
print('OpenToad - Self-Sustainable AI Assistant')
print('')

# 加载保存的配置
config = load_config()
saved_provider = config.get("provider")
saved_api_key = config.get("api_key")
saved_model = config.get("model")

if saved_provider and saved_api_key:
    print(f"Loaded saved configuration:")
    print(f"  Provider: {saved_provider}")
    print(f"  Model: {saved_model}")
    print(f"  API Key: {'*' * len(saved_api_key)}")
    use_saved = input("Use saved configuration? (y/n): ").lower()
    if use_saved == "y":
        provider = saved_provider
        api_key = saved_api_key
        model = saved_model
    else:
        # 选择提供商
        print('')
        print('Available providers:')
        print('1. anthropic')
        print('2. openai')
        print('3. deepseek')
        print('4. ollama')

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
        
        # 保存新配置
        new_config = {
            "provider": provider,
            "api_key": api_key,
            "model": model
        }
        save_config(new_config)
else:
    # 选择提供商
    print('Available providers:')
    print('1. anthropic')
    print('2. openai')
    print('3. deepseek')
    print('4. ollama')

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
    
    # 保存新配置
    new_config = {
        "provider": provider,
        "api_key": api_key,
        "model": model
    }
    save_config(new_config)

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
