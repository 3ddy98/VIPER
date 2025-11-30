"""
Renderer Module

This module handles all UI rendering functions including:
- JSON response formatting and display
- Conversation tables
- Banner display
- Rich-styled console output
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich import box
from rich.text import Text
from rich.rule import Rule
from modules.banner import get_banner


# Initialize Rich console for output
console = Console()


def display_onboarding():
    """
    Display a professional onboarding experience with animated effects.
    
    Shows:
    - Application banner
    - Available commands
    """
    try:
        from terminaltexteffects.effects.effect_print import Print
        use_effects = True
    except ImportError:
        use_effects = False
    
    # Display banner
    console.clear()
    banner_text = get_banner()

    if use_effects:
        effect = Print(banner_text)
        effect.effect_config.print_speed = 8
        effect.effect_config.print_head_return_speed = 3.0
        effect.terminal_config.frame_rate = 120
        with effect.terminal_output() as terminal:
            for frame in effect:
                terminal.print(frame)
    else:
        console.print(banner_text)

    # Available commands
    commands_text = """
  /help                 Show this help message
  /new                  Start a new conversation
  /switch <id>          Switch to a different conversation
  /list                 List all conversations
  /search <query>       Search conversations
  /delete <id>          Delete a conversation
  /config               Open configuration menu
  /tools                List all available tools and their descriptions
  /exit                 Exit the application
"""
    
    console.print(Panel(
        commands_text,
        title="Available Commands",
        box=box.ROUNDED,
        border_style="cyan",
        padding=(1, 2)
    ))
    
    console.print()


def display_start_of_conversation():
    """
    Clears the console and displays a 'Start of Conversation' box.
    """
    console.clear()
    console.print(Panel(
        "Start of Conversation",
        box=box.ROUNDED,
        border_style="green",
        padding=(0, 1)
    ))
    console.print()


def display_conversation_history(messages: List[Dict]):
    """
    Displays the conversation history.

    Args:
        messages (List[Dict]): A list of message dictionaries.
    """
    console.clear()
    for message in messages:
        if message["role"] == "user":
            console.print(f"[bold green]You:[/bold green] {message['content']}")
        elif message["role"] == "assistant":
            console.print("\n[bold cyan]Assistant:[/bold cyan]")
            render_json_response(message['content'])
        # System messages are not displayed in the history


def render_json_response(response_text: str):
    """
    Render a JSON formatted response with Rich styling.
    
    This function:
    1. Strips special tokens from the response
    2. Extracts the JSON portion
    3. Parses and renders with beautiful formatting
    4. Falls back to markdown if JSON parsing fails
    
    Args:
        response_text: The raw response text from the AI
    """
    # Preprocess: Strip special tokens and extract JSON
    cleaned_text = response_text
    
    # Remove special tokens like <|channel|>, <|end|>, <|start|>, etc.
    # These are sometimes added by certain AI models during reasoning
    cleaned_text = re.sub(r'<\|[^|]+\|>', '', cleaned_text)
    
    # Try to extract JSON object from the response
    # Look for content between the first { and last }
    json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
    if json_match:
        cleaned_text = json_match.group(0)
    
    try:
        # Parse the JSON response
        data = json.loads(cleaned_text)
        
        # Render main response with markdown formatting
        if "response" in data:
            console.print("\n")
            console.print(Markdown(data["response"]))
        
        # Render code snippets in styled panels
        if "code_snippets" in data and data["code_snippets"]:
            console.print("\n[bold cyan]📝 Code Snippets:[/bold cyan]")
            for idx, snippet in enumerate(data["code_snippets"], 1):
                lang = snippet.get("language", "text")
                code = snippet.get("code", "")
                desc = snippet.get("description", "")
                
                # Show description if available
                if desc:
                    console.print(f"\n[dim]{desc}[/dim]")
                
                # Display code in a bordered panel
                console.print(Panel(
                    code,
                    title=f"[cyan]{lang}[/cyan]",
                    border_style="cyan",
                    box=box.ROUNDED
                ))
        
        # Render key points as a bulleted list
        if "key_points" in data and data["key_points"]:
            console.print("\n[bold yellow]🔑 Key Points:[/bold yellow]")
            for point in data["key_points"]:
                console.print(f"  • {point}")
        
        # Render next steps as a numbered list
        if "next_steps" in data and data["next_steps"]:
            console.print("\n[bold green]➡️  Next Steps:[/bold green]")
            for idx, step in enumerate(data["next_steps"], 1):
                console.print(f"  {idx}. {step}")
        
        console.print()
        
    except json.JSONDecodeError:
        # If JSON parsing fails, fall back to markdown rendering
        console.print("\n[yellow]⚠️  Response not in JSON format, displaying as markdown:[/yellow]\n")
        console.print(Markdown(response_text))



def show_conversations_table(conversations: List[Dict], title: str = "Conversations"):
    """
    Display conversations in a formatted table.
    
    Shows a Rich table with conversation metadata including:
    - ID (simple number for easy reference)
    - Title (conversation name)
    - Created date
    - Message count
    
    Args:
        conversations: List of conversation dictionaries
        title: Title for the table
    """
    # Handle empty conversation list
    if not conversations:
        console.print(f"\n[yellow]No conversations found.[/yellow]\n")
        return
    
    # Create a styled table with rounded borders
    table = Table(title=title, box=box.ROUNDED, border_style="cyan")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="white")
    table.add_column("Created", style="dim")
    table.add_column("Messages", justify="right", style="green")
    
    # Add rows for each conversation
    for conv in conversations:
        # Format the creation date
        created = datetime.fromisoformat(conv["created"]).strftime("%Y-%m-%d %H:%M")
        messages = str(conv.get("messages", 0))
        table.add_row(conv["id"], conv["title"], created, messages)
    
    # Display the table
    console.print("\n")
    console.print(table)
    console.print()


def render_plan(plan: dict):
    """
    Render an execution plan with professional styling.
    
    Displays a multi-step plan with:
    - Plan name and description
    - Sequential step visualization
    - Tool details for each step
    
    Args:
        plan: Plan dictionary with name, description, and steps
    """
    # Create plan header
    console.print("\n" + "─" * 80)
    console.print(f"[bold cyan]EXECUTION PLAN[/bold cyan]")
    console.print("─" * 80)
    
    # Display plan name and description
    plan_name = plan.get("name", "Unnamed Plan")
    plan_desc = plan.get("description", "No description provided")
    
    console.print(f"\n[bold white]Plan:[/bold white] {plan_name}")
    console.print(f"[dim]{plan_desc}[/dim]\n")
    
    # Get steps
    steps = plan.get("steps", [])
    
    if not steps:
        console.print("[yellow]No steps defined in plan[/yellow]\n")
        return
    
    # Display steps in a professional table
    table = Table(
        box=box.HEAVY_HEAD,
        border_style="cyan",
        header_style="bold cyan",
        show_lines=True
    )
    
    table.add_column("Step", style="cyan", width=4, justify="center")
    table.add_column("Operation", style="white", width=25)
    table.add_column("Description", style="dim white", width=35)
    table.add_column("Tool", style="green", width=14)
    
    # Add each step to the table
    for idx, step in enumerate(steps, 1):
        step_name = step.get("name", f"Step {idx}")
        step_desc = step.get("description", "")
        
        # Extract tool information
        tool_info = step.get("tool", {})
        tool_name = tool_info.get("tool_name", "N/A")
        method = tool_info.get("method", "N/A")
        tool_display = f"{tool_name}.{method}" if tool_name != "N/A" else "N/A"
        
        # Add row to table
        table.add_row(
            str(idx),
            step_name,
            step_desc,
            tool_display
        )
    
    console.print(table)
    
    # Display total steps count
    console.print(f"\n[dim]Total Steps: {len(steps)}[/dim]")
    console.print("─" * 80 + "\n")


def render_plan_step_result(step_number: int, step_name: str, success: bool, result: dict = None):
    """
    Render the result of a plan step execution.
    
    Args:
        step_number: The step number (1-indexed)
        step_name: Name of the step
        success: Whether the step succeeded
        result: Optional result dictionary
    """
    status_symbol = "✓" if success else "✗"
    status_color = "green" if success else "red"
    
    console.print(f"[{status_color}]Step {step_number} {status_symbol}[/{status_color}] [white]{step_name}[/white]")
    
    if not success and result:
        error_msg = result.get("error", "Unknown error")
        console.print(f"  [red]Error: {error_msg}[/red]")
    elif success:
        console.print(f"  [dim]Completed successfully[/dim]")

def render_plan_summary(plan_name: str, total_steps: int, successful_steps: int, results: list):
    """
    Render a summary of plan execution.
    
    Args:
        plan_name: Name of the plan
        total_steps: Total number of steps
        successful_steps: Number of successful steps
        results: List of step results
    """
    console.print("\n" + "─" * 80)
    console.print("[bold cyan]PLAN EXECUTION SUMMARY[/bold cyan]")
    console.print("─" * 80 + "\n")
    
    console.print(f"[bold white]Plan:[/bold white] {plan_name}")
    console.print(f"[white]Steps Completed:[/white] {successful_steps}/{total_steps}")
    
    # Determine overall status
    if successful_steps == total_steps:
        status = "[green]SUCCESS[/green]"
    elif successful_steps == 0:
        status = "[red]FAILED[/red]"
    else:
        status = "[yellow]PARTIAL[/yellow]"
    
    console.print(f"[white]Status:[/white] {status}\n")
    
    console.print("─" * 80 + "\n")

def render_status_bar(directory: str, token_info: str, date_time_info: str):
    """
    Renders a status bar with pre-formatted information.
    """
    status_text = f"[dim]{directory}[/dim] | [cyan]{token_info}[/cyan] | [dim]{date_time_info}[/dim]"
    
    console.print(Panel(
        status_text,
        box=box.ROUNDED,
        border_style="dim"
    ))



def render_input_box():
    """
    Renders a separator line above the input prompt.
    """
    console.print(Rule(style="dim"))
