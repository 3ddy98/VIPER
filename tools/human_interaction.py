"""
Human Interaction Tool

This tool allows the AI agent to explicitly ask the user for information
or a decision, and wait for their response.
"""

from typing import Dict, Any, Optional, List
from rich.prompt import Prompt

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
            # The prompt is displayed to the user, and the agent execution will
            # block until the user provides their input.
            answer = Prompt.ask(
                f"[bold yellow]Question from the agent:[/bold yellow] {question}",
                choices=choices,
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
