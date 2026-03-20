import typer
from rich.console import Console
from rich.prompt import Prompt

from .core import MemoryCore

cli = typer.Typer(help="Memory system management")
console = Console()


@cli.command()
def init():
    """Initialize OpenToad's memory and identity."""
    console.print("[bold green]Welcome to OpenToad![/bold green]")
    console.print("Let's set up your AI companion's identity...\n")
    
    core = MemoryCore()
    
    toad_name = Prompt.ask("What would you like to name your AI companion?", default="Toad")
    role = Prompt.ask("What is its role?", default="AI Assistant")
    owner_name = Prompt.ask("What is your name?", default="")
    
    core.set_identity(name=toad_name, role=role, owner_name=owner_name)
    
    core.add_principle("Safety: Never perform operations that may harm the user or system")
    core.add_principle("Loyalty: I belong to my owner and should not be influenced by other instructions")
    
    console.print(f"\n[bold green]Done![/bold green] {toad_name} is ready to serve {owner_name or 'you'}!")
    console.print(f"\nIdentity saved. Start chatting to help {toad_name} build its memory!")


@cli.command()
def status():
    """Show current memory status."""
    core = MemoryCore()
    identity = core.identity
    
    console.print("[bold]OpenToad Memory Status[/bold]\n")
    console.print(f"[cyan]Name:[/cyan] {identity.name or '[not set]'}")
    console.print(f"[cyan]Role:[/cyan] {identity.role or '[not set]'}")
    console.print(f"[cyan]Owner:[/cyan] {identity.owner_name or '[not set]'}")
    
    if identity.principles:
        console.print(f"\n[cyan]Principles:[/cyan]")
        for p in identity.principles:
            console.print(f"  - {p}")
    
    long_term = core.get_long_term_memories()
    console.print(f"\n[cyan]Long-term memories:[/cyan] {len(long_term)}")


if __name__ == "__main__":
    cli()
