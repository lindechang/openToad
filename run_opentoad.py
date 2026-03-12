#!/usr/bin/env python3

from src.providers import create_provider
from src.agent import Agent, AgentConfig
from src.tools import register_default_tools
import asyncio
import json
import os
import sys
import argparse
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.theme import Theme
    from rich import box
    console = Console()
except ImportError:
    console = None
    print("Warning: rich not installed. Using basic terminal.")
    print("Install with: pip install rich")

register_default_tools()

parser = argparse.ArgumentParser(description="OpenToad - AI Assistant")
parser.add_argument("--stream", action="store_true", help="Enable streaming output")
parser.add_argument("--no-stream", action="store_true", help="Disable streaming output")
args, unknown = parser.parse_known_args()

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")

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
        except Exception:
            pass
    return {}


def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        if console:
            console.print("[green]✓[/green] Configuration saved successfully!")
        else:
            print("Configuration saved successfully!")
    except Exception as e:
        if console:
            console.print(f"[red]Error saving config: {e}[/red]")
        else:
            print(f"Error saving config: {e}")


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def print_history():
    history = load_history()
    if not history:
        if console:
            console.print("[dim]No conversation history.[/dim]")
        else:
            print("No conversation history.")
        return
    
    if console:
        console.print(f"\n[cyan]Conversation History ({len(history)} messages):[/cyan]\n")
        for i, msg in enumerate(history[-10:]):
            role = msg.get("role", "user")
            content = msg.get("content", "")[:100]
            if role == "user":
                console.print(f"[green]You:[/green] {content}")
            else:
                console.print(f"[blue]AI:[/blue] {content}")
            console.print()
    else:
        print(f"\nConversation History ({len(history)} messages):")
        for msg in history[-10:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")[:100]
            print(f"{role}: {content}")


def print_banner():
    console = None
    try:
        from rich.console import Console
        console = Console()
    except ImportError:
        pass
    
    if console:
        console.clear()
        from rich.panel import Panel
        from rich.text import Text
        
        banner_text = Text("🐸 OpenToad", style="bold cyan")
        banner_text.append(" - Self-Sustainable AI Assistant", style="cyan")
        
        from rich.box import DOUBLE
        panel = Panel(
            banner_text,
            border_style="green",
            box=DOUBLE,
            expand=False,
            padding=(1, 4)
        )
        console.print(panel)
        console.print()
        
        # System information
        import platform
        import sys
        from rich.table import Table
        
        from rich.box import SIMPLE
        sys_info = Table(box=SIMPLE, expand=False, show_header=False)
        sys_info.add_row("Platform:", platform.platform())
        sys_info.add_row("Python:", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        console.print(sys_info)
        console.print()
    else:
        print("=" * 55)
        print("  🐸 OpenToad - Self-Sustainable AI Assistant")
        print("=" * 55)
        print()


def print_help():
    console = None
    Table = None
    box = None
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.box import box
        console = Console()
    except ImportError:
        pass
    
    if console and Table and box:
        table = Table(title="Available Commands", box=box.ROUNDED)
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_row("/help", "Show this help message")
        table.add_row("/clear", "Clear conversation history")
        table.add_row("/history", "Show conversation history")
        table.add_row("/config", "Show current configuration")
        table.add_row("/models", "List available models")
        table.add_row("/tools", "List available tools")
        table.add_row("/exit, /quit", "Exit the program")
        console.print(table)
    else:
        print("\nCommands:")
        print("  /help     - Show this help message")
        print("  /clear    - Clear conversation history")
        print("  /history  - Show conversation history")
        print("  /config   - Show current configuration")
        print("  /models   - List available models")
        print("  /tools    - List available tools")
        print("  /exit     - Exit the program")


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
            
            if console:
                table = Table(title=f"Available Models - {provider}", box=box.ROUNDED)
                table.add_column("Model", style="green")
                for m in models:
                    table.add_row(m)
                console.print(table)
            else:
                print(f"\nAvailable models for {provider}:")
                for m in models:
                    print(f"  - {m}")
        except Exception as e:
            if console:
                console.print(f"[red]Error listing models: {e}[/red]")
            else:
                print(f"Error listing models: {e}")


def list_tools():
    from src.tools import global_tools
    
    if console:
        table = Table(title="Available Tools", box=box.ROUNDED)
        table.add_column("Tool", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        for tool_def in global_tools.list():
            table.add_row(tool_def.name, tool_def.description)
        console.print(table)
    else:
        print("\nAvailable tools:")
        for tool_def in global_tools.list():
            print(f"  - {tool_def.name}: {tool_def.description}")


def select_provider():
    if console:
        table = Table(title="Select Provider", box=box.ROUNDED)
        table.add_column("#", style="cyan bold", no_wrap=True)
        table.add_column("Provider", style="green")
        table.add_column("Model", style="white")
        
        for num, (key, name, model) in PROVIDERS.items():
            table.add_row(num, name, model)
        console.print(table)
    else:
        print("Available providers:")
        for num, (key, name, _) in PROVIDERS.items():
            print(f"  {num}. {name}")
    
    while True:
        try:
            if console:
                choice = Prompt.ask("[cyan]Enter provider number[/cyan]", default="1")
            else:
                choice = input("Enter provider number: ").strip()
            
            if choice in PROVIDERS:
                return PROVIDERS[choice]
            
            if console:
                console.print("[red]Invalid choice. Please try again.[/red]")
            else:
                print("Invalid choice. Please try again.")
        except (ValueError, KeyboardInterrupt):
            return PROVIDERS["1"]


def print_config(provider, model, api_key):
    if console:
        table = Table(title="Current Configuration", box=box.ROUNDED)
        table.add_column("Setting", style="cyan bold", no_wrap=True)
        table.add_column("Value", style="white")
        
        provider_name = PROVIDERS.get(str(list(PROVIDERS.keys())[list([k for k, v in PROVIDERS.items() if v[0] == provider])[0] if provider in [v[0] for v in PROVIDERS.values()] else "1"]), (provider, provider, ""))
        
        table.add_row("Provider", provider)
        table.add_row("Model", model or "default")
        table.add_row("API Key", "*" * min(len(api_key), 12) if api_key else "N/A")
        table.add_row("Streaming", "Enabled" if use_stream else "Disabled")
        
        console.print(table)
    else:
        print(f"\nCurrent configuration:")
        print(f"  Provider: {provider}")
        print(f"  Model: {model}")
        print(f"  API Key: {'*' * min(len(api_key), 12)}")
        print(f"  Streaming: {'Enabled' if use_stream else 'Disabled'}")


def print_welcome(provider, model):
    if console:
        panel = Panel(
            f"[bold cyan]Provider:[/bold cyan] {provider}\n"
            f"[bold cyan]Model:[/bold cyan] {model}\n"
            f"[bold cyan]Streaming:[/bold cyan] {'Enabled' if use_stream else 'Disabled'}",
            title="🐸 OpenToad Ready",
            border_style="green",
            box=box.ROUNDED
        )
        console.print(panel)
        console.print("\n[dim]Type [cyan]/help[/cyan] for commands or [cyan]/exit[/cyan] to quit.[/dim]\n")
    else:
        print(f"\nProvider: {provider}, Model: {model}")
        print(f"Streaming: {'Enabled' if use_stream else 'Disabled'}")
        print("Type '/help' for commands or '/exit' to quit.")


print_banner()

config = load_config()
saved_provider = config.get("provider")
saved_api_key = config.get("api_key")
saved_model = config.get("model")

api_key = ""

if saved_provider and saved_api_key:
    if console:
        console.print(f"[yellow]Found saved configuration:[/yellow]")
        console.print(f"  [cyan]Provider:[/cyan] {saved_provider}")
        console.print(f"  [cyan]Model:[/cyan] {saved_model}")
        console.print(f"  [cyan]API Key:[/cyan] {'*' * min(len(saved_api_key), 12)}")
        use_saved = Confirm.ask("[cyan]Use saved configuration?[/cyan]", default=True)
    else:
        print(f"Loaded saved configuration:")
        print(f"  Provider: {saved_provider}")
        print(f"  Model: {saved_model}")
        print(f"  API Key: {'*' * min(len(saved_api_key), 12)}")
        use_saved = input("Use saved configuration? (y/n): ").lower() == "y"
    
    if use_saved:
        provider, provider_name, model = saved_provider, saved_provider, saved_model
        api_key = saved_api_key
    else:
        provider_key, provider_name, model = select_provider()
        provider = provider_key
        
        if provider != "ollama":
            if console:
                api_key = Prompt.ask(f"[cyan]Enter API key for {provider_name}[/cyan]", password=True)
            else:
                api_key = input(f"Enter API key for {provider_name}: ").strip()
        else:
            api_key = "ollama"
        
        new_config = {"provider": provider, "api_key": api_key, "model": model}
        save_config(new_config)
else:
    provider_key, provider_name, model = select_provider()
    provider = provider_key
    
    if provider != "ollama":
        if console:
            api_key = Prompt.ask(f"[cyan]Enter API key for {provider_name}[/cyan]", password=True)
        else:
            api_key = input(f"Enter API key for {provider_name}: ").strip()
    else:
        api_key = "ollama"
    
    new_config = {"provider": provider, "api_key": api_key, "model": model}
    save_config(new_config)

use_stream = args.stream if args.stream or args.no_stream else True

if provider == "ollama" and not api_key:
    api_key = "ollama"

print_welcome(provider, model)

llm = create_provider(provider, api_key)
agent = Agent(llm, AgentConfig(model=model or "default", stream=use_stream))
conversation_history = []

while True:
    try:
        if console:
            user_input = Prompt.ask("[bold green]You[/bold green] [dim]>>[/dim] ")
        else:
            user_input = input("\nYou >> ").strip()
    except (EOFError, KeyboardInterrupt):
        if console:
            console.print("\n[yellow]Goodbye![/yellow]")
        else:
            print("\nGoodbye!")
        break
    
    if not user_input:
        continue
    
    if user_input.lower() in ["/exit", "/quit", "exit", "quit"]:
        if console:
            console.print("[yellow]Goodbye![/yellow]")
        else:
            print("Goodbye!")
        break
    
    if user_input.lower() == "/help":
        print_help()
        continue
    
    if user_input.lower() == "/history":
        print_history()
        continue
    
    if user_input.lower() == "/clear":
        conversation_history = []
        save_history([])
        if console:
            console.print("[green]✓[/green] Conversation history cleared.")
        else:
            print("Conversation history cleared.")
        continue
    
    if user_input.lower() == "/config":
        print_config(provider, model, api_key)
        continue
    
    if user_input.lower() == "/models":
        list_models(provider)
        continue
    
    if user_input.lower() == "/tools":
        list_tools()
        continue
    
    conversation_history.append({"role": "user", "content": user_input})
    
    try:
        if console:
            console.print(f"\n[dim]Thinking...[/dim]", end="\r")
        
        if console:
            console.print("[bold blue]AI[/bold blue] [dim]>>[/dim] ", end="")
        else:
            print("AI >> ", end="")
        
        if use_stream:
            response = asyncio.run(agent.run(user_input))
            if console:
                console.print()
        else:
            response = asyncio.run(agent.run(user_input))
            if console:
                console.print()
                from rich.panel import Panel
                from rich.box import ROUNDED
                panel = Panel(
                    response,
                    border_style="blue",
                    box=ROUNDED,
                    padding=(1, 2)
                )
                console.print(panel)
            else:
                print(response)
        
        conversation_history.append({"role": "assistant", "content": response if not use_stream else ""})
        save_history(conversation_history)
    except Exception as e:
        if console:
            console.print(f"\n[red]Error: {e}[/red]")
        else:
            print(f"Error: {e}")
            print(f"Error: {e}")
