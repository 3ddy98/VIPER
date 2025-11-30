"""
Tool Template

This file serves as a template for creating new tools for the SEBESKY-GPT agent.
Follow the structure and conventions in this file to ensure your tool is
correctly integrated with the tool manager.

A tool should be a self-contained class that:
- Exposes public methods for the AI to call.
- Returns JSON-serializable results.
- Provides a `get_tool_spec()` method to describe its capabilities.
"""

from typing import Dict, Any, Optional

# --- Tool Class Definition ---
# Each tool is a class that encapsulates its logic and state.

class MyTool:
    """
    A template for creating a new tool.
    
    Rename this class and update the docstring to describe your tool's purpose.
    """
    
    def __init__(self, some_config: Optional[str] = None):
        """
        Initialize the tool.
        
        The constructor is a good place to:
        - Set up any initial state (e.g., API clients, base paths).
        - Define the unique `tool_name`. This name is used by the AI to
          identify and call the tool.
        - Load any configuration that the tool might need.
        
        Args:
            some_config: An example configuration parameter.
        """
        self.tool_name = "MY_TOOL"  # <-- IMPORTANT: Change to a unique, descriptive name
        self.config = some_config or "default_value"

    # --- Tool Methods ---
    # Public methods are the functions that the AI can execute.
    
    def perform_action_one(self, a_string: str, a_number: int) -> Dict[str, Any]:
        """
        An example of a non-destructive tool method.
        
        Method Naming:
        - Use descriptive, snake_case names (e.g., `get_weather_forecast`).
        
        Parameters:
        - All parameters must be JSON-serializable (str, int, bool, list, dict).
        - Provide type hints and clear docstrings for each parameter.
        
        Returns:
        - MUST return a dictionary.
        - The dictionary MUST contain a "success": True/False field.
        - On success, include the results in the dictionary.
        - On failure, include an "error": "message" field.
        """
        try:
            # Your method's logic goes here
            result_data = {
                "input_string": a_string,
                "doubled_number": a_number * 2,
                "config_used": self.config
            }
            
            # Return a success dictionary
            return {
                "success": True,
                "result": result_data
            }
            
        except Exception as e:
            # On any error, return a failure dictionary
            return {
                "success": False,
                "error": f"An unexpected error occurred in perform_action_one: {str(e)}"
            }

    def perform_destructive_action(self, target_id: str, force: bool = False) -> Dict[str, Any]:
        """
        An example of a destructive method.
        
        Destructive methods (e.g., deleting data, modifying files) should be
        clearly marked in the tool spec with `destruct_flag: True`.
        
        Args:
            target_id: The ID of the item to modify or delete.
            force: A flag to bypass safety checks (use with caution).
        
        Returns:
            A dictionary indicating success or failure.
        """
        try:
            # Add safety checks here
            if not force:
                return {
                    "success": False,
                    "error": "Destructive action requires 'force=True'. Please confirm."
                }
            
            # Your destructive logic goes here
            # e.g., os.remove(f"/path/to/{target_id}")
            
            return {
                "success": True,
                "message": f"Successfully deleted item {target_id}."
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to perform destructive action: {str(e)}"
            }
            
    # --- Tool Specification ---
    # The `get_tool_spec` method is CRITICAL for AI integration.
    
    def get_tool_spec(self) -> Dict[str, Any]:
        """
        Returns the tool's specification in a structured dictionary format.
        
        This specification tells the AI:
        - The tool's name and what it does.
        - The available methods, their purpose, parameters, and return values.
        - Whether a method is destructive.
        
        Returns:
            A dictionary containing the complete tool specification.
        """
        return {
            "tool_name": self.tool_name,
            "description": "A brief, clear description of what this tool does overall.",
            "version": "1.0.0",  # Optional: for version tracking
            "methods": [
                {
                    "name": "perform_action_one",
                    "description": "A clear, one-sentence description of what this specific method does.",
                    "parameters": {
                        "a_string": {
                            "type": "string",
                            "description": "Description of what this string parameter represents.",
                            "required": True
                        },
                        "a_number": {
                            "type": "integer",
                            "description": "Description of what this number is for.",
                            "required": True
                        }
                    },
                    "returns": "A dictionary containing the processed data.",
                    "destruct_flag": False  # <-- Set to False for read-only actions
                },
                {
                    "name": "perform_destructive_action",
                    "description": "Performs a destructive action, like deleting an item.",
                    "parameters": {
                        "target_id": {
                            "type": "string",
                            "description": "The unique identifier of the item to be deleted.",
                            "required": True
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Must be set to true to confirm the destructive operation.",
                            "required": False,
                            "default": False
                        }
                    },
                    "returns": "A confirmation message upon successful deletion.",
                    "destruct_flag": True  # <-- IMPORTANT: Set to True for destructive actions
                }
            ]
        }

# --- Helper Methods (Optional) ---
# Private helper methods can be defined outside or inside the class.
# Use an underscore prefix (e.g., `_my_helper`) to indicate they are not
# part of the public tool interface.

def _private_helper_function():
    """An example of a private helper function."""
    return "This is a helper"
