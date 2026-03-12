#!/usr/bin/env python3

from src.providers import create_provider
from src.agent import Agent, AgentConfig
from src.tools import register_default_tools
import asyncio
import json
import os
import sys
import argparse

register_default_tools()

parser = argparse.ArgumentParser(description="OpenToad - AI Assistant")
parser.add_argument("--stream", action="store_true", help="Enable streaming output")
parser.add_argument("--no-stream", action="store_true", help="Disable streaming output")
args, unknown = parser.parse_known_args()

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

PROVIDERS = {
    "1": ("anthropic", "Claude", "claude-3-5-sonnet-20241022"),
    "2": ("openai", "GPT", "gpt-4o"),
    "3": ("deepseek", "DeepSeek", "deepseek-chat"),
    "4": ("qianwen", "Qwen (通义千问)", "qwen-turbo"),
    "5": ("ernie", "ERNIE (文心一言)", "ernie-bot"),
    "6": ("hunyuan", "Hunyuan (混元)", "hunyuan-latest"),
    "7": ("zhipu", "Zhipu (智谱)", "glm-4"),
    "8": ("kimi", "Kimi (月之暗面)", "moonshot-v1-8k"),
    "9": ("gemini", "Gemini", "gemini-1.5-flash"),
    "10": ("ollama", "Ollama (本地)", "llama2"),
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    return {}


def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        print("\nConfiguration saved successfully!")
    except Exception as e:
        print(f"Error saving config: {e}")


def print_banner():
    print("=" * 50)
    print("  OpenToad - Self-Sustainable AI Assistant")
    print("=" * 50)
    print()


def print_help():
    print("\nCommands:")
    print("  /help     - Show this help message")
    print("  /clear    - Clear conversation history")
    print("  /config   - Show current configuration")
    print("  /models   - List available models")
    print("  /exit     - Exit the program")
    print()


def list_models(provider):
    from src.providers import (
        AnthropicProvider, OpenAIProvider, DeepSeekProvider,
        QianwenProvider, ErnieProvider, HunyuanProvider,
        ZhipuProvider, KimiProvider, GeminiProvider, OllamaProvider
    )
    models_map = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "deepseek": DeepSeekProvider,
        "qianwen": QianwenProvider,
        "ernie": ErnieProvider,
        "hunyuan": HunyuanProvider,
        "zhipu": ZhipuProvider,
        "kimi": KimiProvider,
        "gemini": GeminiProvider,
        "ollama": OllamaProvider,
    }
    if provider in models_map:
        try:
            p = models_map[provider]("dummy")
            models = p.list_models()
            print(f"\nAvailable models for {provider}:")
            for m in models:
                print(f"  - {m}")
        except Exception as e:
            print(f"Error listing models: {e}")


def select_provider():
    print("Available providers:")
    for num, (key, name, _) in PROVIDERS.items():
        print(f"  {num}. {name}")
    print()
    
    while True:
        try:
            choice = input("Enter provider number: ").strip()
            if choice in PROVIDERS:
                return PROVIDERS[choice]
            print("Invalid choice. Please try again.")
        except (ValueError, KeyboardInterrupt):
            print("\nInvalid input.")
            return PROVIDERS["1"]


print_banner()

config = load_config()
saved_provider = config.get("provider")
saved_api_key = config.get("api_key")
saved_model = config.get("model")

api_key = ""

if saved_provider and saved_api_key:
    print(f"Loaded saved configuration:")
    print(f"  Provider: {saved_provider}")
    print(f"  Model: {saved_model}")
    print(f"  API Key: {'*' * min(len(saved_api_key), 12)}")
    use_saved = input("Use saved configuration? (y/n): ").lower()
    if use_saved == "y":
        provider, provider_name, model = saved_provider, saved_provider, saved_model
        api_key = saved_api_key
    else:
        provider_key, provider_name, model = select_provider()
        provider = provider_key
        
        if provider != "ollama":
            api_key = input(f"Enter API key for {provider_name}: ").strip()
        else:
            api_key = "ollama"
        
        new_config = {"provider": provider, "api_key": api_key, "model": model}
        save_config(new_config)
else:
    provider_key, provider_name, model = select_provider()
    provider = provider_key
    
    if provider != "ollama":
        api_key = input(f"Enter API key for {provider_name}: ").strip()
    else:
        api_key = "ollama"
    
    new_config = {"provider": provider, "api_key": api_key, "model": model}
    save_config(new_config)

use_stream = args.stream if args.stream or args.no_stream else True

if provider == "ollama" and not api_key:
    api_key = "ollama"

print()
print(f"Provider: {provider}, Model: {model}")
print(f"Streaming: {'Enabled' if use_stream else 'Disabled'}")
print("Type '/help' for commands or '/exit' to quit.")
print()

llm = create_provider(provider, api_key)
agent = Agent(llm, AgentConfig(model=model or "default", stream=use_stream))
conversation_history = []

while True:
    try:
        user_input = input("\n> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nExiting...")
        break
    
    if not user_input:
        continue
    
    if user_input.lower() in ["/exit", "/quit", "exit", "quit"]:
        print("Goodbye!")
        break
    
    if user_input.lower() == "/help":
        print_help()
        continue
    
    if user_input.lower() == "/clear":
        conversation_history = []
        print("Conversation history cleared.")
        continue
    
    if user_input.lower() == "/config":
        print(f"\nCurrent configuration:")
        print(f"  Provider: {provider}")
        print(f"  Model: {model}")
        print(f"  API Key: {'*' * min(len(api_key), 12)}")
        continue
    
    if user_input.lower() == "/models":
        list_models(provider)
        continue
    
    conversation_history.append({"role": "user", "content": user_input})
    
    try:
        print()
        if use_stream:
            response = asyncio.run(agent.run(user_input))
        else:
            response = asyncio.run(agent.run(user_input))
            print(response)
        conversation_history.append({"role": "assistant", "content": response if not use_stream else ""})
    except Exception as e:
        print(f"Error: {e}")
