"""
SEBESKY-GPT Chat Manager - Main Entry Point

This is the main application file that ties together all the modules.
The application flow:
1. Check for first-time setup.
2. Load persisted configuration and initialize managers in a background thread.
3. Simultaneously, display the banner and onboarding message on the main thread.
4. Wait for loading to complete, then enter the main input loop.
"""

import threading
import os
import datetime
from rich.console import Console
from rich.prompt import Prompt

# Initialize Rich console for output
console = Console()

def load_resources(results: dict):
    """
    Worker function to load configuration and initialize the conversation manager.
    This runs in a background thread to speed up startup.
    """
    try:
        from modules.config_persistence import load_config
        from modules.conversation_manager import ConversationManager
        
        load_config()
        manager = ConversationManager()
        results['manager'] = manager
        
    except Exception as e:
        console.print(f"[red]Error during background loading: {e}[/red]")
        results['manager'] = None

def main():
    """
    Main application entry point.
    """
    from modules.config_persistence import CONFIG_FILE, run_first_time_setup
    from modules.renderer import display_onboarding, render_status_bar, render_input_box
    from modules.commands import handle_command
    from modules.config import CLIENT_CONFIG

    # --- First-Time Setup Check ---
    if not CONFIG_FILE.exists():
        run_first_time_setup()

    # --- Parallel Loading ---
    loading_results = {}
    loading_thread = threading.Thread(target=load_resources, args=(loading_results,))
    
    loading_thread.start()
    display_onboarding()
    loading_thread.join()
    
    manager = loading_results.get('manager')
    if not manager:
        console.print("[bold red]Fatal Error: Application resources could not be loaded. Exiting.[/bold red]")
        return
    # --- End Parallel Loading ---

    current_conv_id = None
    
    # Main input loop
    while True:
        directory = os.getcwd()
        if current_conv_id:
            token_count = manager.get_current_token_count(current_conv_id)
            total_tokens = CLIENT_CONFIG['token_window_size']
            token_percentage = (token_count / total_tokens) * 100 if total_tokens > 0 else 0
            token_info = f"Tokens: {token_count}/{total_tokens} ({token_percentage:.1f}%)"
        else:
            token_info = "Tokens: N/A"
        date_time_info = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        render_status_bar(directory, token_info, date_time_info)
        render_input_box()
        user_input = Prompt.ask("[bold green]You[/bold green]")
        
        if not user_input.strip():
            console.print("\033[F\033[K\033[F\033[K", end="")
            continue
        
        if user_input.startswith("/"):
            should_exit, new_conv_id = handle_command(manager, user_input, current_conv_id)
            current_conv_id = new_conv_id
            if should_exit:
                break
            continue
        
        if current_conv_id is None:
            title = user_input[:50] + ("..." if len(user_input) > 50 else "")
            current_conv_id = manager.create_conversation(title)
            console.print(f"\n[dim]Created new conversation: '{title}'[/dim]\n")
        
        manager.stream_response(current_conv_id, user_input)

if __name__ == "__main__":
    main()