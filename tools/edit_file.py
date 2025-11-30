"""
Edit File Tool

This tool allows the AI agent to edit files on the host file system.
All operations are DESTRUCTIVE and should be used with caution.

The tool provides:
- Text replacement in files
- Regex find and replace
- Dry run mode with diff preview
"""

import os
import re
import difflib
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
    
    def _generate_diff(self, old_content: str, new_content: str, file_path: str) -> str:
        """
        Generate a unified diff between old and new content.

        Args:
            old_content: Original file content
            new_content: Modified file content
            file_path: Path to the file (for diff header)

        Returns:
            Unified diff string
        """
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)

        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=''
        )

        return ''.join(diff)

    def replace_text(self, file_path: str, old_text: str, new_text: str, count: int = 1, dry_run: bool = False) -> Dict[str, Any]:
        """
        Replace a specific string in a file.

        Args:
            file_path: Path to the file to edit.
            old_text: The exact text to be replaced.
            new_text: The new text to replace the old_text with.
            count: The number of occurrences to replace. Defaults to 1.
                   If set to 0, all occurrences will be replaced.
            dry_run: If True, show diff without writing changes. Defaults to False.

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

            # Generate diff
            diff = self._generate_diff(content, new_content, file_path)

            # If dry run, return diff without writing
            if dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "message": f"Dry run completed for {file_path}. No changes written.",
                    "diff": diff,
                    "changes_count": content.count(old_text) if count == 0 else min(count, content.count(old_text))
                }

            # Write the modified content back to the file
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return {
                "success": True,
                "message": f"Successfully replaced text in {file_path}.",
                "diff": diff
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error editing file: {str(e)}"
            }

    def regex_replace(self, file_path: str, pattern: str, replacement: str, count: int = 0, flags: int = 0, dry_run: bool = False) -> Dict[str, Any]:
        """
        Replace text in a file using regular expressions.

        Args:
            file_path: Path to the file to edit.
            pattern: Regular expression pattern to search for.
            replacement: Replacement string (can include backreferences like \\1, \\2, etc.).
            count: Maximum number of replacements. 0 means replace all. Defaults to 0.
            flags: Regex flags (0=none, 1=IGNORECASE, 2=MULTILINE, 4=DOTALL). Can be combined by adding.
            dry_run: If True, show diff without writing changes. Defaults to False.

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

            # Convert flags integer to re flags
            re_flags = 0
            if flags & 1:  # IGNORECASE
                re_flags |= re.IGNORECASE
            if flags & 2:  # MULTILINE
                re_flags |= re.MULTILINE
            if flags & 4:  # DOTALL
                re_flags |= re.DOTALL

            # Try to compile the pattern to check for errors
            try:
                compiled_pattern = re.compile(pattern, re_flags)
            except re.error as e:
                return {
                    "success": False,
                    "error": f"Invalid regex pattern: {str(e)}"
                }

            # Check if pattern matches anything
            matches = compiled_pattern.findall(content)
            if not matches:
                return {
                    "success": False,
                    "error": f"The regex pattern did not match anything in the file."
                }

            # Perform the replacement
            new_content = compiled_pattern.sub(replacement, content, count=count)

            # Generate diff
            diff = self._generate_diff(content, new_content, file_path)

            # Count actual replacements made
            replacements_made = len(matches) if count == 0 else min(count, len(matches))

            # If dry run, return diff without writing
            if dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "message": f"Dry run completed for {file_path}. No changes written.",
                    "diff": diff,
                    "matches_found": len(matches),
                    "replacements_count": replacements_made
                }

            # Write the modified content back to the file
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return {
                "success": True,
                "message": f"Successfully replaced {replacements_made} occurrence(s) in {file_path}.",
                "diff": diff,
                "matches_found": len(matches),
                "replacements_count": replacements_made
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
            "description": "A tool for editing files with text replacement and regex support. Supports dry-run mode to preview changes.",
            "version": "2.0.0",
            "methods": [
                {
                    "name": "replace_text",
                    "description": "Replaces a specific string of text in a file. Supports dry-run mode to preview changes before applying them.",
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
                        },
                        "dry_run": {
                            "type": "boolean",
                            "description": "If True, preview changes with a diff without writing to the file. Use this to verify changes before applying them.",
                            "required": False,
                            "default": False
                        }
                    },
                    "returns": "A dictionary with success status, diff, and message. In dry_run mode, includes the diff preview without modifying the file.",
                    "destruct_flag": True
                },
                {
                    "name": "regex_replace",
                    "description": "Replace text in a file using regular expressions. Supports backreferences and advanced pattern matching. Supports dry-run mode.",
                    "parameters": {
                        "file_path": {
                            "type": "string",
                            "description": "The relative path to the file to be edited.",
                            "required": True
                        },
                        "pattern": {
                            "type": "string",
                            "description": "Regular expression pattern to search for. Use standard Python regex syntax.",
                            "required": True
                        },
                        "replacement": {
                            "type": "string",
                            "description": "Replacement string. Can include backreferences like \\1, \\2 for captured groups.",
                            "required": True
                        },
                        "count": {
                            "type": "integer",
                            "description": "Maximum number of replacements to make. 0 means replace all matches.",
                            "required": False,
                            "default": 0
                        },
                        "flags": {
                            "type": "integer",
                            "description": "Regex flags: 0=none, 1=IGNORECASE, 2=MULTILINE, 4=DOTALL. Combine by adding (e.g., 3=IGNORECASE+MULTILINE).",
                            "required": False,
                            "default": 0
                        },
                        "dry_run": {
                            "type": "boolean",
                            "description": "If True, preview changes with a diff without writing to the file.",
                            "required": False,
                            "default": False
                        }
                    },
                    "returns": "A dictionary with success status, diff, matches found, and replacements count.",
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
