"""
File Manager Tool

This tool allows the AI agent to perform DESTRUCTIVE file system
operations like creating, moving, and deleting files and directories.
Extreme caution is advised.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

class FileManagerTool:
    """
    File system management tool for AI agents.
    
    Provides destructive methods for file and directory manipulation.
    All operations should be confirmed by the user.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the File Manager tool.
        
        Args:
            base_path: Optional base path to restrict access (default: current directory)
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.tool_name = "FILE_MANAGER"
        
    def create_file(self, file_path: str, content: str = "") -> Dict[str, Any]:
        """
        Create a new file with optional content.
        
        Args:
            file_path: The path of the file to create.
            content: Optional content to write to the new file.
            
        Returns:
            A dictionary indicating success or failure.
        """
        try:
            target_path = self.base_path / file_path
            
            if not self._is_safe_path(target_path):
                return {"success": False, "error": "Access denied"}

            if target_path.exists():
                return {"success": False, "error": f"File already exists: {file_path}"}
            
            # Create parent directories if they don't exist
            target_path.parent.mkdir(parents=True, exist_ok=True)

            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return {"success": True, "message": f"File created: {file_path}"}
        except Exception as e:
            return {"success": False, "error": f"Error creating file: {str(e)}"}

    def create_directory(self, dir_path: str) -> Dict[str, Any]:
        """
        Create a new directory.
        
        Args:
            dir_path: The path of the directory to create.
            
        Returns:
            A dictionary indicating success or failure.
        """
        try:
            target_path = self.base_path / dir_path
            
            if not self._is_safe_path(target_path):
                return {"success": False, "error": "Access denied"}

            if target_path.exists():
                return {"success": False, "error": f"Directory already exists: {dir_path}"}

            target_path.mkdir(parents=True, exist_ok=True)
            return {"success": True, "message": f"Directory created: {dir_path}"}
        except Exception as e:
            return {"success": False, "error": f"Error creating directory: {str(e)}"}

    def move(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        """
        Move a file or directory.
        
        Args:
            source_path: The path of the file/directory to move.
            destination_path: The destination path.
            
        Returns:
            A dictionary indicating success or failure.
        """
        try:
            source = self.base_path / source_path
            destination = self.base_path / destination_path
            
            if not self._is_safe_path(source) or not self._is_safe_path(destination):
                return {"success": False, "error": "Access denied"}
            
            if not source.exists():
                return {"success": False, "error": f"Source path not found: {source_path}"}

            shutil.move(str(source), str(destination))
            return {"success": True, "message": f"Moved {source_path} to {destination_path}"}
        except Exception as e:
            return {"success": False, "error": f"Error moving: {str(e)}"}

    def delete(self, path: str, recursive: bool = False) -> Dict[str, Any]:
        """
        Delete a file or directory.
        
        Args:
            path: The path of the file/directory to delete.
            recursive: If True, allows recursive deletion of directories. 
                       Required to delete non-empty directories. Defaults to False.
                       
        Returns:
            A dictionary indicating success or failure.
        """
        try:
            target_path = self.base_path / path
            
            if not self._is_safe_path(target_path):
                return {"success": False, "error": "Access denied"}
            
            if not target_path.exists():
                return {"success": False, "error": f"Path not found: {path}"}

            if target_path.is_file():
                target_path.unlink()
                return {"success": True, "message": f"File deleted: {path}"}
            
            if target_path.is_dir():
                if any(target_path.iterdir()) and not recursive:
                    return {"success": False, "error": f"Directory is not empty. Use recursive=True to delete."}
                shutil.rmtree(target_path)
                return {"success": True, "message": f"Directory deleted: {path}"}

            return {"success": False, "error": "Path is not a file or directory."}
        except Exception as e:
            return {"success": False, "error": f"Error deleting: {str(e)}"}

    def get_tool_spec(self) -> Dict[str, Any]:
        """Get the tool specification for AI agent integration."""
        return {
            "tool_name": self.tool_name,
            "description": "A tool for creating, moving, and deleting files and directories. All methods are destructive.",
            "methods": [
                {
                    "name": "create_file",
                    "description": "Creates a new file, with optional content.",
                    "parameters": {
                        "file_path": {"type": "string", "description": "The path for the new file.", "required": True},
                        "content": {"type": "string", "description": "Optional content for the file.", "required": False, "default": ""}
                    },
                    "returns": "A confirmation message.",
                    "destruct_flag": True
                },
                {
                    "name": "create_directory",
                    "description": "Creates a new directory.",
                    "parameters": {
                        "dir_path": {"type": "string", "description": "The path for the new directory.", "required": True}
                    },
                    "returns": "A confirmation message.",
                    "destruct_flag": True
                },
                {
                    "name": "move",
                    "description": "Moves a file or directory from a source to a destination.",
                    "parameters": {
                        "source_path": {"type": "string", "description": "The path of the file/directory to move.", "required": True},
                        "destination_path": {"type": "string", "description": "The destination path.", "required": True}
                    },
                    "returns": "A confirmation message.",
                    "destruct_flag": True
                },
                {
                    "name": "delete",
                    "description": "Deletes a file or directory. Highly destructive.",
                    "parameters": {
                        "path": {"type": "string", "description": "The path of the file or directory to delete.", "required": True},
                        "recursive": {"type": "boolean", "description": "If True, allows recursive deletion of non-empty directories.", "required": False, "default": False}
                    },
                    "returns": "A confirmation message.",
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
