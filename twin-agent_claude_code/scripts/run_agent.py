"""
scripts/run_agent.py

CLI entrypoint — run the agent from your terminal without the API.
This is the fastest way to test during development.

Usage:
    python scripts/run_agent.py "Read my last 3 emails"
    python scripts/run_agent.py "Post a tweet about AI agents"
    python scripts/run_agent.py --session abc123 "Follow up on that"
    python scripts/run_agent.py --interactive   # REPL mode
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import os

# Make sure we can import from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich import print as rprint

console = Console()


def print_result(result) -> None:
    """Pretty-print an AgentResult using rich."""
    status_color = "green" if result.success else "red"
    status_icon = "✓" if result.success else "✗"

    # Summary panel
    console.print(Panel(
        Markdown(result.answer),
        title=f"[{status_color}]{status_icon} Final Answer[/{status_color}]",
        border_style=status_color,
    ))

    # Stats
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("key", style="dim")
    table.add_column("value")
    table.add_row("Session", result.session_id)
    table.add_row("Iterations", str(result.iterations))
    table.add_row("Duration", f"{result.duration_seconds:.1f}s")
    if result.error:
        table.add_row("Error", f"[red]{result.error}[/red]")
    console.print(table)

    # Event log (collapsed)
    if "--verbose" in sys.argv or "-v" in sys.argv:
        console.print("\n[dim]── Event log ──[/dim]")
        for event in result.events:
            event_type = event.get("type", "?")
            if event_type == "thought":
                console.print(f"[blue]Thought:[/blue] {event['content'][:200]}")
            elif event_type == "action":
                console.print(f"[yellow]Action:[/yellow] {event['tool']}({event.get('input', {})})")
            elif event_type == "observation":
                console.print(f"[green]Observation:[/green] {event['content'][:200]}")


async def run_once(task: str, session_id: str | None = None) -> None:
    from agent.executor import build_agent
    from config.logging import setup_logging

    setup_logging()

    console.print(f"\n[dim]Task:[/dim] {task}")
    console.print("[dim]Starting agent...[/dim]\n")

    agent = build_agent()

    with console.status("[bold blue]Agent running...[/bold blue]", spinner="dots"):
        result = await agent.run(task=task, session_id=session_id)

    print_result(result)


async def run_interactive() -> None:
    from agent.executor import build_agent
    from config.logging import setup_logging

    setup_logging()

    console.print(Panel(
        "[bold]Twin Agent[/bold] — Interactive mode\n"
        "Type your task and press Enter. Type [red]exit[/red] to quit.\n"
        "Use [dim]--verbose[/dim] flag to see full event log.",
        title="Twin Agent REPL",
        border_style="blue",
    ))

    agent = build_agent()
    session_id = None  # Carry session across turns

    while True:
        try:
            task = console.input("\n[bold blue]>[/bold blue] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Bye.[/dim]")
            break

        if not task:
            continue
        if task.lower() in ("exit", "quit", "q"):
            console.print("[dim]Bye.[/dim]")
            break

        with console.status("[bold blue]Thinking...[/bold blue]", spinner="dots"):
            result = await agent.run(task=task, session_id=session_id)

        session_id = result.session_id  # Continue same session
        print_result(result)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Twin Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("task", nargs="?", help="Task to run")
    parser.add_argument("--session", "-s", help="Session ID to continue", default=None)
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive REPL")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show full event log")

    args = parser.parse_args()

    if args.interactive:
        asyncio.run(run_interactive())
    elif args.task:
        asyncio.run(run_once(args.task, session_id=args.session))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
