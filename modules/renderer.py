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
from rich.syntax import Syntax
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
  /compress             Manually compress conversation context
  /config               Open configuration menu
  /tools                List all available tools and their descriptions
  /agents               Manage AI agents
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

        # Track if we rendered anything
        rendered_something = False

        # Render main response with markdown formatting
        # Check both "response" (legacy) and "content" (OpenRouter standard)
        if "response" in data:
            console.print("\n")
            console.print(Markdown(data["response"]))
            rendered_something = True
        elif "content" in data and isinstance(data["content"], str):
            console.print("\n")
            console.print(Markdown(data["content"]))
            rendered_something = True

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
            rendered_something = True

        # Render key points as a bulleted list
        if "key_points" in data and data["key_points"]:
            console.print("\n[bold yellow]🔑 Key Points:[/bold yellow]")
            for point in data["key_points"]:
                console.print(f"  • {point}")
            rendered_something = True

        # Render next steps as a numbered list
        if "next_steps" in data and data["next_steps"]:
            console.print("\n[bold green]➡️  Next Steps:[/bold green]")
            for idx, step in enumerate(data["next_steps"], 1):
                console.print(f"  {idx}. {step}")
            rendered_something = True

        # If we didn't render anything from the structured fields, show the raw JSON
        if not rendered_something:
            console.print("\n")
            console.print(Markdown(f"```json\n{json.dumps(data, indent=2)}\n```"))

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
    - Plan name
    - Sequential step visualization
    - Tool details for each step

    Args:
        plan: Plan dictionary with name and steps
              Format: {
                  "name": "Plan Name",
                  "steps": [
                      {
                          "step_number": 1,
                          "description": "Step description",
                          "tool": "TOOL_NAME__method",
                          "arguments": "{\"param\": \"value\"}"
                      }
                  ]
              }
    """
    # Create plan header
    console.print("\n" + "─" * 80)
    console.print(f"[bold cyan]EXECUTION PLAN[/bold cyan]")
    console.print("─" * 80)

    # Display plan name
    plan_name = plan.get("name", "Unnamed Plan")
    console.print(f"\n[bold white]Plan:[/bold white] {plan_name}\n")

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
    table.add_column("Description", style="white", width=50)
    table.add_column("Tool", style="green", width=20)

    # Add each step to the table
    for step in steps:
        step_num = step.get("step_number", "?")
        step_desc = step.get("description", "No description")

        # Extract tool information from string format "TOOL_NAME__method"
        tool_str = step.get("tool", "")
        if "__" in tool_str:
            tool_name, method = tool_str.split("__", 1)
            tool_display = f"{tool_name}.{method}"
        else:
            tool_display = tool_str or "N/A"

        # Add row to table
        table.add_row(
            str(step_num),
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


def render_plan_update(old_plan: dict, new_plan: dict):
    """
    Render a comparison between the original plan and an updated plan.

    Displays:
    - Plan name changes
    - Side-by-side comparison of steps
    - Added/removed/modified steps

    Args:
        old_plan: Original plan dictionary
        new_plan: Updated plan dictionary
    """
    console.print("\n" + "─" * 80)
    console.print("[bold yellow]PLAN UPDATE[/bold yellow]")
    console.print("─" * 80 + "\n")

    # Show plan name change if different
    old_name = old_plan.get("name", "Unnamed Plan")
    new_name = new_plan.get("name", "Unnamed Plan")

    if old_name != new_name:
        console.print(f"[dim]Plan name:[/dim]")
        console.print(f"  [red]- {old_name}[/red]")
        console.print(f"  [green]+ {new_name}[/green]\n")
    else:
        console.print(f"[bold white]Plan:[/bold white] {new_name}\n")

    # Get steps
    old_steps = old_plan.get("steps", [])
    new_steps = new_plan.get("steps", [])

    # Create comparison table
    table = Table(
        box=box.HEAVY_HEAD,
        border_style="yellow",
        header_style="bold yellow",
        show_lines=True
    )

    table.add_column("Step", style="cyan", width=4, justify="center")
    table.add_column("Status", style="white", width=8, justify="center")
    table.add_column("Description", style="white", width=50)
    table.add_column("Tool", style="green", width=20)

    # Build step mapping for comparison
    max_steps = max(len(old_steps), len(new_steps))

    for i in range(max_steps):
        old_step = old_steps[i] if i < len(old_steps) else None
        new_step = new_steps[i] if i < len(new_steps) else None

        if old_step and new_step:
            # Both exist - check if modified
            old_desc = old_step.get("description", "")
            new_desc = new_step.get("description", "")
            old_tool = old_step.get("tool", "")
            new_tool = new_step.get("tool", "")

            if old_desc == new_desc and old_tool == new_tool:
                # Unchanged
                status = "="
                status_style = "dim white"
                desc_text = new_desc
                tool_text = new_tool.replace("__", ".")
            else:
                # Modified
                status = "~"
                status_style = "yellow"
                desc_text = f"{old_desc}\n→ {new_desc}"
                old_tool_display = old_tool.replace("__", ".")
                new_tool_display = new_tool.replace("__", ".")
                tool_text = f"{old_tool_display}\n→ {new_tool_display}"
        elif new_step:
            # Added step
            status = "+"
            status_style = "green"
            desc_text = new_step.get("description", "")
            tool_text = new_step.get("tool", "").replace("__", ".")
        elif old_step:
            # Removed step
            status = "-"
            status_style = "red"
            desc_text = old_step.get("description", "")
            tool_text = old_step.get("tool", "").replace("__", ".")
        else:
            continue

        table.add_row(
            str(i + 1),
            Text(status, style=status_style),
            desc_text,
            tool_text
        )

    console.print(table)

    # Summary of changes
    console.print(f"\n[dim]Legend: [green]+[/green] Added  [yellow]~[/yellow] Modified  [red]-[/red] Removed  [dim]=[/dim] Unchanged[/dim]")
    console.print(f"[dim]Total steps: {len(old_steps)} → {len(new_steps)}[/dim]")
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


def render_agent_list(agents: list):
    """
    Display agents in a formatted table.
    
    Args:
        agents: List of agent names
    """
    if not agents:
        console.print(f"\n[yellow]No agents found.[/yellow]\n")
        return
    
    table = Table(title="Available Agents", box=box.ROUNDED, border_style="cyan")
    table.add_column("Agent Name", style="cyan", no_wrap=True)
    
    for agent in agents:
        table.add_row(agent)
    
    console.print("\n")
    console.print(table)
    console.print()


def render_agent_details(agent_details: dict):
    """
    Display the details of an agent in a panel.

    Args:
        agent_details: Dictionary of agent details
    """
    if not agent_details:
        console.print(f"\n[yellow]No agent details found.[/yellow]\n")
        return

    panel_content = f"[bold]Name:[/bold] {agent_details.get('name', 'N/A')}\n"
    panel_content += f"[bold]Description:[/bold] {agent_details.get('description', 'N/A')}"

    console.print(Panel(
        panel_content,
        title="Agent Details",
        box=box.ROUNDED,
        border_style="cyan",
        padding=(1, 2)
    ))
    console.print()


def render_diff(diff_text: str, file_path: str = "file", dry_run: bool = False):
    """
    Render a unified diff with syntax highlighting and line numbers.

    Displays diffs in a git-style format with:
    - Green background for added lines
    - Red background for removed lines
    - Line numbers on the left
    - File path in header

    Args:
        diff_text: Unified diff string
        file_path: Path to the file being edited
        dry_run: Whether this is a dry run preview
    """
    if not diff_text:
        console.print("[dim]No changes to display[/dim]")
        return

    # Parse the diff to extract line numbers and changes
    lines = diff_text.split('\n')

    # Build styled output
    output = Text()

    # Track line numbers
    old_line_num = 0
    new_line_num = 0
    in_hunk = False

    for line in lines:
        # File header lines
        if line.startswith('---') or line.startswith('+++'):
            styled_line = Text(line, style="bold cyan")
            output.append(styled_line)
            output.append("\n")
            continue

        # Hunk header (e.g., @@ -1,4 +1,4 @@)
        if line.startswith('@@'):
            # Extract line numbers from hunk header
            match = re.search(r'@@ -(\d+),?\d* \+(\d+),?\d* @@', line)
            if match:
                old_line_num = int(match.group(1))
                new_line_num = int(match.group(2))
                in_hunk = True

            styled_line = Text(line, style="bold magenta")
            output.append(styled_line)
            output.append("\n")
            continue

        if not in_hunk:
            continue

        # Removed line (starts with -)
        if line.startswith('-') and not line.startswith('---'):
            # Line number and content
            line_num_str = f"{old_line_num:4d} "
            content = line[1:]  # Remove the - prefix

            styled_line = Text()
            styled_line.append(line_num_str, style="dim red")
            styled_line.append("│ ", style="dim")
            styled_line.append(f"- {content}", style="red on #2d0d0d")
            output.append(styled_line)
            output.append("\n")

            old_line_num += 1
            continue

        # Added line (starts with +)
        if line.startswith('+') and not line.startswith('+++'):
            # Line number and content
            line_num_str = f"{new_line_num:4d} "
            content = line[1:]  # Remove the + prefix

            styled_line = Text()
            styled_line.append(line_num_str, style="dim green")
            styled_line.append("│ ", style="dim")
            styled_line.append(f"+ {content}", style="green on #0d2d0d")
            output.append(styled_line)
            output.append("\n")

            new_line_num += 1
            continue

        # Context line (starts with space or is empty)
        if line.startswith(' ') or line == '':
            content = line[1:] if line else ''

            # Show both line numbers for context
            line_num_str = f"{old_line_num:4d} "

            styled_line = Text()
            styled_line.append(line_num_str, style="dim")
            styled_line.append("│ ", style="dim")
            styled_line.append(f"  {content}", style="dim white")
            output.append(styled_line)
            output.append("\n")

            old_line_num += 1
            new_line_num += 1
            continue

    # Display in a panel
    title = f"{'[DRY RUN] ' if dry_run else ''}Changes to {file_path}"
    border_style = "yellow" if dry_run else "green"

    console.print()
    console.print(Panel(
        output,
        title=title,
        box=box.ROUNDED,
        border_style=border_style,
        padding=(0, 1)
    ))
    console.print()
