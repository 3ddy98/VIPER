"""
Simulate the onboarding flow with .env import
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from modules.config_persistence import import_from_env
from rich.console import Console
from rich.panel import Panel

console = Console()

def simulate_onboarding():
    """Simulate what the onboarding will show based on .env import."""

    print("=" * 70)
    print("ONBOARDING SIMULATION")
    print("=" * 70)
    print("\nThis simulates what the user will see during first-time setup")
    print("when a .env file is present.\n")

    # Simulate .env import
    imported = import_from_env()
    keys_imported = any(imported.values())

    # Show what the user would see
    console.clear()

    if keys_imported:
        console.print(Panel(
            "[bold green]Found .env file![/bold green]\n\n" +
            "The following keys were imported:\n" +
            (f"  ✓ API Key\n" if imported['api_key'] else "") +
            (f"  ✓ Google API Key\n" if imported['google_api_key'] else "") +
            (f"  ✓ Google Search Engine ID\n" if imported['google_cx_id'] else "") +
            (f"  ✓ OpenRouter API Key\n" if imported['openrouter_api_key'] else "") +
            "\nYou'll only be asked for values that weren't found.",
            title="Environment Variables Detected",
            border_style="green",
            padding=(1, 2)
        ))
        console.print()

    console.print(Panel(
        "[bold yellow]Welcome to Viper! Let's get you set up.[/bold yellow]\n\nPlease provide the following configuration details.",
        title="Viper First-Time Setup",
        border_style="cyan",
        padding=(1, 2)
    ))

    # Show what would be asked
    console.print("\n[bold]1. AI Model Settings[/bold]")
    console.print("  [cyan]Enter the API Base URL[/cyan] → [dim]Will be asked[/dim]")
    console.print("  [cyan]Enter the Model Name[/cyan] → [dim]Will be asked[/dim]")

    if not imported['api_key']:
        console.print("  [cyan]Enter your API Key[/cyan] → [dim]Will be asked[/dim]")
    else:
        console.print("  [green]✓ API Key loaded from .env[/green] → [dim]SKIPPED[/dim]")

    console.print("\n[bold]2. Preferences[/bold]")
    console.print("  [cyan]Auto-execute non-destructive tools?[/cyan] → [dim]Will be asked[/dim]")
    console.print("  [cyan]Enable live streaming?[/cyan] → [dim]Will be asked[/dim]")

    console.print("\n[bold]3. Optional: Google Web Search[/bold]")
    google_keys_imported = imported['google_api_key'] and imported['google_cx_id']

    if google_keys_imported:
        console.print("  [green]✓ Google Search configured from .env[/green] → [dim]SKIPPED[/dim]")
    else:
        console.print("  [cyan]Do you want to set up Google Web Search?[/cyan] → [dim]Will be asked[/dim]")
        if not imported['google_api_key']:
            console.print("    [cyan]Enter your Google API Key[/cyan] → [dim]Will be asked if yes[/dim]")
        else:
            console.print("    [green]✓ Google API Key loaded from .env[/green] → [dim]SKIPPED[/dim]")

        if not imported['google_cx_id']:
            console.print("    [cyan]Enter your Google CX ID[/cyan] → [dim]Will be asked if yes[/dim]")
        else:
            console.print("    [green]✓ Google CX ID loaded from .env[/green] → [dim]SKIPPED[/dim]")

    console.print("\n[bold]4. Optional: OpenRouter[/bold]")
    if imported['openrouter_api_key']:
        console.print("  [green]✓ OpenRouter API Key loaded from .env[/green] → [dim]SKIPPED[/dim]")
    else:
        console.print("  [cyan]Do you want to set up OpenRouter?[/cyan] → [dim]Will be asked[/dim]")
        console.print("    [cyan]Enter your OpenRouter API Key[/cyan] → [dim]Will be asked if yes[/dim]")

    # Summary
    console.print("\n" + "=" * 70)
    console.print("SUMMARY")
    console.print("=" * 70)

    total_questions = 7  # Base URL, Model, Preferences x2, Google prompt, OpenRouter prompt
    skipped_questions = 0

    if imported['api_key']:
        skipped_questions += 1

    if google_keys_imported:
        skipped_questions += 1  # Skip the entire Google section
    elif imported['google_api_key']:
        skipped_questions += 0  # Still need to ask if they want Google
    elif imported['google_cx_id']:
        skipped_questions += 0

    if imported['openrouter_api_key']:
        skipped_questions += 1

    console.print(f"\n[bold]Questions in standard onboarding:[/bold] ~{total_questions}")
    console.print(f"[bold green]Questions skipped due to .env:[/bold green] {skipped_questions}")
    console.print(f"[bold yellow]Questions remaining:[/bold yellow] ~{total_questions - skipped_questions}")

    console.print("\n[bold cyan]Benefits of .env file:[/bold cyan]")
    console.print("  ✓ Faster onboarding experience")
    console.print("  ✓ No need to manually enter API keys")
    console.print("  ✓ Keys stay secure in .env (not committed to git)")
    console.print("  ✓ Easy to update keys without re-running setup")

if __name__ == "__main__":
    simulate_onboarding()
