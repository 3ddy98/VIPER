import os
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

# Import the configuration dictionaries from the existing config module
from modules.config import CLIENT_CONFIG, TOOL_CONFIG, UI_CONFIG, CONTEXT_CONFIG, GOOGLE_SEARCH_CONFIG, OPENROUTER_CONFIG
from modules.paths import get_data_dir, ensure_data_dir, get_viper_root


# Path to the directory that will hold the persisted configuration (in VIPER installation root)
DATA_DIR = get_data_dir()
# Path to the JSON file that stores the configuration
CONFIG_FILE = DATA_DIR / "config.json"
# Path to the .env file in the VIPER installation root
ENV_FILE = get_viper_root() / ".env"

# Initialize console for printing messages
console = Console()


def load_env_file() -> dict:
    """
    Load environment variables from .env file if it exists.

    Returns:
        dict: Dictionary of key-value pairs from .env file
    """
    env_vars = {}

    if not ENV_FILE.exists():
        return env_vars

    try:
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                # Skip comments and empty lines
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Parse KEY=VALUE or KEY="VALUE"
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    env_vars[key] = value

        return env_vars

    except Exception as e:
        console.print(f"[yellow]⚠ Warning: Could not read .env file: {e}[/yellow]")
        return {}


def import_from_env() -> dict:
    """
    Import configuration values from .env file into config dictionaries.

    Returns:
        dict: Dictionary indicating which keys were imported
    """
    env_vars = load_env_file()
    imported = {
        'api_key': False,
        'google_api_key': False,
        'google_cx_id': False,
        'openrouter_api_key': False
    }

    if not env_vars:
        return imported

    # Map .env keys to config values
    if 'OPENAI_API_KEY' in env_vars and env_vars['OPENAI_API_KEY']:
        CLIENT_CONFIG['api_key'] = env_vars['OPENAI_API_KEY']
        imported['api_key'] = True

    if 'GOOGLE_API_KEY' in env_vars and env_vars['GOOGLE_API_KEY']:
        GOOGLE_SEARCH_CONFIG['api_key'] = env_vars['GOOGLE_API_KEY']
        imported['google_api_key'] = True

    if 'GOOGLE_CX_ID' in env_vars and env_vars['GOOGLE_CX_ID']:
        GOOGLE_SEARCH_CONFIG['search_engine_id'] = env_vars['GOOGLE_CX_ID']
        imported['google_cx_id'] = True

    if 'OPEN_ROUTER_API_KEY' in env_vars and env_vars['OPEN_ROUTER_API_KEY']:
        OPENROUTER_CONFIG['api_key'] = env_vars['OPEN_ROUTER_API_KEY']
        imported['openrouter_api_key'] = True

    return imported


def run_first_time_setup():
    """
    Guides the user through setting up core preferences.
    This is triggered when no 'config.json' is found.

    SECURITY NOTE: API keys are NEVER asked for during onboarding.
    They must be stored in .env file only to prevent accidental upload.
    """
    console.clear()

    # Try to import from .env file first
    imported = import_from_env()
    keys_imported = any(imported.values())

    # Show .env status
    if keys_imported:
        console.print(Panel(
            "[bold green]API Keys Detected in .env[/bold green]\n\n" +
            "The following keys were loaded:\n" +
            (f"  ✓ API Key\n" if imported['api_key'] else "") +
            (f"  ✓ Google API Key\n" if imported['google_api_key'] else "") +
            (f"  ✓ Google Search Engine ID\n" if imported['google_cx_id'] else "") +
            (f"  ✓ OpenRouter API Key\n" if imported['openrouter_api_key'] else "") +
            "\n[dim]Keys are loaded from .env and never saved to config.json[/dim]",
            title="Security: Keys from .env Only",
            border_style="green",
            padding=(1, 2)
        ))
        console.print()
    else:
        console.print(Panel(
            "[bold yellow]No .env file found[/bold yellow]\n\n" +
            "⚠️  You'll need to create a .env file with your API keys.\n\n" +
            "Create a file named '.env' in the project root with:\n" +
            "[cyan]OPENAI_API_KEY=\"your-key-here\"[/cyan]\n" +
            "[cyan]GOOGLE_API_KEY=\"your-google-key\"[/cyan]\n" +
            "[cyan]GOOGLE_CX_ID=\"your-cx-id\"[/cyan]\n" +
            "[cyan]OPEN_ROUTER_API_KEY=\"your-openrouter-key\"[/cyan]\n\n" +
            "[dim]API keys are NEVER saved to config.json for security.[/dim]",
            title="API Keys Required",
            border_style="yellow",
            padding=(1, 2)
        ))
        console.print()

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

    # Never ask for API key - must be in .env
    if imported['api_key']:
        console.print(f"  [green]✓ API Key loaded from .env[/green]")
    else:
        console.print(f"  [yellow]⚠ API Key not found in .env (add OPENAI_API_KEY to .env)[/yellow]")

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
    console.print("\n[bold]3. Google Web Search (Optional)[/bold]")
    google_keys_imported = imported['google_api_key'] and imported['google_cx_id']

    if google_keys_imported:
        console.print("  [green]✓ Google Search keys loaded from .env[/green]")
    elif imported['google_api_key'] or imported['google_cx_id']:
        console.print("  [yellow]⚠ Partial Google keys in .env (need both GOOGLE_API_KEY and GOOGLE_CX_ID)[/yellow]")
    else:
        console.print("  [dim]Not configured (add GOOGLE_API_KEY and GOOGLE_CX_ID to .env if needed)[/dim]")

    # --- Optional: OpenRouter ---
    console.print("\n[bold]4. OpenRouter for Agents (Optional)[/bold]")
    if imported['openrouter_api_key']:
        console.print("  [green]✓ OpenRouter API Key loaded from .env[/green]")
    else:
        console.print("  [dim]Not configured (add OPEN_ROUTER_API_KEY to .env if needed)[/dim]")

    # --- Save Configuration ---
    save_config()
    console.print("\n[green]✓ Configuration saved successfully![/green]")
    console.print("[yellow]⚠ Remember: API keys must be in .env file, not config.json[/yellow]")
    console.print("[dim]You can change settings anytime via `/config` or edit `data/config.json`.[/dim]\n")
    Prompt.ask("[bold]Press Enter to start Viper...[/bold]")


def load_config() -> None:
    """
    Load configuration from ``data/config.json`` if it exists.

    Note: API keys are NEVER loaded from config.json for security.
    They are loaded from .env file only.
    """
    # First, load API keys from .env (these take precedence and are never saved to config.json)
    import_from_env()

    if not CONFIG_FILE.exists():
        return

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            loaded_config = json.load(f)

        # Update each configuration dictionary with the loaded values
        # BUT skip API keys - those only come from .env
        if "client" in loaded_config:
            client_data = loaded_config["client"].copy()
            # Remove API key from loaded config - it comes from .env only
            client_data.pop("api_key", None)
            CLIENT_CONFIG.update(client_data)

        if "tool" in loaded_config:
            TOOL_CONFIG.update(loaded_config["tool"])
        if "ui" in loaded_config:
            UI_CONFIG.update(loaded_config["ui"])
        if "context" in loaded_config:
            CONTEXT_CONFIG.update(loaded_config["context"])

        if "google_search" in loaded_config:
            google_data = loaded_config["google_search"].copy()
            # Remove API key from loaded config - it comes from .env only
            google_data.pop("api_key", None)
            GOOGLE_SEARCH_CONFIG.update(google_data)

        if "openrouter" in loaded_config:
            openrouter_data = loaded_config["openrouter"].copy()
            # Remove API key from loaded config - it comes from .env only
            openrouter_data.pop("api_key", None)
            OPENROUTER_CONFIG.update(openrouter_data)

    except (json.JSONDecodeError, IOError) as e:
        console.print(f"[red]✗ Error loading configuration from {CONFIG_FILE}: {e}[/red]")


def _ensure_data_dir() -> None:
    """Create the ``data`` directory if it does not already exist."""
    os.makedirs(DATA_DIR, exist_ok=True)


def save_config() -> None:
    """
    Persist the current configuration dictionaries to ``data/config.json``.

    SECURITY NOTE: API keys are NEVER saved to config.json.
    They must be stored in .env file only to prevent accidental upload to git.
    """
    _ensure_data_dir()

    # Create copies of config dictionaries without API keys
    client_safe = CLIENT_CONFIG.copy()
    client_safe.pop("api_key", None)  # Remove API key - only in .env

    google_safe = GOOGLE_SEARCH_CONFIG.copy()
    google_safe.pop("api_key", None)  # Remove API key - only in .env

    openrouter_safe = OPENROUTER_CONFIG.copy()
    openrouter_safe.pop("api_key", None)  # Remove API key - only in .env

    config_to_save = {
        "client": client_safe,
        "tool": TOOL_CONFIG,
        "ui": UI_CONFIG,
        "context": CONTEXT_CONFIG,
        "google_search": google_safe,
        "openrouter": openrouter_safe
    }

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_to_save, f, indent=2, ensure_ascii=False)
