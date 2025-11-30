"""
Commands Module

This module handles all slash command processing including:
- Command parsing and validation
- Command execution
- Help text display
- Conversation switching and management
"""

from typing import Optional, Tuple
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich import box

from modules.conversation_manager import ConversationManager
from modules.agent_manager import AgentManager
from modules.renderer import show_conversations_table, display_conversation_history, display_start_of_conversation, render_agent_list
from modules.config_persistence import save_config
from modules.config import TOOL_CONFIG, UI_CONFIG, CLIENT_CONFIG

# Initialize Rich console for output
console = Console()
agent_manager = AgentManager()


def show_config_menu():
    """
    Display and handle the configuration menu.
    
    Allows users to toggle tool execution settings interactively.
    """
    while True:
        # Clear and display config menu
        console.print("\n" + "=" * 60)
        console.print("[bold cyan]⚙️  Configuration Menu[/bold cyan]")
        console.print("=" * 60 + "\n")
        
        # Create configuration table
        table = Table(box=box.ROUNDED, border_style="cyan")
        table.add_column("Option", style="cyan", width=4)
        table.add_column("Setting", style="white")
        table.add_column("Value", style="green", justify="center")
        
        # Add configuration options
        table.add_row(
            "1", 
            "Tools Enabled", 
            f"[{'green' if TOOL_CONFIG['tools_enabled'] else 'red'}]{TOOL_CONFIG['tools_enabled']}[/]"
        )
        table.add_row(
            "2", 
            "Auto-Execute Non-Destructive Actions", 
            f"[{'green' if TOOL_CONFIG['auto_execute_non_destructive'] else 'red'}]{TOOL_CONFIG['auto_execute_non_destructive']}[/]"
        )
        table.add_row(
            "3", 
            "Auto-Execute Destructive Actions", 
            f"[{'green' if TOOL_CONFIG['auto_execute_destructive'] else 'red'}]{TOOL_CONFIG['auto_execute_destructive']}[/]"
        )
        table.add_row(
            "4",
            "Show AI Response Streaming",
            f"[{'green' if UI_CONFIG['show_streaming'] else 'red'}]{UI_CONFIG['show_streaming']}[/]"
        )
        table.add_row(
            "5",
            "AI Token Window Size",
            f"[cyan]{CLIENT_CONFIG['token_window_size']}[/]"
        )
        table.add_row("9", "Exit Configuration Menu", "[dim]Return to chat[/dim]")
        
        console.print(table)
        console.print()
        
        # Get user choice
        choice = Prompt.ask(
            "[bold cyan]Select option to toggle (1-5) or 9 to exit[/bold cyan]",
            choices=["1", "2", "3", "4", "5", "9"]
        )
        
        # Handle choice
        if choice == "1":
            TOOL_CONFIG["tools_enabled"] = not TOOL_CONFIG["tools_enabled"]
            status = "enabled" if TOOL_CONFIG["tools_enabled"] else "disabled"
            console.print(f"\n[green]✓ Tools {status}[/green]")
            
        elif choice == "2":
            TOOL_CONFIG["auto_execute_non_destructive"] = not TOOL_CONFIG["auto_execute_non_destructive"]
            status = "enabled" if TOOL_CONFIG["auto_execute_non_destructive"] else "disabled"
            console.print(f"\n[green]✓ Auto-execute non-destructive actions {status}[/green]")
            
        elif choice == "3":
            TOOL_CONFIG["auto_execute_destructive"] = not TOOL_CONFIG["auto_execute_destructive"]
            status = "enabled" if TOOL_CONFIG["auto_execute_destructive"] else "disabled"
            console.print(f"\n[green]✓ Auto-execute destructive actions {status}[/green]")
            if TOOL_CONFIG["auto_execute_destructive"]:
                console.print("[yellow]⚠️  Warning: Destructive actions will execute without confirmation![/yellow]")

        elif choice == "4":
            UI_CONFIG["show_streaming"] = not UI_CONFIG["show_streaming"]
            status = "enabled" if UI_CONFIG["show_streaming"] else "disabled"
            console.print(f"\n[green]✓ AI response streaming {status}[/green]")
            
        elif choice == "5":
            while True:
                try:
                    new_size = Prompt.ask(
                        f"[bold cyan]Enter new token window size (current: {CLIENT_CONFIG['token_window_size']}):[/bold cyan]",
                        default=str(CLIENT_CONFIG['token_window_size'])
                    )
                    new_size = int(new_size)
                    if new_size <= 0:
                        console.print("[red]Error: Token window size must be a positive integer.[/red]")
                    else:
                        CLIENT_CONFIG["token_window_size"] = new_size
                        console.print(f"\n[green]✓ Token window size set to {new_size}[/green]")
                        break
                except ValueError:
                    console.print("[red]Error: Invalid input. Please enter a number.[/red]")
            
        elif choice == "9":
            # Save the current configuration before exiting
            try:
                save_config()
            except Exception as e:
                console.print(f"[red]Failed to save configuration: {e}[/red]")
            console.print("\n[cyan]Exiting configuration menu...[/cyan]\n")
            break


import requests

def _select_model_from_openrouter():
    """
    Fetches models from OpenRouter, allows searching, pagination, and selection.

    Returns:
        str: The ID of the selected model, or None if no model is selected.
    """
    try:
        response = requests.get("https://openrouter.ai/api/v1/models")
        response.raise_for_status()
        models = response.json()["data"]
    except requests.RequestException as e:
        console.print(f"[red]Error fetching models from OpenRouter: {e}[/red]")
        return None

    page = 0
    page_size = 20
    filtered_models = models

    while True:
        console.print("\n[bold cyan]Select a model from OpenRouter:[/bold cyan]")
        
        start_index = page * page_size
        end_index = start_index + page_size
        
        paginated_models = filtered_models[start_index:end_index]
        
        table = Table(box=box.ROUNDED, border_style="cyan")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        
        for i, model in enumerate(paginated_models):
            table.add_row(str(start_index + i + 1), model["id"])
            
        console.print(table)
        
        prompt_text = (
            f"\n[bold cyan]Showing models {start_index + 1}-{min(end_index, len(filtered_models))} of {len(filtered_models)}. "
            "Enter a model ID to select, /search <query>, /next, /back, or /exit:[/bold cyan]"
        )
        
        user_input = Prompt.ask(prompt_text)

        if user_input.lower().startswith("/search"):
            query = user_input.split(maxsplit=1)[1] if len(user_input.split(maxsplit=1)) > 1 else ""
            filtered_models = [m for m in models if query.lower() in m["id"].lower()]
            page = 0
            continue
            
        elif user_input.lower() == "/next":
            if end_index < len(filtered_models):
                page += 1
            else:
                console.print("[yellow]Already on the last page.[/yellow]")
            continue

        elif user_input.lower() == "/back":
            if page > 0:
                page -= 1
            else:
                console.print("[yellow]Already on the first page.[/yellow]")
            continue
            
        elif user_input.lower() == "/exit":
            return None
            
        else:
            try:
                model_index = int(user_input) - 1
                if 0 <= model_index < len(filtered_models):
                    return filtered_models[model_index]["id"]
                else:
                    console.print("[red]Invalid model ID.[/red]")
            except ValueError:
                console.print("[red]Invalid input. Please enter a number or a command.[/red]")


def show_agents_menu():
    """
    Display and handle the agent management menu.
    
    Allows users to list, create, modify, and delete agents.
    """
    while True:
        console.print("\n" + "=" * 60)
        console.print("[bold cyan]🤖 Agent Management Menu[/bold cyan]")
        console.print("=" * 60 + "\n")
        
        table = Table(box=box.ROUNDED, border_style="cyan")
        table.add_column("Option", style="cyan", width=4)
        table.add_column("Description", style="white")
        
        table.add_row("1", "List all agents")
        table.add_row("2", "Create a new agent")
        table.add_row("3", "Modify an existing agent")
        table.add_row("4", "Delete an agent")
        table.add_row("9", "Exit Agent Management Menu")
        
        console.print(table)
        console.print()
        
        choice = Prompt.ask(
            "[bold cyan]Select an option (1-4) or 9 to exit[/bold cyan]",
            choices=["1", "2", "3", "4", "9"]
        )
        
        if choice == "1":
            agents = agent_manager.list_agents()
            render_agent_list(agents)
            
        elif choice == "2":
            agent_name = Prompt.ask("[bold cyan]Enter a name for the new agent[/bold cyan]")
            agent_desc = Prompt.ask(f"[bold cyan]Enter a description for {agent_name}[/bold cyan]")

            # Note: API key is loaded from .env (OPEN_ROUTER_API_KEY), not stored in agent config
            console.print("[dim]  API Key will be loaded from .env (OPEN_ROUTER_API_KEY)[/dim]")

            site_url = Prompt.ask(f"[bold cyan]Enter the site URL for {agent_name}[/bold cyan] (optional, press Enter to skip)", default="")
            site_name = Prompt.ask(f"[bold cyan]Enter the site name for {agent_name}[/bold cyan] (optional, press Enter to skip)", default="")

            selected_model = _select_model_from_openrouter()

            if selected_model:
                agent_details = {
                    "name": agent_name,
                    "description": agent_desc,
                    "site_url": site_url,
                    "site_name": site_name,
                    "model": selected_model
                }
                if agent_manager.create_agent(agent_name, agent_details):
                    console.print(f"\n[green]✓ Agent '{agent_name}' created successfully.[/green]")
                    console.print(f"[dim]  API key will be loaded from .env when agent is invoked[/dim]")
                else:
                    console.print(f"\n[red]Error: Agent '{agent_name}' already exists.[/red]")
            else:
                console.print(f"\n[red]Agent creation cancelled.[/red]")

        elif choice == "3":
            agent_name = Prompt.ask("[bold cyan]Enter the name of the agent to modify[/bold cyan]")
            if agent_name in agent_manager.list_agents():
                agent_details = agent_manager.get_agent_details(agent_name)

                new_desc = Prompt.ask(f"[bold cyan]Enter the new description for {agent_name}[/bold cyan]", default=agent_details.get("description"))

                # Note: API key is loaded from .env, not stored in agent config
                console.print("[dim]  API Key is loaded from .env (OPEN_ROUTER_API_KEY)[/dim]")

                new_site_url = Prompt.ask(f"[bold cyan]Enter the new site URL for {agent_name}[/bold cyan]", default=agent_details.get("site_url", ""))
                new_site_name = Prompt.ask(f"[bold cyan]Enter the new site name for {agent_name}[/bold cyan]", default=agent_details.get("site_name", ""))

                console.print(f"[bold cyan]Current model: {agent_details.get('model', 'Not set')}[/bold cyan]")
                if Confirm.ask("[bold cyan]Do you want to change the model?[/bold cyan]"):
                    selected_model = _select_model_from_openrouter()
                else:
                    selected_model = agent_details.get("model")

                if selected_model:
                    new_details = {
                        "name": agent_name,
                        "description": new_desc,
                        "site_url": new_site_url,
                        "site_name": new_site_name,
                        "model": selected_model
                    }

                    if agent_manager.modify_agent(agent_name, new_details):
                        console.print(f"\n[green]✓ Agent '{agent_name}' modified successfully.[/green]")
                    else:
                        console.print(f"\n[red]Error: Could not modify agent '{agent_name}'.[/red]")
                else:
                    console.print(f"\n[red]Agent modification cancelled.[/red]")
            else:
                console.print(f"\n[red]Error: Agent '{agent_name}' not found.[/red]")

        elif choice == "4":
            agent_name = Prompt.ask("[bold cyan]Enter the name of the agent to delete[/bold cyan]")
            if agent_name in agent_manager.list_agents():
                if Confirm.ask(f"\n[red]Are you sure you want to delete agent '{agent_name}'?[/red]", default=False):
                    if agent_manager.delete_agent(agent_name):
                        console.print(f"\n[green]✓ Agent '{agent_name}' deleted successfully.[/green]")
                    else:
                        console.print(f"\n[red]Error: Could not delete agent '{agent_name}'.[/red]")
            else:
                console.print(f"\n[red]Error: Agent '{agent_name}' not found.[/red]")
            
        elif choice == "9":
            console.print("\n[cyan]Exiting agent management menu...[/cyan]\n")
            break


def handle_command(
    manager: ConversationManager, 
    command: str, 
    current_conv_id: Optional[str]
) -> Tuple[bool, Optional[str]]:
    """
    Handle slash commands entered by the user.
    
    This function parses and executes various commands that allow the user
    to manage conversations without leaving the main chat interface.
    
    Available commands:
    - /help: Show help message
    - /new: Start a new conversation
    - /switch <id>: Switch to a different conversation
    - /list: List all conversations
    - /search <query>: Search conversations
    - /delete <id>: Delete a conversation
    - /exit: Exit the application
    
    Args:
        manager: The conversation manager instance
        command: The command string (including the leading /)
        current_conv_id: The ID of the currently active conversation
        
    Returns:
        Tuple[bool, Optional[str]]: (should_exit, new_conversation_id)
    """
    # Parse the command and its arguments
    parts = command[1:].split(maxsplit=1)
    cmd = parts[0].lower()
    
    # Help command - display available commands
    if cmd == "help":
        console.print("\n[bold cyan]Available Commands:[/bold cyan]")
        console.print("  [cyan]/help[/cyan]              - Show this help message")
        console.print("  [cyan]/new[/cyan]               - Start a new conversation")
        console.print("  [cyan]/switch <id>[/cyan]       - Switch to a different conversation")
        console.print("  [cyan]/list[/cyan]              - List all conversations")
        console.print("  [cyan]/search <query>[/cyan]    - Search conversations")
        console.print("  [cyan]/delete <id>[/cyan]       - Delete a conversation")
        console.print("  [cyan]/config[/cyan]            - Open configuration menu")
        console.print("  [cyan]/tools[/cyan]             - List all available tools and their descriptions")
        console.print("  [cyan]/agents[/cyan]            - Open agent management menu")
        console.print("  [cyan]/exit[/cyan]              - Exit the application\n")
        return False, current_conv_id
    
    # Agents command - open agent management menu
    elif cmd == "agents":
        show_agents_menu()
        return False, current_conv_id
    
    # Config command - open configuration menu
    elif cmd == "config":
        show_config_menu()
        return False, current_conv_id

    # Tools command - list available tools
    elif cmd == "tools":
        tools = manager.list_tool_details()
        if tools:
            table = Table(title="Available Tools", box=box.ROUNDED, border_style="cyan")
            table.add_column("Tool Name", style="cyan", no_wrap=True)
            table.add_column("Description", style="white")
            for tool in tools:
                table.add_row(tool["name"], tool["description"])
            console.print("\n")
            console.print(table)
            console.print("\n")
        else:
            console.print("\n[yellow]No tools currently available.[/yellow]\n")
        return False, current_conv_id
    
    # New command - start a new conversation
    elif cmd == "new":
        display_start_of_conversation()
        # Return None to clear the current conversation ID
        return False, None
    
    # Switch command - change to a different conversation
    elif cmd == "switch":
        # Validate that an ID was provided
        if len(parts) < 2:
            console.print("\n[red]Usage: /switch <conversation_id>[/red]\n")
            return False, current_conv_id
        
        conv_id = parts[1].strip()
        
        # Check if the conversation exists
        if conv_id in manager.conversations:
            conversation = manager.get_conversation(conv_id)
            if conversation:
                display_conversation_history(conversation["messages"])
            return False, conv_id
        else:
            console.print(f"\n[red]Conversation '{conv_id}' not found![/red]\n")
            return False, current_conv_id
    
    # List command - show all conversations
    elif cmd == "list":
        conversations = manager.list_conversations()
        
        # Show current conversation if there is one
        if current_conv_id:
            console.print(f"\n[dim]Current conversation: {current_conv_id}[/dim]")
        
        # Display the conversations table
        show_conversations_table(conversations, "All Conversations")
        return False, current_conv_id
    
    # Search command - find conversations by query
    elif cmd == "search":
        # Validate that a query was provided
        if len(parts) < 2:
            console.print("\n[red]Usage: /search <query>[/red]\n")
            return False, current_conv_id
        
        query = parts[1].strip()
        results = manager.search_conversations(query)
        
        # Display results or no results message
        if results:
            show_conversations_table(results, f"Search Results: '{query}'")
        else:
            console.print(f"\n[yellow]No conversations found matching '{query}'[/yellow]\n")
        
        return False, current_conv_id
    
    # Delete command - remove a conversation
    elif cmd == "delete":
        # Validate that an ID was provided
        if len(parts) < 2:
            console.print("\n[red]Usage: /delete <conversation_id>[/red]\n")
            return False, current_conv_id
        
        conv_id = parts[1].strip()
        
        # Check if the conversation exists
        if conv_id in manager.conversations:
            title = manager.conversations[conv_id]["title"]
            
            # Confirm deletion with the user
            if Confirm.ask(f"\n[red]Delete conversation '{title}'?[/red]", default=False):
                manager.delete_conversation(conv_id)
                console.print(f"\n[green]✓ Deleted conversation: {title}[/green]\n")
                
                # If we deleted the current conversation, clear it
                if conv_id == current_conv_id:
                    return False, None
        else:
            console.print(f"\n[red]Conversation '{conv_id}' not found![/red]\n")
        
        return False, current_conv_id
    
    # Exit/Quit command - terminate the application
    elif cmd == "exit" or cmd == "quit":
        console.print("\n[cyan]Goodbye! 👋[/cyan]\n")
        return True, current_conv_id
    
    # Unknown command - show error and hint
    else:
        console.print(f"\n[red]Unknown command: /{cmd}[/red]")
        console.print("[dim]Type /help for available commands[/dim]\n")
        return False, current_conv_id
