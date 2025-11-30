import os
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

# Import the configuration dictionaries from the existing config module
from modules.config import CLIENT_CONFIG, TOOL_CONFIG, UI_CONFIG, CONTEXT_CONFIG, GOOGLE_SEARCH_CONFIG

# Path to the directory that will hold the persisted configuration
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
# Path to the JSON file that stores the configuration
CONFIG_FILE = DATA_DIR / "config.json"

# Initialize console for printing messages
console = Console()


def run_first_time_setup():
    """
    Guides the user through setting up API keys and core preferences.
    This is triggered when no 'config.json' is found.
    """
    console.clear()
    console.print(Panel(
        "[bold yellow]Welcome to Viper! Let's get you set up.[/bold yellow]\n\nPlease provide the following configuration details.",
        title="Viper First-Time Setup",
        border_style="cyan",
        padding=(1, 2)
    ))

    # --- Core AI Configuration ---
    console.print("\n[bold]1. AI Model Settings[/bold]")
    CLIENT_CONFIG['base_url'] = Prompt.ask(
        "  [cyan]Enter the API Base URL[/cyan] (e.g., http://localhost:1234/v1)",
        default=CLIENT_CONFIG.get("base_url") or "http://localhost:8000/v1"
    )
    CLIENT_CONFIG['model'] = Prompt.ask(
        "  [cyan]Enter the Model Name[/cyan]",
        default=CLIENT_CONFIG.get("model") or "gpt-oss-120B"
    )
    CLIENT_CONFIG['api_key'] = Prompt.ask(
        "  [cyan]Enter your API Key[/cyan] (if required by your model endpoint)",
        default=CLIENT_CONFIG.get("api_key") or "123456"
    )

    # --- Tool & UI Preferences ---
    console.print("\n[bold]2. Preferences[/bold]")
    TOOL_CONFIG['auto_execute_non_destructive'] = Confirm.ask(
        "  [cyan]Automatically run non-destructive tools (e.g., read files, list directories) without asking?[/cyan]",
        default=True
    )
    UI_CONFIG['show_streaming'] = Confirm.ask(
        "  [cyan]Enable live streaming for AI responses?[/cyan]",
        default=True
    )

    # --- Optional: Google Search ---
    console.print("\n[bold]3. Optional: Google Web Search[/bold]")
    console.print("[dim]  These keys are only required for the 'web_search' tool.[/dim]")
    if Confirm.ask("  [cyan]Do you want to set up Google Web Search?[/cyan]", default=False):
        GOOGLE_SEARCH_CONFIG['api_key'] = Prompt.ask(
            "    [cyan]Enter your Google API Key[/cyan]"
        )
        GOOGLE_SEARCH_CONFIG['search_engine_id'] = Prompt.ask(
            "    [cyan]Enter your Google Programmable Search Engine ID (CX ID)[/cyan]"
        )

    # --- Save Configuration ---
    save_config()
    console.print("\n[green]✓ Configuration saved successfully![/green]")
    console.print("[dim]You can change these values anytime via the `/config` command or by editing the `data/config.json` file.[/dim]\n")
    Prompt.ask("[bold]Press Enter to start Viper...[/bold]")


def load_config() -> None:
    """Load configuration from ``data/config.json`` if it exists."""
    if not CONFIG_FILE.exists():
        return

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            loaded_config = json.load(f)
        
        # Update each configuration dictionary with the loaded values
        if "client" in loaded_config:
            CLIENT_CONFIG.update(loaded_config["client"])
        if "tool" in loaded_config:
            TOOL_CONFIG.update(loaded_config["tool"])
        if "ui" in loaded_config:
            UI_CONFIG.update(loaded_config["ui"])
        if "context" in loaded_config:
            CONTEXT_CONFIG.update(loaded_config["context"])
        if "google_search" in loaded_config:
            GOOGLE_SEARCH_CONFIG.update(loaded_config["google_search"])

    except (json.JSONDecodeError, IOError) as e:
        console.print(f"[red]✗ Error loading configuration from {CONFIG_FILE}: {e}[/red]")


def _ensure_data_dir() -> None:
    """Create the ``data`` directory if it does not already exist."""
    os.makedirs(DATA_DIR, exist_ok=True)


def save_config() -> None:
    """Persist the current configuration dictionaries to ``data/config.json``."""
    _ensure_data_dir()
    
    config_to_save = {
        "client": CLIENT_CONFIG,
        "tool": TOOL_CONFIG,
        "ui": UI_CONFIG,
        "context": CONTEXT_CONFIG,
        "google_search": GOOGLE_SEARCH_CONFIG
    }
    
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_to_save, f, indent=2, ensure_ascii=False)
