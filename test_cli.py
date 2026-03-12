import asyncio
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def main():
    console.print("[bold green]OpenToad[/bold green] - Self-Sustainable AI Assistant")
    console.print("Testing CLI functionality...")
    
    # 选择提供商
    console.print("\nAvailable providers:")
    providers = ["anthropic", "openai", "deepseek", "ollama"]
    for i, p in enumerate(providers, 1):
        console.print(f"{i}. {p}")
    choice = typer.prompt("Enter provider number", type=int, min=1, max=len(providers))
    provider = providers[choice - 1]
    
    # 选择模型
    models = {
        "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
        "openai": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        "deepseek": ["deepseek-chat", "deepseek-coder"],
        "ollama": ["llama2", "mistral", "gemma"]
    }
    
    console.print(f"\nAvailable models for {provider}:")
    model_list = models.get(provider, [])
    for i, m in enumerate(model_list, 1):
        console.print(f"{i}. {m}")
    choice = typer.prompt("Enter model number", type=int, min=1, max=len(model_list))
    model = model_list[choice - 1]
    
    # 获取 API key
    api_key = ""
    if provider != "ollama":
        api_key = typer.prompt("Enter API key")
    
    console.print(f"\nProvider: {provider}, Model: {model}")
    console.print("CLI test completed successfully!")

if __name__ == "__main__":
    app()
