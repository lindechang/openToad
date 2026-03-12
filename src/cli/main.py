import asyncio
import os
import typer
from rich.console import Console
from src.providers import create_provider
from src.agent import Agent, AgentConfig
from src.tools import register_default_tools

app = typer.Typer()
console = Console()


@app.command()
def main(
    provider: str = typer.Option("anthropic", help="LLM provider (anthropic, openai)"),
    model: str = typer.Option("claude-3-5-sonnet-20241022", help="Model name"),
    api_key: str = typer.Option("", help="API key (or set ANTHROPIC_API_KEY / OPENAI_API_KEY env var)"),
):
    register_default_tools()
    
    if not api_key:
        if provider == "anthropic":
            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        else:
            api_key = os.environ.get("OPENAI_API_KEY", "")
    
    if not api_key:
        api_key = typer.prompt("Enter API key")
    
    console.print("[bold green]OpenToad[/bold green] - Self-Sustainable AI Assistant")
    console.print(f"Provider: {provider}, Model: {model}")
    console.print("Type 'exit' or 'quit' to stop.\n")
    
    llm = create_provider(provider, api_key)
    agent = Agent(llm, AgentConfig(model=model))
    
    while True:
        user_input = typer.prompt("\n> ")
        if user_input in ("exit", "quit"):
            break
        
        response = asyncio.run(agent.run(user_input))
        console.print(response)


if __name__ == "__main__":
    app()
