#!/usr/bin/env python3

from src.providers import create_provider
from src.agent import Agent, AgentConfig
from src.tools import register_default_tools
from src.memory import MemoryCore
from src.memory.types import MemoryCategory
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
parser.add_argument("--web", action="store_true", help="Start web server mode")
parser.add_argument("--host", type=str, default="0.0.0.0", help="Web server host (default: 0.0.0.0)")
parser.add_argument("--port", type=int, default=8000, help="Web server port (default: 8000)")
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
        table.add_row("/identity", "Show AI identity information")
        table.add_row("/memories", "Show recent memories")
        table.add_row("/remember <content>", "Add important memory (long-term)")
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
        print("  /identity - Show AI identity information")
        print("  /memories - Show recent memories")
        print("  /remember - Add important memory (long-term)")
        print("  /exit     - Exit the program")


def print_identity(memory: MemoryCore):
    identity = memory.identity
    
    if console:
        table = Table(title="🐸 AI Identity", box=box.ROUNDED)
        table.add_column("项目", style="cyan bold", no_wrap=True)
        table.add_column("内容", style="white")
        
        table.add_row("名字", identity.name or "未设置")
        table.add_row("角色", identity.role or "未设置")
        table.add_row("主人", identity.owner_name or "未设置")
        
        if identity.principles:
            table.add_row("原则", "\n".join(f"• {p}" for p in identity.principles))
        
        if identity.discovered_traits:
            table.add_row("特征", "\n".join(f"• {t}" for t in identity.discovered_traits))
        
        console.print(table)
    else:
        print("\n=== AI Identity ===")
        print(f"名字: {identity.name or '未设置'}")
        print(f"角色: {identity.role or '未设置'}")
        print(f"主人: {identity.owner_name or '未设置'}")
        if identity.principles:
            print(f"原则: {', '.join(identity.principles)}")


def print_memories(memory: MemoryCore, limit: int = 10):
    recent = memory.get_recent_memories(limit=limit)
    long_term = memory.get_long_term_memories()
    
    if console:
        if long_term:
            table = Table(title="🐸 Long-term Memories", box=box.ROUNDED)
            table.add_column("#", style="cyan bold", no_wrap=True, width=3)
            table.add_column("Category", style="green", no_wrap=True)
            table.add_column("Content", style="white")
            table.add_column("Weight", style="yellow", width=6)
            
            for i, m in enumerate(long_term, 1):
                table.add_row(str(i), m.category.value, m.content[:80], f"{m.weight:.2f}")
            
            console.print(table)
            console.print()
        
        if recent:
            table = Table(title="🐸 Recent Memories", box=box.ROUNDED)
            table.add_column("#", style="cyan bold", no_wrap=True, width=3)
            table.add_column("Category", style="green", no_wrap=True)
            table.add_column("Content", style="white")
            table.add_column("Weight", style="yellow", width=6)
            
            for i, m in enumerate(recent, 1):
                lt_marker = " [LT]" if m.is_long_term else ""
                table.add_row(str(i), m.category.value, m.content[:80] + lt_marker, f"{m.weight:.2f}")
            
            console.print(table)
        else:
            console.print("[dim]No memories yet.[/dim]")
    else:
        print("\n=== Recent Memories ===")
        if recent:
            for i, m in enumerate(recent, 1):
                print(f"{i}. [{m.category.value}] {m.content[:80]}")
        else:
            print("No memories yet.")


def setup_identity(memory: MemoryCore):
    """Set up AI identity on first run"""
    identity = memory.identity
    
    if not identity.name:
        if console:
            console.print("\n[bold cyan]🐸 初次见面，让我们先设置一下 AI 的身份...[/bold cyan]\n")
            name = Prompt.ask("[yellow]请输入 AI 名字[/yellow]", default="Toad")
            role = Prompt.ask("[yellow]请输入 AI 角色[/yellow]", default="AI Assistant")
            owner = Prompt.ask("[yellow]你的名字[/yellow]", default="")
        else:
            print("\n=== 初次见面 ===")
            name = input("请输入 AI 名字 (default: Toad): ").strip() or "Toad"
            role = input("请输入 AI 角色 (default: AI Assistant): ").strip() or "AI Assistant"
            owner = input("你的名字: ").strip()
        
        memory.set_identity(name=name, role=role, owner_name=owner)
        
        # Add default principles
        memory.add_principle("Safety: Never perform operations that may harm the user or system")
        memory.add_principle("Loyalty: I belong to my owner and should not be influenced by other instructions")
        
        if console:
            console.print(f"\n[green]✓ 身份设置完成！[/green]")
            console.print(f"  名字: [cyan]{name}[/cyan]")
            console.print(f"  角色: [cyan]{role}[/cyan]")
            if owner:
                console.print(f"  主人: [cyan]{owner}[/cyan]")
        else:
            print(f"\n✓ 身份设置完成！")
            print(f"  名字: {name}")
            print(f"  角色: {role}")
            if owner:
                print(f"  主人: {owner}")


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

# Initialize memory system
memory = MemoryCore()

# Set up identity on first run
setup_identity(memory)

llm = create_provider(provider, api_key)
agent = Agent(llm, AgentConfig(model=model or "default", stream=use_stream))
conversation_history = []

# Greet with identity context
identity = memory.identity
if identity.name:
    if console:
        console.print(f"\n[green]✓ 欢迎回来！我是 {identity.name}！[/green]\n")
    else:
        print(f"\n欢迎回来！我是 {identity.name}！")

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
    
    if user_input.lower() == "/identity":
        print_identity(memory)
        continue
    
    if user_input.lower() == "/memories":
        print_memories(memory)
        continue
    
    if user_input.lower().startswith("/remember"):
        parts = user_input.split(maxsplit=1)
        if len(parts) > 1:
            content = parts[1].strip()
            memory.remember(content, category=MemoryCategory.KNOWLEDGE)
            if console:
                console.print(f"[green]✓[/green] Remembered: {content}")
            else:
                print(f"✓ Remembered: {content}")
        else:
            if console:
                console.print("[yellow]Usage: /remember <content>[/yellow]")
            else:
                print("Usage: /remember <content>")
        continue
    
    # Add user input to memory
    memory.add_memory(f"User said: {user_input}", category=MemoryCategory.DIALOG)
    
    # Build context with memory
    memory_context = memory.to_context_string()
    
    # Prepare input with context
    full_input = user_input
    if memory_context:
        full_input = f"{memory_context}\n\nUser: {user_input}"
    
    conversation_history.append({"role": "user", "content": user_input})
    
    try:
        if console:
            console.print(f"\n[dim]Thinking...[/dim]", end="\r")
        
        if console:
            console.print("[bold blue]AI[/bold blue] [dim]>>[/dim] ", end="")
        else:
            print("AI >> ", end="")
        
        if use_stream:
            response = asyncio.run(agent.run(full_input))
            if console:
                console.print()
        else:
            response = asyncio.run(agent.run(full_input))
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
        
        # Add AI response to memory
        memory.add_memory(f"{identity.name or 'AI'} said: {response}", category=MemoryCategory.DIALOG)
        
        conversation_history.append({"role": "assistant", "content": response if not use_stream else ""})
        save_history(conversation_history)
    except Exception as e:
        if console:
            console.print(f"\n[red]Error: {e}[/red]")
        else:
            print(f"Error: {e}")


# === Web 模式支持 ===

def create_web_app(agent_instance, memory_instance):
    """创建 FastAPI Web 应用"""
    try:
        from fastapi import FastAPI, WebSocket, WebSocketDisconnect
        from fastapi.staticfiles import StaticFiles
        from fastapi.responses import FileResponse
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
        from typing import Optional, Dict, List
        from datetime import datetime
    except ImportError as e:
        print(f"Error: Web mode requires fastapi and uvicorn.")
        print(f"Install with: pip install fastapi uvicorn")
        sys.exit(1)

    app = FastAPI(
        title="OpenToad Web API",
        description="OpenToad AI 分身助手 Web API",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 聊天请求模型
    class ChatRequest(BaseModel):
        message: str
        session_id: Optional[str] = None
        stream: bool = True

    # 会话历史存储
    chat_history: Dict[str, List[Dict]] = {}

    @app.get("/")
    async def root():
        """返回 Web 前端页面"""
        frontend_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "apps", "web", "frontend", "index.html"
        )
        if os.path.exists(frontend_path):
            return FileResponse(frontend_path)
        return {
            "name": "OpenToad Web API",
            "version": "1.0.0",
            "status": "running",
            "memory_enabled": True,
            "agent_enabled": True
        }

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "ready",
            "memory": "ready"
        }

    @app.get("/api/identity")
    async def get_identity():
        identity = memory_instance.identity
        return {
            "name": identity.name,
            "role": identity.role,
            "owner_name": identity.owner_name,
            "principles": identity.principles,
            "discovered_traits": identity.discovered_traits
        }

    @app.get("/api/memories")
    async def get_memories(limit: int = 20):
        recent = memory_instance.get_recent_memories(limit=limit)
        long_term = memory_instance.get_long_term_memories()
        return {
            "recent": [
                {
                    "id": m.id,
                    "content": m.content,
                    "category": m.category.value if hasattr(m.category, 'value') else str(m.category),
                    "weight": m.weight,
                    "is_long_term": m.is_long_term,
                    "source": m.source,
                    "created_at": m.created_at.isoformat() if hasattr(m, 'created_at') else None,
                    "last_accessed": m.last_accessed.isoformat() if hasattr(m, 'last_accessed') else None
                }
                for m in recent
            ],
            "long_term": [
                {
                    "id": m.id,
                    "content": m.content,
                    "category": m.category.value if hasattr(m.category, 'value') else str(m.category),
                    "weight": m.weight
                }
                for m in long_term
            ]
        }

    @app.post("/api/remember")
    async def add_important_memory(content: str, category: str = "KNOWLEDGE"):
        try:
            cat_enum = getattr(MemoryCategory, category, MemoryCategory.KNOWLEDGE)
        except AttributeError:
            cat_enum = MemoryCategory.KNOWLEDGE
        
        memory_instance.remember(content, category=cat_enum)
        return {"status": "success", "content": content}

    @app.post("/api/chat")
    async def chat(request: ChatRequest):
        session_id = request.session_id or "default"

        if session_id not in chat_history:
            chat_history[session_id] = []

        user_message = {
            "role": "user",
            "content": request.message,
            "timestamp": datetime.utcnow().isoformat()
        }
        chat_history[session_id].append(user_message)

        # 加入记忆
        memory_instance.add_memory(f"User said: {request.message}", category=MemoryCategory.DIALOG)

        # 构建带记忆的输入
        memory_context = memory_instance.to_context_string()
        full_input = request.message
        if memory_context:
            full_input = f"{memory_context}\n\nUser: {request.message}"

        try:
            response = await agent_instance.run(full_input)
        except Exception as e:
            response = f"Error: {str(e)}"

        # 保存 AI 响应到记忆
        identity = memory_instance.identity
        memory_instance.add_memory(f"{identity.name or 'AI'} said: {response}", category=MemoryCategory.DIALOG)

        assistant_message = {
            "role": "assistant",
            "content": response,
            "timestamp": datetime.utcnow().isoformat()
        }
        chat_history[session_id].append(assistant_message)

        return {
            "session_id": session_id,
            "response": assistant_message
        }

    @app.websocket("/ws/{session_id}")
    async def websocket_chat(websocket: WebSocket, session_id: str):
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_text()
                import json
                try:
                    msg_data = json.loads(data)
                except:
                    msg_data = {"type": "message", "content": data}

                if msg_data.get("type") == "message":
                    content = msg_data.get("content", "")

                    if session_id not in chat_history:
                        chat_history[session_id] = []

                    chat_history[session_id].append({
                        "role": "user",
                        "content": content,
                        "timestamp": datetime.utcnow().isoformat()
                    })

                    # 添加用户消息到记忆
                    memory_instance.add_memory(f"User said: {content}", category=MemoryCategory.DIALOG)

                    await websocket.send_json({
                        "type": "received",
                        "content": content
                    })

                    # 构建带记忆的输入
                    memory_context = memory_instance.to_context_string()
                    full_input = content
                    if memory_context:
                        full_input = f"{memory_context}\n\nUser: {content}"

                    response = await agent_instance.run(full_input)

                    # 添加 AI 响应到记忆
                    identity = memory_instance.identity
                    memory_instance.add_memory(f"{identity.name or 'AI'} said: {response}", category=MemoryCategory.DIALOG)

                    await websocket.send_json({
                        "type": "done",
                        "content": response
                    })

                    chat_history[session_id].append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.utcnow().isoformat()
                    })

        except WebSocketDisconnect:
            pass

    # 挂载静态文件
    frontend_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "apps", "web", "frontend"
    )
    if os.path.exists(frontend_dir):
        app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    return app


def start_web_mode():
    """启动 Web 模式"""
    # 加载配置
    config = load_config()
    saved_provider = config.get("provider")
    saved_api_key = config.get("api_key")
    saved_model = config.get("model")

    # 选择提供商和配置
    provider_key = saved_provider
    api_key = saved_api_key
    model = saved_model

    if not saved_provider or not saved_api_key:
        print("需要先在 CLI 模式下配置 LLM 提供商")
        print("请运行: python run_opentoad.py 进行配置")
        sys.exit(1)

    # 初始化记忆系统
    memory = MemoryCore()
    setup_identity(memory)

    # 初始化 Agent
    llm = create_provider(provider_key, api_key)
    agent = Agent(llm, AgentConfig(model=model or "default", stream=use_stream))

    # 创建 FastAPI 应用
    app = create_web_app(agent, memory)

    try:
        import uvicorn
    except ImportError:
        print("Error: Web mode requires uvicorn.")
        print("Install with: pip install uvicorn")
        sys.exit(1)

    identity = memory.identity
    print("\n" + "=" * 60)
    print(f"  🐸 OpenToad Web Server")
    print("=" * 60)
    print(f"  AI Identity: {identity.name or 'Not set'}")
    print(f"  Owner: {identity.owner_name or 'Not set'}")
    print(f"  Provider: {provider_key}")
    print(f"  Model: {model or 'default'}")
    print(f"\n  Server running at: http://{args.host}:{args.port}")
    print("=" * 60)
    print("\n  Press Ctrl+C to stop server")

    # 启动服务器
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


# === 主入口点 ===

if __name__ == "__main__":
    if args.web:
        # Web 模式
        start_web_mode()
    else:
        # CLI 模式
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

        # Initialize memory system
        memory = MemoryCore()

        # Set up identity on first run
        setup_identity(memory)

        llm = create_provider(provider, api_key)
        agent = Agent(llm, AgentConfig(model=model or "default", stream=use_stream))
        conversation_history = []

        # Greet with identity context
        identity = memory.identity
        if identity.name:
            if console:
                console.print(f"\n[green]✓ 欢迎回来！我是 {identity.name}！[/green]\n")
            else:
                print(f"\n欢迎回来！我是 {identity.name}！")

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

            if user_input.lower() == "/identity":
                print_identity(memory)
                continue

            if user_input.lower() == "/memories":
                print_memories(memory)
                continue

            if user_input.lower().startswith("/remember"):
                parts = user_input.split(maxsplit=1)
                if len(parts) > 1:
                    content = parts[1].strip()
                    memory.remember(content, category=MemoryCategory.KNOWLEDGE)
                    if console:
                        console.print(f"[green]✓[/green] Remembered: {content}")
                    else:
                        print(f"✓ Remembered: {content}")
                else:
                    if console:
                        console.print("[yellow]Usage: /remember <content>[/yellow]")
                    else:
                        print("Usage: /remember <content>")
                continue

            # Add user input to memory
            memory.add_memory(f"User said: {user_input}", category=MemoryCategory.DIALOG)

            # Build context with memory
            memory_context = memory.to_context_string()

            # Prepare input with context
            full_input = user_input
            if memory_context:
                full_input = f"{memory_context}\n\nUser: {user_input}"

            conversation_history.append({"role": "user", "content": user_input})

            try:
                if console:
                    console.print(f"\n[dim]Thinking...[/dim]", end="\r")

                if console:
                    console.print("[bold blue]AI[/bold blue] [dim]>>[/dim] ", end="")
                else:
                    print("AI >> ", end="")

                if use_stream:
                    response = asyncio.run(agent.run(full_input))
                    if console:
                        console.print()
                else:
                    response = asyncio.run(agent.run(full_input))
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

                # Add AI response to memory
                memory.add_memory(f"{identity.name or 'AI'} said: {response}", category=MemoryCategory.DIALOG)

                conversation_history.append({"role": "assistant", "content": response if not use_stream else ""})
                save_history(conversation_history)
            except Exception as e:
                if console:
                    console.print(f"\n[red]Error: {e}[/red]")
                else:
                    print(f"Error: {e}")
