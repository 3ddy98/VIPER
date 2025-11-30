"""
Edit File Tool

This tool allows the AI agent to edit files on the host file system.
All operations are DESTRUCTIVE and should be used with caution.

The tool provides:
- Text replacement in files.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

class EditFileTool:
    """
    File editing tool for AI agents.
    
    This tool provides destructive methods to modify files.
    All operations should be confirmed by the user unless auto-execute is enabled.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the Edit File tool.
        
        Args:
            base_path: Optional base path to restrict access (default: current directory)
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.tool_name = "EDIT_FILE"
    
    def replace_text(self, file_path: str, old_text: str, new_text: str, count: int = 1) -> Dict[str, Any]:
        """
        Replace a specific string in a file.
        
        Args:
            file_path: Path to the file to edit.
            old_text: The exact text to be replaced.
            new_text: The new text to replace the old_text with.
            count: The number of occurrences to replace. Defaults to 1.
                   If set to 0, all occurrences will be replaced.
                   
        Returns:
            A dictionary indicating success or failure.
        """
        try:
            target_path = self.base_path / file_path
            
            # Security check: ensure we're not escaping base_path
            if not self._is_safe_path(target_path):
                return {
                    "success": False,
                    "error": "Access denied: Path is outside allowed directory"
                }
            
            if not target_path.exists():
                return {
                    "success": False,
                    "error": f"File does not exist: {file_path}"
                }
            
            if not target_path.is_file():
                return {
                    "success": False,
                    "error": f"Path is not a file: {file_path}"
                }

            # Read the file content
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if old_text exists
            if old_text not in content:
                return {
                    "success": False,
                    "error": f"The specified 'old_text' was not found in the file."
                }
            
            # Perform the replacement
            if count == 0:
                new_content = content.replace(old_text, new_text)
            else:
                new_content = content.replace(old_text, new_text, count)
                
            # Write the modified content back to the file
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            return {
                "success": True,
                "message": f"Successfully replaced text in {file_path}."
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error editing file: {str(e)}"
            }

    def get_tool_spec(self) -> Dict[str, Any]:
        """
        Get the tool specification for AI agent integration.
        
        Returns:
            Dict containing tool name, methods, parameters, and metadata
        """
        return {
            "tool_name": self.tool_name,
            "description": "A tool for editing files. All methods are destructive.",
            "version": "1.0.0",
            "methods": [
                {
                    "name": "replace_text",
                    "description": "Replaces a specific string of text in a file. This is a destructive action.",
                    "parameters": {
                        "file_path": {
                            "type": "string",
                            "description": "The relative path to the file to be edited.",
                            "required": True
                        },
                        "old_text": {
                            "type": "string",
                            "description": "The exact block of text to be found and replaced. Must be an exact match.",
                            "required": True
                        },
                        "new_text": {
                            "type": "string",
                            "description": "The new block of text that will replace the old_text.",
                            "required": True
                        },
                        "count": {
                            "type": "integer",
                            "description": "The number of occurrences to replace. Set to 1 for the first match, or 0 to replace all matches.",
                            "required": False,
                            "default": 1
                        }
                    },
                    "returns": "A dictionary with a success message or an error.",
                    "destruct_flag": True
                }
            ]
        }

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is within allowed directory."""
        try:
            path.resolve().relative_to(self.base_path.resolve())
            return True
        except ValueError:
            return False
