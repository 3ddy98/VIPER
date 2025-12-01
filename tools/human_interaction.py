"""
Human Interaction Tool

This tool allows the AI agent to explicitly ask the user for information
or a decision, and wait for their response.
"""

from typing import Dict, Any, Optional, List
from rich.prompt import Prompt, IntPrompt
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

class HumanInteractionTool:
    """
    A tool for the AI agent to interact with the human user.
    """

    def __init__(self):
        """
        Initialize the Human Interaction tool.
        """
        self.tool_name = "HUMAN_INTERACTION"

    def ask_question(
        self,
        question: str,
        choices: Optional[List[str]] = None,
        default: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Asks the user a question and waits for their input.

        Args:
            question: The question to ask the user.
            choices: An optional list of valid choices for the user's answer.
            default: An optional default value for the answer.

        Returns:
            A dictionary containing the user's answer.
        """
        try:
            if choices:
                # Display numbered options with a table
                console.print(f"\n[bold yellow]Question from the agent:[/bold yellow] {question}\n")

                table = Table(
                    box=box.ROUNDED,
                    border_style="cyan",
                    show_header=False,
                    padding=(0, 1)
                )
                table.add_column("Number", style="cyan", width=6, justify="right")
                table.add_column("Option", style="white")

                for idx, choice in enumerate(choices, 1):
                    table.add_row(f"{idx}.", choice)

                console.print(table)
                console.print()

                # Get user's numeric choice
                while True:
                    try:
                        choice_num = IntPrompt.ask(
                            "[cyan]Enter your choice (number)[/cyan]",
                            default=1 if default is None else choices.index(default) + 1 if default in choices else 1
                        )

                        if 1 <= choice_num <= len(choices):
                            answer = choices[choice_num - 1]
                            console.print(f"[dim]Selected: {answer}[/dim]\n")
                            break
                        else:
                            console.print(f"[red]Please enter a number between 1 and {len(choices)}[/red]")
                    except ValueError:
                        console.print("[red]Please enter a valid number[/red]")
            else:
                # Free-form text input
                answer = Prompt.ask(
                    f"[bold yellow]Question from the agent:[/bold yellow] {question}",
                    default=default
                )

            return {
                "success": True,
                "answer": answer
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"An error occurred while asking the user: {str(e)}"
            }

    def get_tool_spec(self) -> Dict[str, Any]:
        """
        Get the tool specification for AI agent integration.
        """
        return {
            "tool_name": self.tool_name,
            "description": "A tool to ask the human user a question and get their answer.",
            "methods": [
                {
                    "name": "ask_question",
                    "description": "Asks the user a question and returns their answer. Use this when you need a specific piece of information or a decision from the user before proceeding.",
                    "parameters": {
                        "question": {
                            "type": "string",
                            "description": "The question to be presented to the user.",
                            "required": True
                        },
                        "choices": {
                            "type": "array",
                            "description": "An optional list of allowed answers. If provided, the user will be forced to choose one.",
                            "required": False
                        },
                        "default": {
                            "type": "string",
                            "description": "An optional default answer to use if the user provides no input.",
                            "required": False
                        }
                    },
                    "returns": "A dictionary containing the user's answer under the 'answer' key.",
                    "destruct_flag": False
                }
            ]
        }
