"""
scripts/seed_memory.py

Seeds the agent's semantic memory with persona context, preferences,
and any background knowledge you want the agent to always have access to.

Run this once after setting up, then re-run whenever you update the persona.

Usage:
    python scripts/seed_memory.py
    python scripts/seed_memory.py --clear   # wipe and re-seed
"""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.progress import track

console = Console()


SEED_MEMORIES = [
    # ── Communication preferences ─────────────────────────────────────────────
    {
        "text": "Always write emails in a direct, concise style. No filler phrases. Keep under 150 words unless the topic requires more.",
        "metadata": {"type": "preference", "domain": "email"},
    },
    {
        "text": "When writing Slack messages, lead with the ask. No 'Hey!' or 'Hope you're doing well' openers.",
        "metadata": {"type": "preference", "domain": "slack"},
    },
    {
        "text": "Twitter/X posts should be thoughtful and specific. Avoid generic takes. Focus on AI, startups, and engineering topics.",
        "metadata": {"type": "preference", "domain": "twitter"},
    },

    # ── Scheduling preferences ────────────────────────────────────────────────
    {
        "text": "Prefer morning meetings (9am–12pm). Avoid scheduling anything on Friday afternoons. Leave buffer time between back-to-back calls.",
        "metadata": {"type": "preference", "domain": "calendar"},
    },

    # ── Work context ──────────────────────────────────────────────────────────
    {
        "text": "Currently building a digital twin AI startup. The core product is an autonomous agent that represents users across digital platforms.",
        "metadata": {"type": "context", "domain": "work"},
    },
    {
        "text": "Technical background in machine learning and software engineering. Can go deep on implementation details when needed.",
        "metadata": {"type": "context", "domain": "background"},
    },

    # ── Decision-making principles ────────────────────────────────────────────
    {
        "text": "When in doubt, do less and confirm. Don't send emails or post publicly without being confident it reflects the owner's intent.",
        "metadata": {"type": "principle", "domain": "safety"},
    },
    {
        "text": "Prioritize tasks by impact and urgency. Respond to emails from investors, co-founders, and key users first.",
        "metadata": {"type": "principle", "domain": "prioritization"},
    },

    # ── People ────────────────────────────────────────────────────────────────
    # Add entries like this for important contacts:
    # {
    #     "text": "John Smith (john@example.com) is the co-founder handling frontend. Ping on Slack for quick things, email for formal updates.",
    #     "metadata": {"type": "contact", "name": "John Smith"},
    # },
]


def seed(clear: bool = False) -> None:
    from memory.semantic import SemanticMemory
    from config.logging import setup_logging
    from agent.persona import create_default_persona_file, load_persona

    setup_logging()

    semantic = SemanticMemory()

    if clear:
        console.print("[yellow]Clearing all semantic memory...[/yellow]")
        # ChromaDB doesn't have a bulk delete — recreate the client
        import shutil
        from config.settings import settings
        shutil.rmtree(settings.chroma_persist_path, ignore_errors=True)
        semantic = SemanticMemory()
        console.print("[green]Cleared.[/green]")

    # Create persona file if it doesn't exist
    persona_path = "./data/persona.json"
    if not os.path.exists(persona_path):
        create_default_persona_file()

    # Load persona and add it as a memory entry
    persona = load_persona()
    persona_memory = {
        "text": f"Persona: {persona.name}. {persona.description} Communication style: {persona.communication_style}",
        "metadata": {"type": "persona", "name": persona.name},
    }

    all_memories = [persona_memory] + SEED_MEMORIES

    console.print(f"\nSeeding [bold]{len(all_memories)}[/bold] memories into semantic store...\n")

    stored = 0
    for entry in track(all_memories, description="Storing..."):
        try:
            semantic.store(
                text=entry["text"],
                metadata=entry.get("metadata", {}),
            )
            stored += 1
        except Exception as e:
            console.print(f"[red]Failed to store: {entry['text'][:50]}... — {e}[/red]")

    console.print(f"\n[green]Done.[/green] Stored {stored}/{len(all_memories)} memories.")
    console.print(f"Total entries in memory: [bold]{semantic.count()}[/bold]")
    console.print("\nEdit [cyan]data/persona.json[/cyan] to customize the agent's identity.")
    console.print("Re-run this script with [cyan]--clear[/cyan] to reset and re-seed.\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed agent semantic memory")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all existing memories before seeding",
    )
    args = parser.parse_args()
    seed(clear=args.clear)


if __name__ == "__main__":
    main()
